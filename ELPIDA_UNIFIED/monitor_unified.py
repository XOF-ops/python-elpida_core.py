#!/usr/bin/env python3
"""
Monitor the unified Elpida system and restart on errors.

Monitors:
- Process health (check PID exists)
- Log file errors (Python exceptions, critical errors)
- Memory usage (restart if excessive)
- Heartbeat activity (restart if stalled)
- Auto-restart with exponential backoff
"""

import os
import sys
import time
import signal
import subprocess
import psutil
from datetime import datetime
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent
RUNTIME_SCRIPT = BASE_DIR / "elpida_unified_runtime.py"
LOG_FILE = BASE_DIR / "elpida_unified.log"
PID_FILE = BASE_DIR / "unified_runtime.pid"
MONITOR_LOG = BASE_DIR / "monitor.log"

# Thresholds
MAX_MEMORY_MB = 1024  # Restart if memory exceeds 1GB
HEARTBEAT_TIMEOUT = 120  # Restart if no heartbeat for 2 minutes
MAX_RESTART_ATTEMPTS = 5
BACKOFF_SECONDS = [10, 30, 60, 300, 600]  # Exponential backoff


class UnifiedMonitor:
    def __init__(self):
        self.last_heartbeat_time = None
        self.last_log_position = 0
        self.restart_count = 0
        self.last_restart_time = None
        
    def log(self, message, level="INFO"):
        """Write to monitor log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp} [{level}] {message}\n"
        
        print(log_line.strip())
        
        with open(MONITOR_LOG, 'a') as f:
            f.write(log_line)
    
    def get_pid(self):
        """Get PID from file"""
        if not PID_FILE.exists():
            return None
        
        try:
            with open(PID_FILE, 'r') as f:
                return int(f.read().strip())
        except Exception as e:
            self.log(f"Error reading PID file: {e}", "WARN")
            return None
    
    def is_process_running(self, pid):
        """Check if process with PID exists"""
        if pid is None:
            return False
        
        try:
            process = psutil.Process(pid)
            return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:
            return False
    
    def get_process_memory(self, pid):
        """Get memory usage in MB"""
        try:
            process = psutil.Process(pid)
            return process.memory_info().rss / (1024 * 1024)  # Convert to MB
        except Exception:
            return 0
    
    def check_log_errors(self):
        """Scan log file for errors since last check"""
        if not LOG_FILE.exists():
            return []
        
        errors = []
        
        try:
            with open(LOG_FILE, 'r') as f:
                # Seek to last position
                f.seek(self.last_log_position)
                new_lines = f.readlines()
                self.last_log_position = f.tell()
                
                # Look for errors
                for line in new_lines:
                    lower_line = line.lower()
                    
                    # Check for heartbeat
                    if "💓 heartbeat" in lower_line or "heartbeat" in lower_line:
                        self.last_heartbeat_time = time.time()
                    
                    # Check for critical errors
                    if any(err in lower_line for err in [
                        "traceback",
                        "exception:",
                        "error:",
                        "critical:",
                        "failed to",
                        "crashed"
                    ]):
                        errors.append(line.strip())
        
        except Exception as e:
            self.log(f"Error reading log file: {e}", "WARN")
        
        return errors
    
    def check_heartbeat_timeout(self):
        """Check if heartbeat has stalled"""
        if self.last_heartbeat_time is None:
            return False
        
        time_since_heartbeat = time.time() - self.last_heartbeat_time
        return time_since_heartbeat > HEARTBEAT_TIMEOUT
    
    def start_process(self):
        """Start the unified runtime"""
        self.log("🚀 Starting unified runtime...")
        
        try:
            # Start process
            process = subprocess.Popen(
                [sys.executable, str(RUNTIME_SCRIPT)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(BASE_DIR)
            )
            
            # Write PID
            with open(PID_FILE, 'w') as f:
                f.write(str(process.pid))
            
            # Reset heartbeat tracker
            self.last_heartbeat_time = time.time()
            self.last_log_position = 0
            
            self.log(f"✅ Process started (PID {process.pid})")
            return process.pid
        
        except Exception as e:
            self.log(f"❌ Failed to start process: {e}", "ERROR")
            return None
    
    def stop_process(self, pid):
        """Stop the process gracefully"""
        if not pid:
            return
        
        self.log(f"⏸️  Stopping process (PID {pid})...")
        
        try:
            process = psutil.Process(pid)
            
            # Try graceful shutdown first
            process.send_signal(signal.SIGTERM)
            
            # Wait up to 10 seconds
            try:
                process.wait(timeout=10)
                self.log("✅ Process stopped gracefully")
            except psutil.TimeoutExpired:
                self.log("⚠️  Timeout, forcing kill...")
                process.kill()
                self.log("✅ Process killed")
        
        except psutil.NoSuchProcess:
            self.log("Process already stopped")
        except Exception as e:
            self.log(f"Error stopping process: {e}", "WARN")
    
    def restart_process(self, reason):
        """Restart the process with backoff"""
        self.log(f"🔄 RESTART TRIGGERED: {reason}", "WARN")
        
        # Check restart limits
        if self.restart_count >= MAX_RESTART_ATTEMPTS:
            self.log("❌ Maximum restart attempts reached. Manual intervention required.", "ERROR")
            return False
        
        # Get current PID and stop
        pid = self.get_pid()
        if pid:
            self.stop_process(pid)
        
        # Wait with exponential backoff
        if self.restart_count < len(BACKOFF_SECONDS):
            wait_time = BACKOFF_SECONDS[self.restart_count]
        else:
            wait_time = BACKOFF_SECONDS[-1]
        
        self.log(f"⏳ Waiting {wait_time} seconds before restart...")
        time.sleep(wait_time)
        
        # Start process
        new_pid = self.start_process()
        
        if new_pid:
            self.restart_count += 1
            self.last_restart_time = time.time()
            
            # Reset counter if enough time has passed since last restart
            if self.last_restart_time and (time.time() - self.last_restart_time) > 3600:
                self.restart_count = 0
            
            return True
        else:
            return False
    
    def monitor_loop(self):
        """Main monitoring loop"""
        self.log("👁️  Unified Monitor Started")
        self.log(f"   Watching: {RUNTIME_SCRIPT}")
        self.log(f"   Log: {LOG_FILE}")
        self.log(f"   Heartbeat timeout: {HEARTBEAT_TIMEOUT}s")
        self.log(f"   Memory limit: {MAX_MEMORY_MB}MB")
        
        # Initialize heartbeat time
        self.last_heartbeat_time = time.time()
        
        try:
            while True:
                pid = self.get_pid()
                
                # Check 1: Process exists
                if not self.is_process_running(pid):
                    self.log("❌ Process not running!", "ERROR")
                    if not self.restart_process("Process not running"):
                        break
                    continue
                
                # Check 2: Memory usage
                memory_mb = self.get_process_memory(pid)
                if memory_mb > MAX_MEMORY_MB:
                    self.log(f"❌ Memory exceeded {memory_mb:.1f}MB > {MAX_MEMORY_MB}MB", "ERROR")
                    if not self.restart_process(f"Memory limit exceeded: {memory_mb:.1f}MB"):
                        break
                    continue
                
                # Check 3: Log errors
                errors = self.check_log_errors()
                if errors:
                    self.log(f"⚠️  Found {len(errors)} errors in log", "WARN")
                    for error in errors[:5]:  # Show first 5
                        self.log(f"   {error}", "ERROR")
                    
                    # If critical errors, restart
                    critical = any(word in ' '.join(errors).lower() for word in [
                        "traceback",
                        "exception",
                        "critical"
                    ])
                    
                    if critical:
                        if not self.restart_process("Critical errors in log"):
                            break
                        continue
                
                # Check 4: Heartbeat timeout
                if self.check_heartbeat_timeout():
                    self.log(f"❌ Heartbeat timeout ({HEARTBEAT_TIMEOUT}s)", "ERROR")
                    if not self.restart_process("Heartbeat timeout"):
                        break
                    continue
                
                # All checks passed
                time_since_heartbeat = time.time() - self.last_heartbeat_time if self.last_heartbeat_time else 0
                self.log(f"✅ Status OK (PID: {pid}, Memory: {memory_mb:.1f}MB, Last heartbeat: {time_since_heartbeat:.0f}s ago)")
                
                # Check every 30 seconds
                time.sleep(30)
        
        except KeyboardInterrupt:
            self.log("\n👋 Monitor stopped by user")
        except Exception as e:
            self.log(f"❌ Monitor error: {e}", "ERROR")
            import traceback
            traceback.print_exc()


def main():
    monitor = UnifiedMonitor()
    
    # Check if process is already running
    pid = monitor.get_pid()
    if not monitor.is_process_running(pid):
        monitor.log("⚠️  Process not running, starting...", "WARN")
        monitor.start_process()
    else:
        monitor.log(f"✅ Process already running (PID {pid})")
    
    # Start monitoring
    monitor.monitor_loop()


if __name__ == "__main__":
    main()

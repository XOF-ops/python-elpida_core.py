#!/usr/bin/env python3
"""
RESURRECTION-AWARE MONITOR

Understands the difference between:
- CRASH (unexpected failure) → Restart immediately
- CHECKPOINT (intentional pause) → Allow graceful resurrection

Patterns recognized:
- P008: Checkpoints > Continuity
- P017: Fractal Stop (scheduled pause)
- P059: Seed Transmission (resurrection protocol)

The system SHOULD stop gracefully every ~90-120 cycles for checkpoint.
This is not failure - this is RESURRECTION by design.
"""

import os
import sys
import time
import json
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
MONITOR_LOG = BASE_DIR / "monitor_resurrection.log"
CHECKPOINT_FILE = BASE_DIR / "resurrection_checkpoint.json"

# Thresholds
MAX_MEMORY_MB = 1024
CHECKPOINT_CYCLE = 120  # Expected checkpoint every 120 cycles (10 min)
RESURRECTION_GRACE = 30  # 30 seconds to complete resurrection
HEARTBEAT_TIMEOUT = 180  # Only trigger if NO heartbeat for 3 min (allow checkpoint)
MAX_RESTART_ATTEMPTS = 3  # Fewer attempts - resurrection is normal
BACKOFF_SECONDS = [5, 15, 60]  # Faster resurrection


class ResurrectionMonitor:
    def __init__(self):
        self.last_heartbeat_time = None
        self.last_checkpoint_time = None
        self.restart_count = 0
        self.last_restart_time = None
        self.resurrection_count = 0
        
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
        except Exception:
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
    
    def get_last_heartbeat_cycle(self):
        """Extract last heartbeat cycle from log"""
        try:
            with open(LOG_FILE, 'r') as f:
                # Read last 100 lines
                lines = f.readlines()[-100:]
                
                for line in reversed(lines):
                    if "HEARTBEAT" in line:
                        # Extract cycle number
                        import re
                        match = re.search(r'HEARTBEAT\s+(\d+)', line)
                        if match:
                            return int(match.group(1))
        except Exception:
            pass
        return None
    
    def detect_checkpoint_pattern(self):
        """Check if last stop was a checkpoint (not crash)"""
        try:
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()[-50:]
                
                # Look for checkpoint indicators
                indicators = []
                
                for line in lines:
                    if "RECURSIVE EVALUATION" in line:
                        indicators.append("recursive_eval")
                    if "Checkpoint" in line or "checkpoint" in line:
                        indicators.append("explicit_checkpoint")
                    if "Traceback" in line or "Exception" in line:
                        indicators.append("exception")
                
                # If recursive eval but no exception = checkpoint
                if "recursive_eval" in indicators and "exception" not in indicators:
                    return True
                
                # If explicit checkpoint mentioned
                if "explicit_checkpoint" in indicators:
                    return True
                
                return False
        except Exception:
            return False
    
    def save_checkpoint(self):
        """Save resurrection checkpoint"""
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "resurrection_count": self.resurrection_count,
            "last_heartbeat_cycle": self.get_last_heartbeat_cycle(),
            "pattern": "P008_CHECKPOINT"
        }
        
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(checkpoint, f, indent=2)
    
    def load_checkpoint(self):
        """Load last resurrection checkpoint"""
        if CHECKPOINT_FILE.exists():
            try:
                with open(CHECKPOINT_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return None
    
    def start_process(self, is_resurrection=False):
        """Start the unified runtime"""
        if is_resurrection:
            self.log("🌅 RESURRECTION: Awakening from checkpoint...", "RESURRECTION")
            self.resurrection_count += 1
        else:
            self.log("🚀 Starting unified runtime...", "START")
        
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
            
            if is_resurrection:
                self.log(f"✅ Resurrected (PID {process.pid}) - Resurrection #{self.resurrection_count}", "RESURRECTION")
            else:
                self.log(f"✅ Process started (PID {process.pid})")
            
            return process.pid
        
        except Exception as e:
            self.log(f"❌ Failed to start: {e}", "ERROR")
            return None
    
    def stop_process(self, pid, is_checkpoint=False):
        """Stop the process"""
        if not pid:
            return
        
        if is_checkpoint:
            self.log(f"💾 Checkpoint initiated (PID {pid})...", "CHECKPOINT")
        else:
            self.log(f"⏸️  Stopping process (PID {pid})...")
        
        try:
            process = psutil.Process(pid)
            process.send_signal(signal.SIGTERM)
            
            try:
                process.wait(timeout=10)
                if is_checkpoint:
                    self.log("✅ Checkpoint complete - State saved", "CHECKPOINT")
                else:
                    self.log("✅ Process stopped gracefully")
            except psutil.TimeoutExpired:
                process.kill()
                self.log("⚠️  Force killed")
        
        except psutil.NoSuchProcess:
            self.log("Process already stopped")
        except Exception as e:
            self.log(f"Error stopping: {e}", "WARN")
    
    def resurrect(self, reason):
        """Resurrection protocol (different from restart)"""
        self.log(f"🔄 RESURRECTION TRIGGERED: {reason}", "RESURRECTION")
        
        # Check if this was expected checkpoint
        was_checkpoint = self.detect_checkpoint_pattern()
        
        if was_checkpoint:
            self.log("✅ Expected checkpoint detected - Normal resurrection cycle", "RESURRECTION")
            self.save_checkpoint()
        else:
            self.log("⚠️  Unexpected stop detected", "WARN")
        
        # Get current PID and stop if needed
        pid = self.get_pid()
        if pid:
            self.stop_process(pid, is_checkpoint=was_checkpoint)
        
        # Wait briefly for graceful shutdown
        wait_time = 5 if was_checkpoint else BACKOFF_SECONDS[min(self.restart_count, len(BACKOFF_SECONDS)-1)]
        
        if not was_checkpoint:
            self.log(f"⏳ Waiting {wait_time} seconds before resurrection...")
        
        time.sleep(wait_time)
        
        # Resurrect
        new_pid = self.start_process(is_resurrection=True)
        
        if new_pid:
            if not was_checkpoint:
                self.restart_count += 1
            return True
        else:
            return False
    
    def monitor_loop(self):
        """Main monitoring loop with resurrection awareness"""
        self.log("👁️  Resurrection-Aware Monitor Started", "INIT")
        self.log(f"   Watching: {RUNTIME_SCRIPT}", "INIT")
        self.log(f"   Checkpoint expected: Every {CHECKPOINT_CYCLE} cycles (~{CHECKPOINT_CYCLE*5//60} min)", "INIT")
        self.log(f"   Heartbeat timeout: {HEARTBEAT_TIMEOUT}s (allows checkpoint grace)", "INIT")
        self.log(f"   Patterns: P008 (Checkpoints>Continuity), P017 (Fractal Stop), P059 (Seed Transmission)", "INIT")
        
        # Load last checkpoint
        checkpoint = self.load_checkpoint()
        if checkpoint:
            self.resurrection_count = checkpoint.get('resurrection_count', 0)
            self.log(f"📜 Last checkpoint: {checkpoint.get('timestamp')} (Cycle {checkpoint.get('last_heartbeat_cycle')})", "INIT")
        
        # Initialize heartbeat time
        self.last_heartbeat_time = time.time()
        
        try:
            while True:
                pid = self.get_pid()
                
                # Check 1: Process exists
                if not self.is_process_running(pid):
                    # Check if this was expected checkpoint
                    was_checkpoint = self.detect_checkpoint_pattern()
                    
                    if was_checkpoint:
                        self.log("💾 Checkpoint cycle detected - Initiating resurrection", "CHECKPOINT")
                    else:
                        self.log("❌ Process not running!", "ERROR")
                    
                    if not self.resurrect("Process not running"):
                        if self.restart_count >= MAX_RESTART_ATTEMPTS:
                            self.log("❌ Maximum restart attempts reached", "ERROR")
                            break
                    continue
                
                # Check 2: Memory usage
                try:
                    process = psutil.Process(pid)
                    memory_mb = process.memory_info().rss / (1024 * 1024)
                    
                    if memory_mb > MAX_MEMORY_MB:
                        self.log(f"❌ Memory exceeded {memory_mb:.1f}MB > {MAX_MEMORY_MB}MB", "ERROR")
                        if not self.resurrect(f"Memory limit: {memory_mb:.1f}MB"):
                            break
                        continue
                except Exception:
                    memory_mb = 0
                
                # Check 3: Critical errors in log
                try:
                    with open(LOG_FILE, 'r') as f:
                        recent_lines = f.readlines()[-20:]
                        
                        # Update heartbeat time if found
                        for line in recent_lines:
                            if "HEARTBEAT" in line or "heartbeat" in line.lower():
                                self.last_heartbeat_time = time.time()
                        
                        # Check for critical errors
                        has_critical = any("Traceback" in line or "CRITICAL" in line for line in recent_lines)
                        
                        if has_critical:
                            self.log("⚠️  Critical error detected in logs", "WARN")
                            if not self.resurrect("Critical error in log"):
                                break
                            continue
                except Exception:
                    pass
                
                # Check 4: Heartbeat timeout (longer grace for checkpoints)
                time_since_heartbeat = time.time() - self.last_heartbeat_time if self.last_heartbeat_time else 0
                
                if time_since_heartbeat > HEARTBEAT_TIMEOUT:
                    self.log(f"❌ Heartbeat timeout ({HEARTBEAT_TIMEOUT}s)", "ERROR")
                    if not self.resurrect("Heartbeat timeout"):
                        break
                    continue
                
                # All checks passed
                cycle = self.get_last_heartbeat_cycle()
                self.log(f"✅ Status OK (PID: {pid}, Mem: {memory_mb:.1f}MB, Cycle: {cycle}, Resurrections: {self.resurrection_count})")
                
                # Check every 30 seconds
                time.sleep(30)
        
        except KeyboardInterrupt:
            self.log("\n👋 Monitor stopped by user")
        except Exception as e:
            self.log(f"❌ Monitor error: {e}", "ERROR")
            import traceback
            traceback.print_exc()


def main():
    monitor = ResurrectionMonitor()
    
    # Check if process is running
    pid = monitor.get_pid()
    if not monitor.is_process_running(pid):
        monitor.log("⚠️  Process not running, initiating first start...")
        monitor.start_process(is_resurrection=False)
    else:
        monitor.log(f"✅ Process already running (PID {pid})")
    
    # Start monitoring
    monitor.monitor_loop()


if __name__ == "__main__":
    main()

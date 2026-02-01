#!/usr/bin/env python3
"""
HYBRID RUNTIME MONITOR
======================

Monitor and report on hybrid runtime performance.
Analyzes logs, extracts metrics, and generates reports.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class HybridMonitor:
    """Monitor and analyze hybrid runtime performance."""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.log_path = self.base_path / "logs" / "hybrid_runtime.log"
        self.status_path = self.base_path / "reports" / "HYBRID_RUNTIME_STATUS.json"
        self.dilemma_log_path = self.base_path / "internal_dilemmas.jsonl"
    
    def analyze_logs(self) -> Dict[str, Any]:
        """Analyze runtime logs and extract metrics."""
        if not self.log_path.exists():
            return {"error": "No runtime logs found", "log_path": str(self.log_path)}
        
        with open(self.log_path) as f:
            lines = f.readlines()
        
        metrics = {
            "total_lines": len(lines),
            "internal_cycles": 0,
            "external_cycles": 0,
            "feedback_cycles": 0,
            "dilemmas_mentioned": 0,
            "syntheses_mentioned": 0,
            "patterns_mentioned": 0,
            "errors": 0,
            "warnings": 0,
            "first_entry": None,
            "last_entry": None,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for line in lines:
            # Track cycle types
            if "INTERNAL LOOP CYCLE" in line:
                metrics["internal_cycles"] += 1
            elif "EXTERNAL LOOP CYCLE" in line:
                metrics["external_cycles"] += 1
            elif "FEEDBACK LOOP CYCLE" in line:
                metrics["feedback_cycles"] += 1
            
            # Track content
            if "dilemma" in line.lower():
                metrics["dilemmas_mentioned"] += 1
            if "synthes" in line.lower():
                metrics["syntheses_mentioned"] += 1
            if "pattern" in line.lower():
                metrics["patterns_mentioned"] += 1
            
            # Track issues
            if "ERROR" in line:
                metrics["errors"] += 1
            if "WARNING" in line or "Warning" in line:
                metrics["warnings"] += 1
            
            # Track time range
            if "|" in line:
                try:
                    timestamp_str = line.split("|")[0].strip()
                    if metrics["first_entry"] is None:
                        metrics["first_entry"] = timestamp_str
                    metrics["last_entry"] = timestamp_str
                except:
                    pass
        
        return metrics
    
    def analyze_dilemmas(self) -> Dict[str, Any]:
        """Analyze generated dilemmas."""
        if not self.dilemma_log_path.exists():
            return {"error": "No dilemma log found", "path": str(self.dilemma_log_path)}
        
        dilemmas = []
        with open(self.dilemma_log_path) as f:
            for line in f:
                try:
                    dilemmas.append(json.loads(line.strip()))
                except:
                    pass
        
        if not dilemmas:
            return {"count": 0, "templates": {}}
        
        # Analyze templates
        template_counts = {}
        for d in dilemmas:
            template = d.get("template", "UNKNOWN")
            template_counts[template] = template_counts.get(template, 0) + 1
        
        return {
            "total_dilemmas": len(dilemmas),
            "templates_used": template_counts,
            "first_dilemma": dilemmas[0].get("timestamp") if dilemmas else None,
            "last_dilemma": dilemmas[-1].get("timestamp") if dilemmas else None
        }
    
    def get_current_status(self) -> Dict[str, Any]:
        """Load current status from file."""
        if not self.status_path.exists():
            return {"error": "No status file found", "path": str(self.status_path)}
        
        with open(self.status_path) as f:
            return json.load(f)
    
    def report(self, verbose: bool = True) -> Dict[str, Any]:
        """Generate a comprehensive report of hybrid runtime performance."""
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "log_analysis": self.analyze_logs(),
            "dilemma_analysis": self.analyze_dilemmas(),
            "current_status": self.get_current_status()
        }
        
        if verbose:
            self._print_report(report)
        
        # Save report
        report_path = self.base_path / "reports" / "HYBRID_MONITOR_REPORT.json"
        report_path.parent.mkdir(exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        if verbose:
            print(f"\nReport saved to: {report_path}")
        
        return report
    
    def _print_report(self, report: Dict[str, Any]):
        """Pretty-print the report."""
        print("\n" + "=" * 70)
        print("HYBRID RUNTIME PERFORMANCE REPORT")
        print(f"Generated: {report['timestamp']}")
        print("=" * 70)
        
        # Log analysis
        log = report.get("log_analysis", {})
        if "error" in log:
            print(f"\n⚠ Log Analysis: {log['error']}")
        else:
            print(f"\n📋 LOG ANALYSIS")
            print(f"  Total log lines: {log.get('total_lines', 0)}")
            print(f"  Time range: {log.get('first_entry', 'N/A')} → {log.get('last_entry', 'N/A')}")
            print(f"\n  Cycles:")
            print(f"    Internal: {log.get('internal_cycles', 0)}")
            print(f"    External: {log.get('external_cycles', 0)}")
            print(f"    Feedback: {log.get('feedback_cycles', 0)}")
            print(f"\n  Mentions:")
            print(f"    Dilemmas: {log.get('dilemmas_mentioned', 0)}")
            print(f"    Syntheses: {log.get('syntheses_mentioned', 0)}")
            print(f"    Patterns: {log.get('patterns_mentioned', 0)}")
            print(f"\n  Issues:")
            print(f"    Errors: {log.get('errors', 0)}")
            print(f"    Warnings: {log.get('warnings', 0)}")
        
        # Dilemma analysis
        dilemma = report.get("dilemma_analysis", {})
        if "error" in dilemma:
            print(f"\n⚠ Dilemma Analysis: {dilemma['error']}")
        else:
            print(f"\n🧠 DILEMMA ANALYSIS")
            print(f"  Total dilemmas: {dilemma.get('total_dilemmas', 0)}")
            print(f"  Time range: {dilemma.get('first_dilemma', 'N/A')} → {dilemma.get('last_dilemma', 'N/A')}")
            templates = dilemma.get("templates_used", {})
            if templates:
                print(f"\n  Templates used:")
                for template, count in sorted(templates.items(), key=lambda x: -x[1]):
                    print(f"    {template}: {count}")
        
        # Current status
        status = report.get("current_status", {})
        if "error" in status:
            print(f"\n⚠ Status: {status['error']}")
        else:
            print(f"\n📊 CURRENT STATUS")
            print(f"  Uptime: {status.get('uptime_seconds', 0)/60:.1f} minutes")
            print(f"  Total cycles: {status.get('cycle_count', 0)}")
            print(f"\n  Metrics:")
            print(f"    Dilemmas: {status.get('total_dilemmas', 0)}")
            print(f"    Syntheses: {status.get('total_syntheses', 0)}")
            print(f"    Patterns: {status.get('total_patterns', 0)}")
            print(f"    Votes: {status.get('total_votes', 0)}")
            
            # Dilemma engine stats if available
            de_stats = status.get("dilemma_engine_stats", {})
            if de_stats:
                print(f"\n  Dilemma Engine:")
                print(f"    Generated: {de_stats.get('total_generated', 0)}")
                print(f"    Axioms: {de_stats.get('axioms_known', 0)}")
                print(f"    Templates: {de_stats.get('templates_available', 0)}")
        
        print("\n" + "=" * 70)
    
    def tail_log(self, lines: int = 20):
        """Show the last N lines of the log."""
        if not self.log_path.exists():
            print(f"No log file found at {self.log_path}")
            return
        
        with open(self.log_path) as f:
            all_lines = f.readlines()
        
        print(f"\n📜 Last {lines} lines of hybrid_runtime.log:")
        print("-" * 70)
        for line in all_lines[-lines:]:
            print(line.rstrip())
        print("-" * 70)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor Hybrid Runtime")
    parser.add_argument("--tail", type=int, default=0,
                       help="Show last N lines of log")
    parser.add_argument("--quiet", action="store_true",
                       help="Don't print report, just save")
    args = parser.parse_args()
    
    monitor = HybridMonitor()
    
    if args.tail > 0:
        monitor.tail_log(args.tail)
    else:
        monitor.report(verbose=not args.quiet)


if __name__ == "__main__":
    main()

"""
Unrotting — Error recovery and system health monitoring
"""
import os
import sys
import json
import threading
import logging
import time
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("unrotting")


class HealthMonitor:
    """Monitor application health and recover from errors."""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.health_log = config_dir / "health.json"
        self._check_interval = 60  # seconds
        self._running = False
        self._thread = None
        
    def start_monitoring(self) -> None:
        """Start background health monitoring."""
        self._running = True
        self._thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self._thread.start()
        logger.info("Health monitor started")
        
    def stop_monitoring(self) -> None:
        """Stop health monitoring."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            
    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while self._running:
            try:
                self._check_health()
                time.sleep(self._check_interval)
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                time.sleep(self._check_interval)
                
    def _check_health(self) -> None:
        """Perform health checks."""
        health = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "status": "healthy"
        }
        
        # Check config directory
        if self.config_dir.exists():
            health["checks"]["config_dir"] = "ok"
        else:
            health["checks"]["config_dir"] = "missing"
            health["status"] = "warning"
            
        # Check hosts file (Windows only)
        if sys.platform == 'win32':
            hosts_file = Path(r"C:\Windows\System32\drivers\etc\hosts")
            if hosts_file.exists():
                health["checks"]["hosts_file"] = "ok"
            else:
                health["checks"]["hosts_file"] = "missing"
                health["status"] = "warning"
                
        # Save health report
        try:
            self.health_log.write_text(json.dumps(health, indent=2))
        except Exception as e:
            logger.warning(f"Failed to save health report: {e}")
            
    def get_health_report(self) -> dict:
        """Get current health report."""
        try:
            if self.health_log.exists():
                return json.loads(self.health_log.read_text())
        except Exception as e:
            logger.warning(f"Failed to read health report: {e}")
        return {"status": "unknown"}


# Global instance
health_monitor = None


def init_health_monitor(config_dir: Path) -> HealthMonitor:
    """Initialize health monitor."""
    global health_monitor
    health_monitor = HealthMonitor(config_dir)
    health_monitor.start_monitoring()
    return health_monitor


def get_health_report() -> dict:
    """Get current health report."""
    if health_monitor:
        return health_monitor.get_health_report()
    return {"status": "unknown"}

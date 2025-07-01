#!/usr/bin/env python3
"""
Safety and Monitoring System - 24/7 operation safety and error recovery
Comprehensive monitoring, alerting, and graceful degradation for production deployment
Part of the RC Sandbox modular architecture
"""

import asyncio
import json
import logging
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import websockets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/safety_monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class SystemStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OFFLINE = "offline"

@dataclass
class Alert:
    id: str
    timestamp: float
    level: AlertLevel
    component: str
    message: str
    details: Dict[str, Any]
    acknowledged: bool = False
    resolved: bool = False

@dataclass
class HealthCheck:
    component: str
    status: SystemStatus
    last_check: float
    response_time: float
    error_count: int
    details: Dict[str, Any]

@dataclass
class SystemMetrics:
    timestamp: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_latency: float
    active_connections: int
    error_rate: float
    uptime: float

class SafetyMonitoringSystem:
    """Comprehensive safety monitoring and alerting system"""
    
    def __init__(self, config_file: str = "config/safety_config.json"):
        self.config = self.load_config(config_file)
        
        # System state
        self.system_status = SystemStatus.HEALTHY
        self.alerts = []
        self.health_checks = {}
        self.metrics_history = []
        self.start_time = time.time()
        
        # Monitoring components
        self.monitored_services = {}
        self.sensor_connections = {}
        self.vehicle_connections = {}
        
        # Alert management
        self.alert_handlers = []
        self.notification_channels = []
        
        # Recovery mechanisms
        self.recovery_procedures = {}
        self.auto_recovery_enabled = True
        
        # Performance tracking
        self.performance_thresholds = self.config.get('thresholds', {})
        self.degradation_mode = False
        
        # Watchdog timers
        self.watchdog_timers = {}
        
        # Initialize monitoring
        self.setup_monitoring()
        
        logger.info("🛡️ Safety Monitoring System initialized")
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load safety monitoring configuration"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            logger.info(f"📋 Configuration loaded from {config_file}")
            return config
        except FileNotFoundError:
            logger.warning(f"⚠️ Config file {config_file} not found, using defaults")
            return self.get_default_config()
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Default safety monitoring configuration"""
        return {
            "thresholds": {
                "cpu_usage": 80.0,
                "memory_usage": 85.0,
                "disk_usage": 90.0,
                "network_latency": 100.0,
                "error_rate": 5.0,
                "response_time": 1000.0
            },
            "monitoring": {
                "interval": 5.0,
                "health_check_interval": 30.0,
                "metrics_retention_hours": 24,
                "alert_cooldown": 300
            },
            "recovery": {
                "auto_restart_services": True,
                "max_restart_attempts": 3,
                "restart_delay": 10.0,
                "graceful_degradation": True
            },
            "notifications": {
                "email_enabled": False,
                "webhook_enabled": False,
                "console_enabled": True
            },
            "services": {
                "depth_server": {"port": 8765, "critical": True},
                "telemetry_server": {"port": 8766, "critical": True},
                "streaming_server": {"port": 8767, "critical": False}
            }
        }
    
    def setup_monitoring(self):
        """Initialize monitoring components"""
        # Setup service monitoring
        self.setup_service_monitoring()
        
        # Setup sensor monitoring
        self.setup_sensor_monitoring()
        
        # Setup performance monitoring
        self.setup_performance_monitoring()
        
        # Setup alert handlers
        self.setup_alert_handlers()
        
        # Setup recovery procedures
        self.setup_recovery_procedures()
        
        # Start monitoring loops
        self.start_monitoring_loops()
    
    def setup_service_monitoring(self):
        """Setup monitoring for backend services"""
        services = self.config.get('services', {})
        
        for service_name, service_config in services.items():
            self.monitored_services[service_name] = {
                'config': service_config,
                'status': SystemStatus.OFFLINE,
                'last_check': 0,
                'error_count': 0,
                'restart_count': 0
            }
            
            # Initialize health check
            self.health_checks[service_name] = HealthCheck(
                component=service_name,
                status=SystemStatus.OFFLINE,
                last_check=0,
                response_time=0,
                error_count=0,
                details={}
            )
        
        logger.info(f"🔍 Service monitoring setup for {len(services)} services")
    
    def setup_sensor_monitoring(self):
        """Setup monitoring for hardware sensors"""
        self.sensor_connections = {
            'kinect': {
                'status': SystemStatus.OFFLINE,
                'last_data': 0,
                'error_count': 0,
                'auto_reconnect': True
            },
            'projector': {
                'status': SystemStatus.OFFLINE,
                'last_check': 0,
                'error_count': 0,
                'auto_reconnect': False
            }
        }
        
        logger.info("📡 Sensor monitoring initialized")
    
    def setup_performance_monitoring(self):
        """Setup system performance monitoring"""
        self.performance_monitors = {
            'cpu': self.monitor_cpu_usage,
            'memory': self.monitor_memory_usage,
            'disk': self.monitor_disk_usage,
            'network': self.monitor_network_latency
        }
        
        logger.info("📊 Performance monitoring initialized")
    
    def setup_alert_handlers(self):
        """Setup alert notification handlers"""
        if self.config.get('notifications', {}).get('email_enabled'):
            self.alert_handlers.append(self.send_email_alert)
        
        if self.config.get('notifications', {}).get('webhook_enabled'):
            self.alert_handlers.append(self.send_webhook_alert)
        
        if self.config.get('notifications', {}).get('console_enabled'):
            self.alert_handlers.append(self.send_console_alert)
        
        logger.info(f"📢 Alert handlers setup: {len(self.alert_handlers)} channels")
    
    def setup_recovery_procedures(self):
        """Setup automatic recovery procedures"""
        self.recovery_procedures = {
            'service_restart': self.restart_service,
            'sensor_reconnect': self.reconnect_sensor,
            'graceful_degradation': self.enable_degradation_mode,
            'emergency_shutdown': self.emergency_shutdown
        }
        
        logger.info("🔧 Recovery procedures initialized")
    
    def start_monitoring_loops(self):
        """Start all monitoring loops"""
        # System metrics monitoring
        threading.Thread(
            target=self.metrics_monitoring_loop,
            daemon=True
        ).start()
        
        # Service health monitoring
        threading.Thread(
            target=self.health_monitoring_loop,
            daemon=True
        ).start()
        
        # Sensor monitoring
        threading.Thread(
            target=self.sensor_monitoring_loop,
            daemon=True
        ).start()
        
        # Alert processing
        threading.Thread(
            target=self.alert_processing_loop,
            daemon=True
        ).start()
        
        logger.info("🔄 All monitoring loops started")
    
    def metrics_monitoring_loop(self):
        """Main metrics monitoring loop"""
        interval = self.config.get('monitoring', {}).get('interval', 5.0)
        
        while True:
            try:
                metrics = self.collect_system_metrics()
                self.process_metrics(metrics)
                self.check_performance_thresholds(metrics)
                
                # Store metrics
                self.metrics_history.append(metrics)
                
                # Cleanup old metrics
                self.cleanup_old_metrics()
                
            except Exception as e:
                logger.error(f"❌ Metrics monitoring error: {e}")
                self.create_alert(
                    AlertLevel.ERROR,
                    "monitoring",
                    f"Metrics collection failed: {e}",
                    {"exception": str(e)}
                )
            
            time.sleep(interval)
    
    def health_monitoring_loop(self):
        """Service health monitoring loop"""
        interval = self.config.get('monitoring', {}).get('health_check_interval', 30.0)
        
        while True:
            try:
                for service_name in self.monitored_services:
                    self.check_service_health(service_name)
                
                # Update overall system status
                self.update_system_status()
                
            except Exception as e:
                logger.error(f"❌ Health monitoring error: {e}")
            
            time.sleep(interval)
    
    def sensor_monitoring_loop(self):
        """Sensor connection monitoring loop"""
        while True:
            try:
                for sensor_name, sensor_info in self.sensor_connections.items():
                    self.check_sensor_connection(sensor_name)
                
            except Exception as e:
                logger.error(f"❌ Sensor monitoring error: {e}")
            
            time.sleep(10)  # Check sensors every 10 seconds
    
    def alert_processing_loop(self):
        """Alert processing and notification loop"""
        while True:
            try:
                # Process pending alerts
                unprocessed_alerts = [a for a in self.alerts if not a.acknowledged]
                
                for alert in unprocessed_alerts:
                    self.process_alert(alert)
                
                # Cleanup old alerts
                self.cleanup_old_alerts()
                
            except Exception as e:
                logger.error(f"❌ Alert processing error: {e}")
            
            time.sleep(5)
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        return SystemMetrics(
            timestamp=time.time(),
            cpu_usage=psutil.cpu_percent(interval=1),
            memory_usage=psutil.virtual_memory().percent,
            disk_usage=psutil.disk_usage('/').percent,
            network_latency=self.measure_network_latency(),
            active_connections=len(psutil.net_connections()),
            error_rate=self.calculate_error_rate(),
            uptime=time.time() - self.start_time
        )
    
    def measure_network_latency(self) -> float:
        """Measure network latency to localhost"""
        try:
            import subprocess
            result = subprocess.run(
                ['ping', '-c', '1', 'localhost'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse ping output for latency
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'time=' in line:
                        time_str = line.split('time=')[1].split(' ')[0]
                        return float(time_str)
            
            return 0.0
            
        except Exception:
            return 999.0  # High latency indicates network issues
    
    def calculate_error_rate(self) -> float:
        """Calculate current error rate"""
        if not self.metrics_history:
            return 0.0
        
        # Count errors in last 5 minutes
        recent_time = time.time() - 300
        recent_alerts = [
            a for a in self.alerts 
            if a.timestamp > recent_time and a.level in [AlertLevel.ERROR, AlertLevel.CRITICAL]
        ]
        
        return len(recent_alerts) / 5.0  # Errors per minute
    
    def process_metrics(self, metrics: SystemMetrics):
        """Process collected metrics"""
        # Log metrics periodically
        if len(self.metrics_history) % 12 == 0:  # Every minute at 5-second intervals
            logger.info(
                f"📊 System Metrics - "
                f"CPU: {metrics.cpu_usage:.1f}% | "
                f"RAM: {metrics.memory_usage:.1f}% | "
                f"Disk: {metrics.disk_usage:.1f}% | "
                f"Latency: {metrics.network_latency:.1f}ms"
            )
    
    def check_performance_thresholds(self, metrics: SystemMetrics):
        """Check if metrics exceed performance thresholds"""
        thresholds = self.performance_thresholds
        
        # CPU usage check
        if metrics.cpu_usage > thresholds.get('cpu_usage', 80):
            self.create_alert(
                AlertLevel.WARNING,
                "performance",
                f"High CPU usage: {metrics.cpu_usage:.1f}%",
                {"cpu_usage": metrics.cpu_usage, "threshold": thresholds.get('cpu_usage')}
            )
        
        # Memory usage check
        if metrics.memory_usage > thresholds.get('memory_usage', 85):
            self.create_alert(
                AlertLevel.WARNING,
                "performance",
                f"High memory usage: {metrics.memory_usage:.1f}%",
                {"memory_usage": metrics.memory_usage, "threshold": thresholds.get('memory_usage')}
            )
        
        # Disk usage check
        if metrics.disk_usage > thresholds.get('disk_usage', 90):
            self.create_alert(
                AlertLevel.ERROR,
                "performance",
                f"High disk usage: {metrics.disk_usage:.1f}%",
                {"disk_usage": metrics.disk_usage, "threshold": thresholds.get('disk_usage')}
            )
        
        # Network latency check
        if metrics.network_latency > thresholds.get('network_latency', 100):
            self.create_alert(
                AlertLevel.WARNING,
                "network",
                f"High network latency: {metrics.network_latency:.1f}ms",
                {"latency": metrics.network_latency, "threshold": thresholds.get('network_latency')}
            )
    
    async def check_service_health(self, service_name: str):
        """Check health of a specific service"""
        service_info = self.monitored_services.get(service_name)
        if not service_info:
            return
        
        service_config = service_info['config']
        port = service_config.get('port')
        
        start_time = time.time()
        
        try:
            # Try to connect to service WebSocket
            uri = f"ws://localhost:{port}"
            
            async with websockets.connect(uri, timeout=5) as websocket:
                # Send ping message
                await websocket.send(json.dumps({"type": "ping"}))
                response = await websocket.recv()
                
                # Service is healthy
                response_time = (time.time() - start_time) * 1000
                
                service_info['status'] = SystemStatus.HEALTHY
                service_info['last_check'] = time.time()
                service_info['error_count'] = 0
                
                # Update health check
                self.health_checks[service_name] = HealthCheck(
                    component=service_name,
                    status=SystemStatus.HEALTHY,
                    last_check=time.time(),
                    response_time=response_time,
                    error_count=0,
                    details={"port": port, "response": response}
                )
                
        except Exception as e:
            # Service is unhealthy
            service_info['status'] = SystemStatus.OFFLINE
            service_info['error_count'] += 1
            
            self.health_checks[service_name] = HealthCheck(
                component=service_name,
                status=SystemStatus.OFFLINE,
                last_check=time.time(),
                response_time=0,
                error_count=service_info['error_count'],
                details={"error": str(e), "port": port}
            )
            
            # Create alert for critical services
            if service_config.get('critical', False):
                self.create_alert(
                    AlertLevel.CRITICAL,
                    service_name,
                    f"Critical service {service_name} is offline",
                    {"error": str(e), "port": port, "error_count": service_info['error_count']}
                )
                
                # Attempt auto-recovery
                if self.auto_recovery_enabled:
                    await self.attempt_service_recovery(service_name)
    
    def check_sensor_connection(self, sensor_name: str):
        """Check sensor connection status"""
        sensor_info = self.sensor_connections.get(sensor_name)
        if not sensor_info:
            return
        
        # Simulate sensor health check
        # In real implementation, this would check actual sensor status
        current_time = time.time()
        
        # Check if sensor data is recent
        if sensor_name == 'kinect':
            # Check if depth data is being received
            if current_time - sensor_info.get('last_data', 0) > 30:
                sensor_info['status'] = SystemStatus.OFFLINE
                sensor_info['error_count'] += 1
                
                self.create_alert(
                    AlertLevel.ERROR,
                    sensor_name,
                    f"Sensor {sensor_name} not responding",
                    {"last_data": sensor_info.get('last_data', 0)}
                )
                
                # Attempt reconnection
                if sensor_info.get('auto_reconnect') and self.auto_recovery_enabled:
                    self.attempt_sensor_reconnection(sensor_name)
            else:
                sensor_info['status'] = SystemStatus.HEALTHY
                sensor_info['error_count'] = 0

    async def attempt_service_recovery(self, service_name: str):
        """Attempt to recover a failed service"""
        service_info = self.monitored_services.get(service_name)
        if not service_info:
            return

        max_attempts = self.config.get('recovery', {}).get('max_restart_attempts', 3)

        if service_info['restart_count'] >= max_attempts:
            logger.error(f"❌ Service {service_name} exceeded max restart attempts")
            self.create_alert(
                AlertLevel.CRITICAL,
                service_name,
                f"Service {service_name} failed to recover after {max_attempts} attempts",
                {"restart_count": service_info['restart_count']}
            )
            return

        try:
            logger.info(f"🔧 Attempting to restart service: {service_name}")

            # Increment restart count
            service_info['restart_count'] += 1

            # Execute recovery procedure
            success = await self.restart_service(service_name)

            if success:
                logger.info(f"✅ Service {service_name} restarted successfully")
                self.create_alert(
                    AlertLevel.INFO,
                    service_name,
                    f"Service {service_name} recovered successfully",
                    {"restart_count": service_info['restart_count']}
                )
            else:
                logger.error(f"❌ Failed to restart service: {service_name}")

        except Exception as e:
            logger.error(f"❌ Service recovery failed for {service_name}: {e}")

    async def restart_service(self, service_name: str) -> bool:
        """Restart a specific service"""
        try:
            import subprocess

            # Service restart commands
            restart_commands = {
                'depth_server': ['python', 'backend/depth_server.py'],
                'telemetry_server': ['python', 'backend/telemetry_server.py'],
                'streaming_server': ['python', 'backend/streaming_server.py']
            }

            command = restart_commands.get(service_name)
            if not command:
                logger.error(f"❌ No restart command for service: {service_name}")
                return False

            # Start the service
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Wait a moment for service to start
            await asyncio.sleep(5)

            # Check if service is running
            if process.poll() is None:
                logger.info(f"✅ Service {service_name} started with PID: {process.pid}")
                return True
            else:
                logger.error(f"❌ Service {service_name} failed to start")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to restart {service_name}: {e}")
            return False

    def attempt_sensor_reconnection(self, sensor_name: str):
        """Attempt to reconnect a sensor"""
        try:
            logger.info(f"🔌 Attempting to reconnect sensor: {sensor_name}")

            # Sensor-specific reconnection logic
            if sensor_name == 'kinect':
                # Reinitialize Kinect connection
                success = self.reconnect_kinect()
            elif sensor_name == 'projector':
                # Check projector connection
                success = self.reconnect_projector()
            else:
                success = False

            if success:
                logger.info(f"✅ Sensor {sensor_name} reconnected successfully")
                self.sensor_connections[sensor_name]['status'] = SystemStatus.HEALTHY
                self.sensor_connections[sensor_name]['error_count'] = 0
            else:
                logger.error(f"❌ Failed to reconnect sensor: {sensor_name}")

        except Exception as e:
            logger.error(f"❌ Sensor reconnection failed for {sensor_name}: {e}")

    def reconnect_kinect(self) -> bool:
        """Attempt to reconnect Kinect sensor"""
        try:
            # Simulate Kinect reconnection
            # In real implementation, this would reinitialize the Kinect SDK
            logger.info("🔌 Reinitializing Kinect connection...")
            time.sleep(2)  # Simulate initialization time

            # Update last data timestamp to indicate successful reconnection
            self.sensor_connections['kinect']['last_data'] = time.time()

            return True

        except Exception as e:
            logger.error(f"❌ Kinect reconnection failed: {e}")
            return False

    def reconnect_projector(self) -> bool:
        """Attempt to reconnect projector"""
        try:
            # Simulate projector connection check
            logger.info("📽️ Checking projector connection...")
            time.sleep(1)

            # In real implementation, this would check projector status
            return True

        except Exception as e:
            logger.error(f"❌ Projector reconnection failed: {e}")
            return False

    def create_alert(self, level: AlertLevel, component: str, message: str, details: Dict[str, Any]):
        """Create a new alert"""
        alert_id = f"{component}_{int(time.time())}"

        alert = Alert(
            id=alert_id,
            timestamp=time.time(),
            level=level,
            component=component,
            message=message,
            details=details
        )

        # Check for alert cooldown to prevent spam
        cooldown = self.config.get('monitoring', {}).get('alert_cooldown', 300)
        recent_alerts = [
            a for a in self.alerts
            if a.component == component and
               a.message == message and
               time.time() - a.timestamp < cooldown
        ]

        if not recent_alerts:
            self.alerts.append(alert)
            logger.warning(f"🚨 Alert created: [{level.value.upper()}] {component}: {message}")

    def process_alert(self, alert: Alert):
        """Process and handle an alert"""
        try:
            # Send notifications
            for handler in self.alert_handlers:
                handler(alert)

            # Mark as acknowledged
            alert.acknowledged = True

            # Trigger automatic responses for critical alerts
            if alert.level == AlertLevel.CRITICAL:
                self.handle_critical_alert(alert)

        except Exception as e:
            logger.error(f"❌ Failed to process alert {alert.id}: {e}")

    def handle_critical_alert(self, alert: Alert):
        """Handle critical alerts with automatic responses"""
        if alert.component in self.monitored_services:
            service_config = self.monitored_services[alert.component]['config']

            if service_config.get('critical', False):
                # Enable degradation mode for critical service failures
                if self.config.get('recovery', {}).get('graceful_degradation', True):
                    self.enable_degradation_mode()

    def enable_degradation_mode(self):
        """Enable graceful degradation mode"""
        if not self.degradation_mode:
            self.degradation_mode = True
            logger.warning("⚠️ Entering degradation mode")

            self.create_alert(
                AlertLevel.WARNING,
                "system",
                "System entering degradation mode",
                {"reason": "critical_service_failure"}
            )

            # Reduce system load
            self.reduce_system_load()

    def reduce_system_load(self):
        """Reduce system load during degradation mode"""
        # Reduce monitoring frequency
        self.config['monitoring']['interval'] = 10.0

        # Disable non-critical features
        logger.info("🔧 Reducing system load for degradation mode")

    def emergency_shutdown(self):
        """Perform emergency shutdown"""
        logger.critical("🚨 EMERGENCY SHUTDOWN INITIATED")

        self.create_alert(
            AlertLevel.CRITICAL,
            "system",
            "Emergency shutdown initiated",
            {"reason": "critical_system_failure"}
        )

        # Stop all services gracefully
        # In real implementation, this would stop all processes

    def send_email_alert(self, alert: Alert):
        """Send alert via email"""
        try:
            email_config = self.config.get('email', {})

            if not email_config.get('enabled', False):
                return

            msg = MIMEMultipart()
            msg['From'] = email_config.get('from_address')
            msg['To'] = email_config.get('to_address')
            msg['Subject'] = f"RC Sandbox Alert: {alert.level.value.upper()} - {alert.component}"

            body = f"""
            Alert Details:

            Level: {alert.level.value.upper()}
            Component: {alert.component}
            Message: {alert.message}
            Timestamp: {datetime.fromtimestamp(alert.timestamp)}

            Details: {json.dumps(alert.details, indent=2)}
            """

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(email_config.get('smtp_server'), email_config.get('smtp_port'))
            server.starttls()
            server.login(email_config.get('username'), email_config.get('password'))
            server.send_message(msg)
            server.quit()

            logger.info(f"📧 Email alert sent for {alert.id}")

        except Exception as e:
            logger.error(f"❌ Failed to send email alert: {e}")

    def send_webhook_alert(self, alert: Alert):
        """Send alert via webhook"""
        try:
            import requests

            webhook_config = self.config.get('webhook', {})

            if not webhook_config.get('enabled', False):
                return

            payload = {
                'alert_id': alert.id,
                'timestamp': alert.timestamp,
                'level': alert.level.value,
                'component': alert.component,
                'message': alert.message,
                'details': alert.details
            }

            response = requests.post(
                webhook_config.get('url'),
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"🌐 Webhook alert sent for {alert.id}")
            else:
                logger.error(f"❌ Webhook alert failed: {response.status_code}")

        except Exception as e:
            logger.error(f"❌ Failed to send webhook alert: {e}")

    def send_console_alert(self, alert: Alert):
        """Send alert to console"""
        timestamp = datetime.fromtimestamp(alert.timestamp).strftime('%Y-%m-%d %H:%M:%S')

        level_colors = {
            AlertLevel.INFO: '\033[94m',      # Blue
            AlertLevel.WARNING: '\033[93m',   # Yellow
            AlertLevel.ERROR: '\033[91m',     # Red
            AlertLevel.CRITICAL: '\033[95m'   # Magenta
        }

        color = level_colors.get(alert.level, '\033[0m')
        reset = '\033[0m'

        print(f"{color}🚨 [{timestamp}] {alert.level.value.upper()} - {alert.component}: {alert.message}{reset}")

    def update_system_status(self):
        """Update overall system status based on component health"""
        critical_services_down = 0
        total_services = len(self.monitored_services)

        for service_name, service_info in self.monitored_services.items():
            service_config = service_info['config']

            if service_config.get('critical', False) and service_info['status'] == SystemStatus.OFFLINE:
                critical_services_down += 1

        # Determine system status
        if critical_services_down > 0:
            self.system_status = SystemStatus.CRITICAL
        elif any(s['status'] == SystemStatus.OFFLINE for s in self.monitored_services.values()):
            self.system_status = SystemStatus.DEGRADED
        else:
            self.system_status = SystemStatus.HEALTHY

    def cleanup_old_metrics(self):
        """Remove old metrics to prevent memory buildup"""
        retention_hours = self.config.get('monitoring', {}).get('metrics_retention_hours', 24)
        cutoff_time = time.time() - (retention_hours * 3600)

        self.metrics_history = [
            m for m in self.metrics_history
            if m.timestamp > cutoff_time
        ]

    def cleanup_old_alerts(self):
        """Remove old resolved alerts"""
        # Keep alerts for 7 days
        cutoff_time = time.time() - (7 * 24 * 3600)

        self.alerts = [
            a for a in self.alerts
            if a.timestamp > cutoff_time or not a.resolved
        ]

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            'system_status': self.system_status.value,
            'uptime': time.time() - self.start_time,
            'degradation_mode': self.degradation_mode,
            'services': {
                name: {
                    'status': info['status'].value,
                    'error_count': info['error_count'],
                    'restart_count': info['restart_count']
                }
                for name, info in self.monitored_services.items()
            },
            'sensors': {
                name: {
                    'status': info['status'].value,
                    'error_count': info['error_count']
                }
                for name, info in self.sensor_connections.items()
            },
            'alerts': {
                'total': len(self.alerts),
                'unresolved': len([a for a in self.alerts if not a.resolved]),
                'critical': len([a for a in self.alerts if a.level == AlertLevel.CRITICAL and not a.resolved])
            },
            'latest_metrics': asdict(self.metrics_history[-1]) if self.metrics_history else None
        }

    def get_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        return {
            'timestamp': time.time(),
            'system_status': self.get_system_status(),
            'health_checks': {
                name: asdict(check)
                for name, check in self.health_checks.items()
            },
            'recent_alerts': [
                asdict(alert) for alert in self.alerts[-10:]
            ],
            'performance_summary': self.get_performance_summary()
        }

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary from recent metrics"""
        if not self.metrics_history:
            return {}

        recent_metrics = self.metrics_history[-60:]  # Last 5 minutes at 5-second intervals

        return {
            'avg_cpu_usage': sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics),
            'avg_memory_usage': sum(m.memory_usage for m in recent_metrics) / len(recent_metrics),
            'avg_network_latency': sum(m.network_latency for m in recent_metrics) / len(recent_metrics),
            'current_error_rate': recent_metrics[-1].error_rate if recent_metrics else 0
        }

# Monitor CPU usage
def monitor_cpu_usage(self) -> float:
    return psutil.cpu_percent(interval=1)

# Monitor memory usage
def monitor_memory_usage(self) -> float:
    return psutil.virtual_memory().percent

# Monitor disk usage
def monitor_disk_usage(self) -> float:
    return psutil.disk_usage('/').percent

# Monitor network latency
def monitor_network_latency(self) -> float:
    return self.measure_network_latency()

async def main():
    """Main entry point for safety monitoring system"""
    safety_monitor = SafetyMonitoringSystem()

    try:
        # Keep the monitoring system running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("🛑 Safety monitoring system shutting down")
    except Exception as e:
        logger.error(f"❌ Safety monitoring system error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

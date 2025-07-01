#!/usr/bin/env python3
"""
Performance Monitor - Real-time System Performance Tracking
Monitors system performance and suggests optimizations
"""

import psutil
import time
import json
from datetime import datetime
import threading

class PerformanceMonitor:
    def __init__(self):
        self.monitoring = True
        self.metrics = []
        self.alerts = []
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[PERF {timestamp}] {message}")
        
    def collect_system_metrics(self):
        """Collect current system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('.')
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_free_gb': round(disk.free / (1024**3), 2),
                'disk_percent': round((disk.used / disk.total) * 100, 1)
            }
            
            return metrics
        except Exception as e:
            self.log(f"Error collecting metrics: {e}")
            return None
    
    def analyze_performance_trends(self):
        """Analyze performance trends and generate alerts"""
        if len(self.metrics) < 5:
            return
        
        recent_metrics = self.metrics[-5:]
        
        # Check for high CPU usage
        avg_cpu = sum(m['cpu_percent'] for m in recent_metrics) / len(recent_metrics)
        if avg_cpu > 80:
            self.alerts.append({
                'type': 'high_cpu',
                'severity': 'warning',
                'message': f'High CPU usage detected: {avg_cpu:.1f}% average',
                'timestamp': datetime.now().isoformat()
            })
        
        # Check for high memory usage
        avg_memory = sum(m['memory_percent'] for m in recent_metrics) / len(recent_metrics)
        if avg_memory > 85:
            self.alerts.append({
                'type': 'high_memory',
                'severity': 'warning',
                'message': f'High memory usage detected: {avg_memory:.1f}% average',
                'timestamp': datetime.now().isoformat()
            })
        
        # Check for low disk space
        latest_disk = recent_metrics[-1]['disk_percent']
        if latest_disk > 90:
            self.alerts.append({
                'type': 'low_disk_space',
                'severity': 'critical',
                'message': f'Low disk space: {latest_disk:.1f}% used',
                'timestamp': datetime.now().isoformat()
            })
    
    def monitor_performance(self, duration_minutes=5):
        """Monitor performance for specified duration"""
        self.log(f"Starting performance monitoring for {duration_minutes} minutes...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time and self.monitoring:
            metrics = self.collect_system_metrics()
            if metrics:
                self.metrics.append(metrics)
                
                # Log current status
                self.log(f"CPU: {metrics['cpu_percent']:.1f}% | "
                        f"Memory: {metrics['memory_percent']:.1f}% | "
                        f"Disk: {metrics['disk_percent']:.1f}%")
                
                # Analyze trends
                self.analyze_performance_trends()
                
                # Report alerts
                if self.alerts:
                    latest_alert = self.alerts[-1]
                    if latest_alert['timestamp'] == metrics['timestamp']:
                        self.log(f"ALERT: {latest_alert['message']}")
            
            time.sleep(10)  # Monitor every 10 seconds
        
        self.log("Performance monitoring completed")
        return self.generate_performance_report()
    
    def generate_performance_report(self):
        """Generate performance monitoring report"""
        if not self.metrics:
            return None
        
        # Calculate statistics
        cpu_values = [m['cpu_percent'] for m in self.metrics]
        memory_values = [m['memory_percent'] for m in self.metrics]
        
        report = {
            'monitoring_period': {
                'start': self.metrics[0]['timestamp'],
                'end': self.metrics[-1]['timestamp'],
                'duration_minutes': round((len(self.metrics) * 10) / 60, 1),
                'samples': len(self.metrics)
            },
            'cpu_statistics': {
                'average': round(sum(cpu_values) / len(cpu_values), 1),
                'maximum': max(cpu_values),
                'minimum': min(cpu_values)
            },
            'memory_statistics': {
                'average': round(sum(memory_values) / len(memory_values), 1),
                'maximum': max(memory_values),
                'minimum': min(memory_values)
            },
            'alerts_generated': len(self.alerts),
            'alerts': self.alerts[-10:],  # Last 10 alerts
            'recommendations': self.generate_recommendations()
        }
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"performance_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"Performance report saved: {report_file}")
        return report
    
    def generate_recommendations(self):
        """Generate performance optimization recommendations"""
        recommendations = []
        
        if not self.metrics:
            return recommendations
        
        # Analyze CPU usage
        cpu_values = [m['cpu_percent'] for m in self.metrics]
        avg_cpu = sum(cpu_values) / len(cpu_values)
        
        if avg_cpu > 70:
            recommendations.append({
                'category': 'cpu_optimization',
                'priority': 'high',
                'description': f'High CPU usage detected ({avg_cpu:.1f}% average)',
                'suggestions': [
                    'Consider optimizing CPU-intensive operations',
                    'Review background processes',
                    'Implement caching to reduce computation'
                ]
            })
        
        # Analyze memory usage
        memory_values = [m['memory_percent'] for m in self.metrics]
        avg_memory = sum(memory_values) / len(memory_values)
        
        if avg_memory > 80:
            recommendations.append({
                'category': 'memory_optimization',
                'priority': 'high',
                'description': f'High memory usage detected ({avg_memory:.1f}% average)',
                'suggestions': [
                    'Review memory-intensive operations',
                    'Implement garbage collection optimization',
                    'Consider increasing available RAM'
                ]
            })
        
        # Analyze disk usage
        if self.metrics:
            latest_disk = self.metrics[-1]['disk_percent']
            if latest_disk > 85:
                recommendations.append({
                    'category': 'disk_optimization',
                    'priority': 'medium',
                    'description': f'High disk usage detected ({latest_disk:.1f}% used)',
                    'suggestions': [
                        'Clean up temporary files',
                        'Archive old log files',
                        'Consider disk space expansion'
                    ]
                })
        
        return recommendations

def main():
    print("PERFORMANCE MONITOR - REAL-TIME SYSTEM TRACKING")
    print("=" * 60)
    print("Monitoring system performance and generating optimization suggestions...")
    print("=" * 60)
    
    monitor = PerformanceMonitor()
    
    try:
        # Monitor for 5 minutes
        report = monitor.monitor_performance(duration_minutes=5)
        
        if report:
            print(f"\nPERFORMANCE MONITORING COMPLETE!")
            print(f"Duration: {report['monitoring_period']['duration_minutes']} minutes")
            print(f"Samples: {report['monitoring_period']['samples']}")
            print(f"Average CPU: {report['cpu_statistics']['average']}%")
            print(f"Average Memory: {report['memory_statistics']['average']}%")
            print(f"Alerts Generated: {report['alerts_generated']}")
            print(f"Recommendations: {len(report['recommendations'])}")
            
            if report['recommendations']:
                print("\nTOP RECOMMENDATIONS:")
                for rec in report['recommendations'][:3]:
                    print(f"- {rec['description']}")
        else:
            print("Performance monitoring failed to generate report")
            
    except KeyboardInterrupt:
        print("\nPerformance monitoring stopped by user")
        monitor.monitoring = False
    except Exception as e:
        print(f"\nPerformance monitoring failed: {e}")

if __name__ == "__main__":
    main()

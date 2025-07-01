#!/usr/bin/env python3
"""
VIP Analytics Dashboard Launcher
Integrates with existing AR Sandbox RC system for comprehensive analytics
"""

import subprocess
import time
import webbrowser
import threading
import logging
import sys
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VIPAnalyticsLauncher:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.processes = []
        self.analytics_port = 8768
        
    def launch_analytics_suite(self):
        """Launch the complete VIP Analytics suite"""
        logger.info("🚀 Launching VIP Analytics Dashboard Suite")
        
        try:
            # 1. Start the analytics backend
            self.start_analytics_backend()
            
            # 2. Start supporting services if needed
            self.start_supporting_services()
            
            # 3. Open the analytics dashboard
            self.open_analytics_dashboard()
            
            # 4. Generate initial analytics report
            self.generate_initial_report()
            
            logger.info("✅ VIP Analytics Dashboard Suite launched successfully")
            logger.info(f"📊 Dashboard available at: http://localhost:8080/frontend/vip_analytics_dashboard.html")
            logger.info(f"🔌 WebSocket API at: ws://localhost:{self.analytics_port}")
            
            # Keep the launcher running
            self.monitor_services()
            
        except Exception as e:
            logger.error(f"❌ Failed to launch VIP Analytics Suite: {e}")
            self.cleanup()
    
    def start_analytics_backend(self):
        """Start the VIP Analytics Dashboard backend"""
        logger.info("📊 Starting VIP Analytics Dashboard backend...")
        
        try:
            # Start the analytics dashboard server
            analytics_process = subprocess.Popen([
                sys.executable, 'vip_analytics_dashboard.py'
            ], cwd=self.base_dir)
            
            self.processes.append(('VIP Analytics Dashboard', analytics_process))
            
            # Wait for server to start
            time.sleep(3)
            logger.info("✅ VIP Analytics Dashboard backend started")
            
        except Exception as e:
            logger.error(f"❌ Failed to start analytics backend: {e}")
            raise
    
    def start_supporting_services(self):
        """Start supporting services for comprehensive analytics"""
        logger.info("🔧 Starting supporting services...")
        
        # Check if professional demo suite is available
        demo_suite_path = self.base_dir / 'professional_demo_suite.py'
        if demo_suite_path.exists():
            try:
                logger.info("🎯 Professional demo suite available for data generation")
                # Don't auto-start demo suite, just note availability
            except Exception as e:
                logger.warning(f"⚠️ Demo suite not available: {e}")
        
        # Check if telemetry server is available
        telemetry_path = self.base_dir / 'backend' / 'telemetry_server.py'
        if telemetry_path.exists():
            try:
                logger.info("📡 Starting telemetry server for real-time data...")
                telemetry_process = subprocess.Popen([
                    sys.executable, str(telemetry_path)
                ], cwd=self.base_dir)
                
                self.processes.append(('Telemetry Server', telemetry_process))
                time.sleep(2)
                logger.info("✅ Telemetry server started")
                
            except Exception as e:
                logger.warning(f"⚠️ Telemetry server not available: {e}")
    
    def open_analytics_dashboard(self):
        """Open the analytics dashboard in the browser"""
        logger.info("🌐 Opening VIP Analytics Dashboard...")
        
        # Start a simple HTTP server for the frontend
        try:
            http_server = subprocess.Popen([
                sys.executable, '-m', 'http.server', '8080'
            ], cwd=self.base_dir)
            
            self.processes.append(('HTTP Server', http_server))
            time.sleep(2)
            
            # Open the dashboard in the browser
            dashboard_url = 'http://localhost:8080/frontend/vip_analytics_dashboard.html'
            webbrowser.open(dashboard_url)
            
            logger.info(f"✅ Analytics Dashboard opened: {dashboard_url}")
            
        except Exception as e:
            logger.error(f"❌ Failed to open dashboard: {e}")
    
    def generate_initial_report(self):
        """Generate an initial analytics report"""
        logger.info("📄 Generating initial analytics report...")
        
        try:
            # Run a quick analysis of existing data
            report_process = subprocess.Popen([
                sys.executable, '-c', '''
import json
import glob
from datetime import datetime

# Quick analysis of existing demo reports
demo_files = glob.glob("professional_demo_report_*.json")
system_files = glob.glob("logs/system_test_report_*.json")

summary = {
    "generated_at": datetime.now().isoformat(),
    "data_sources": {
        "demo_reports": len(demo_files),
        "system_tests": len(system_files)
    },
    "status": "VIP Analytics Dashboard Ready",
    "recommendations": [
        "Review executive summary for key insights",
        "Monitor performance trends for optimization opportunities",
        "Export comprehensive reports for stakeholder presentations"
    ]
}

with open("vip_analytics_initial_report.json", "w") as f:
    json.dump(summary, f, indent=2)

print("📊 Initial analytics report generated: vip_analytics_initial_report.json")
'''
            ], cwd=self.base_dir)
            
            report_process.wait()
            logger.info("✅ Initial analytics report generated")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not generate initial report: {e}")
    
    def monitor_services(self):
        """Monitor running services"""
        logger.info("👁️ Monitoring VIP Analytics services...")
        logger.info("Press Ctrl+C to stop all services")
        
        try:
            while True:
                # Check if all processes are still running
                running_processes = []
                for name, process in self.processes:
                    if process.poll() is None:
                        running_processes.append(name)
                    else:
                        logger.warning(f"⚠️ Service stopped: {name}")
                
                if running_processes:
                    logger.info(f"✅ Running services: {', '.join(running_processes)}")
                else:
                    logger.warning("⚠️ No services running")
                    break
                
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested by user")
            self.cleanup()
    
    def cleanup(self):
        """Clean up all running processes"""
        logger.info("🧹 Cleaning up VIP Analytics services...")
        
        for name, process in self.processes:
            try:
                if process.poll() is None:
                    logger.info(f"🛑 Stopping {name}...")
                    process.terminate()
                    process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️ Force killing {name}...")
                process.kill()
            except Exception as e:
                logger.error(f"❌ Error stopping {name}: {e}")
        
        logger.info("✅ VIP Analytics Dashboard Suite stopped")

def main():
    """Main entry point"""
    print("📊 VIP Professional Analytics Dashboard")
    print("=" * 50)
    print("Executive-Grade Analytics for AR Sandbox RC")
    print("=" * 50)
    print()
    print("Features:")
    print("• 📈 Executive Summary Dashboard")
    print("• 💰 ROI Analysis & Business Metrics")
    print("• 🔧 System Health Monitoring")
    print("• 👥 User Engagement Analytics")
    print("• 📊 Performance Trend Analysis")
    print("• 📄 Comprehensive Report Generation")
    print("• ⚡ Real-time Data Visualization")
    print()
    print("=" * 50)
    
    launcher = VIPAnalyticsLauncher()
    
    try:
        launcher.launch_analytics_suite()
    except KeyboardInterrupt:
        print("\n🛑 Launch cancelled by user")
        launcher.cleanup()
    except Exception as e:
        print(f"❌ Launch failed: {e}")
        launcher.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()

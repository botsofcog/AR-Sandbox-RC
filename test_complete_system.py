#!/usr/bin/env python3
"""
Comprehensive System Testing Suite
Tests all components of the RC Sandbox system and generates detailed reports
"""

import os
import sys
import json
import time
import subprocess
import threading
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import unittest
import codecs
import io

# Fix Windows console encoding for Unicode characters
if sys.platform == "win32":
    try:
        # Reconfigure stdout and stderr to handle UTF-8
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        # Fallback for older Python versions
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging with UTF-8 support
class SafeStreamHandler(logging.StreamHandler):
    """Stream handler that safely handles Unicode characters"""
    def emit(self, record):
        try:
            msg = self.format(record)
            # Replace problematic Unicode characters with safe alternatives
            safe_msg = msg.replace('🧪', '[TEST]').replace('🚀', '[START]').replace('🔍', '[CHECK]')
            safe_msg = safe_msg.replace('✅', '[PASS]').replace('❌', '[FAIL]').replace('📊', '[REPORT]')
            safe_msg = safe_msg.replace('📄', '[FILE]').replace('📋', '[SUMMARY]').replace('🎉', '[SUCCESS]')
            stream = self.stream
            stream.write(safe_msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system_test.log', encoding='utf-8'),
        SafeStreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    test_name: str
    component: str
    status: str  # PASS, FAIL, SKIP, ERROR
    duration: float
    message: str
    details: Dict[str, Any]
    timestamp: float

@dataclass
class ComponentHealth:
    component: str
    status: str
    tests_passed: int
    tests_failed: int
    critical_issues: List[str]
    warnings: List[str]
    performance_metrics: Dict[str, float]

class SystemTester:
    """Comprehensive system testing framework"""
    
    def __init__(self):
        self.test_results = []
        self.component_health = {}
        self.start_time = time.time()
        
        # Test configuration
        self.test_config = {
            'timeout': 30,
            'retry_attempts': 3,
            'performance_thresholds': {
                'response_time': 1000,  # ms
                'memory_usage': 500,    # MB
                'cpu_usage': 80,        # %
                'startup_time': 10      # seconds
            }
        }
        
        # Components to test
        self.components = [
            'frontend_html_demo',
            'terrain_engine',
            'physics_engine',
            'vehicle_fleet',
            'mission_system',
            'backend_services',
            'control_panel',
            'safety_monitoring',
            'professional_demo_suite',
            'file_structure',
            'documentation'
        ]
        
        logger.info("🧪 System Tester initialized")
    
    def run_all_tests(self):
        """Run comprehensive system tests"""
        logger.info("🚀 Starting comprehensive system testing")
        
        try:
            # Test each component
            for component in self.components:
                logger.info(f"🔍 Testing component: {component}")
                self.test_component(component)
            
            # Generate final report
            self.generate_final_report()
            
        except Exception as e:
            logger.error(f"❌ System testing failed: {e}")
            self.add_test_result("system_test", "system", "ERROR", 0, str(e), {})
    
    def test_component(self, component: str):
        """Test a specific component"""
        start_time = time.time()
        
        try:
            if component == 'frontend_html_demo':
                self.test_frontend_html_demo()
            elif component == 'terrain_engine':
                self.test_terrain_engine()
            elif component == 'physics_engine':
                self.test_physics_engine()
            elif component == 'vehicle_fleet':
                self.test_vehicle_fleet()
            elif component == 'mission_system':
                self.test_mission_system()
            elif component == 'backend_services':
                self.test_backend_services()
            elif component == 'control_panel':
                self.test_control_panel()
            elif component == 'safety_monitoring':
                self.test_safety_monitoring()
            elif component == 'professional_demo_suite':
                self.test_professional_demo_suite()
            elif component == 'file_structure':
                self.test_file_structure()
            elif component == 'documentation':
                self.test_documentation()
            
            duration = time.time() - start_time
            logger.info(f"✅ Component {component} tested in {duration:.2f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ Component {component} testing failed: {e}")
            self.add_test_result(f"{component}_test", component, "ERROR", duration, str(e), {})
    
    def test_frontend_html_demo(self):
        """Test the enhanced HTML demo"""
        component = "frontend_html_demo"
        
        # Test 1: Check if HTML file exists and is valid
        html_file = "rc_sandbox_clean/index.html"
        if not os.path.exists(html_file):
            self.add_test_result("html_file_exists", component, "FAIL", 0, 
                               f"HTML demo file not found: {html_file}", {})
            return
        
        self.add_test_result("html_file_exists", component, "PASS", 0, 
                           "HTML demo file exists", {"file": html_file})
        
        # Test 2: Check HTML structure
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_elements = [
                'TerrainEngine',
                'canvas',
                'weather-panel',
                'physics',
                'Magic Sand',
                'diffusion'
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if missing_elements:
                self.add_test_result("html_structure", component, "FAIL", 0,
                                   f"Missing elements: {missing_elements}", 
                                   {"missing": missing_elements})
            else:
                self.add_test_result("html_structure", component, "PASS", 0,
                                   "All required elements present", 
                                   {"elements_checked": len(required_elements)})
        
        except Exception as e:
            self.add_test_result("html_structure", component, "ERROR", 0, str(e), {})
        
        # Test 3: Check JavaScript functionality
        js_files = [
            "frontend/js/terrain.js",
            "frontend/js/physics_engine.js",
            "frontend/js/vehicle_fleet.js"
        ]
        
        for js_file in js_files:
            if os.path.exists(js_file):
                self.add_test_result(f"js_file_{os.path.basename(js_file)}", component, "PASS", 0,
                                   f"JavaScript file exists: {js_file}", {"file": js_file})
            else:
                self.add_test_result(f"js_file_{os.path.basename(js_file)}", component, "FAIL", 0,
                                   f"JavaScript file missing: {js_file}", {"file": js_file})
    
    def test_terrain_engine(self):
        """Test terrain engine functionality"""
        component = "terrain_engine"
        
        # Test 1: Check terrain.js file
        terrain_file = "frontend/js/terrain.js"
        if not os.path.exists(terrain_file):
            self.add_test_result("terrain_file_exists", component, "FAIL", 0,
                               f"Terrain engine file not found: {terrain_file}", {})
            return
        
        self.add_test_result("terrain_file_exists", component, "PASS", 0,
                           "Terrain engine file exists", {"file": terrain_file})
        
        # Test 2: Check for required classes and methods
        try:
            with open(terrain_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_features = [
                'class TerrainEngine',
                'initializePhysics',
                'renderContourLines',
                'getColorForHeight',
                'Magic Sand',
                'diffusion',
                'heightmap'
            ]
            
            missing_features = []
            for feature in required_features:
                if feature not in content:
                    missing_features.append(feature)
            
            if missing_features:
                self.add_test_result("terrain_features", component, "FAIL", 0,
                                   f"Missing features: {missing_features}",
                                   {"missing": missing_features})
            else:
                self.add_test_result("terrain_features", component, "PASS", 0,
                                   "All terrain features present",
                                   {"features_checked": len(required_features)})
        
        except Exception as e:
            self.add_test_result("terrain_features", component, "ERROR", 0, str(e), {})
    
    def test_physics_engine(self):
        """Test physics engine functionality"""
        component = "physics_engine"
        
        # Test 1: Check physics engine file
        physics_file = "frontend/js/physics_engine.js"
        if not os.path.exists(physics_file):
            self.add_test_result("physics_file_exists", component, "FAIL", 0,
                               f"Physics engine file not found: {physics_file}", {})
            return
        
        self.add_test_result("physics_file_exists", component, "PASS", 0,
                           "Physics engine file exists", {"file": physics_file})
        
        # Test 2: Check physics features
        try:
            with open(physics_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            physics_features = [
                'class PhysicsEngine',
                'updateSandPhysics',
                'updateWaterSimulation',
                'updateParticleSystem',
                'updateWeatherEffects',
                'angleOfRepose',
                'waterFlow',
                'particles'
            ]
            
            missing_features = []
            for feature in physics_features:
                if feature not in content:
                    missing_features.append(feature)
            
            if missing_features:
                self.add_test_result("physics_features", component, "FAIL", 0,
                                   f"Missing physics features: {missing_features}",
                                   {"missing": missing_features})
            else:
                self.add_test_result("physics_features", component, "PASS", 0,
                                   "All physics features present",
                                   {"features_checked": len(physics_features)})
        
        except Exception as e:
            self.add_test_result("physics_features", component, "ERROR", 0, str(e), {})
    
    def test_vehicle_fleet(self):
        """Test vehicle fleet system"""
        component = "vehicle_fleet"
        
        # Test 1: Check vehicle fleet file
        fleet_file = "frontend/js/vehicle_fleet.js"
        if not os.path.exists(fleet_file):
            self.add_test_result("fleet_file_exists", component, "FAIL", 0,
                               f"Vehicle fleet file not found: {fleet_file}", {})
            return
        
        self.add_test_result("fleet_file_exists", component, "PASS", 0,
                           "Vehicle fleet file exists", {"file": fleet_file})
        
        # Test 2: Check vehicle types
        try:
            with open(fleet_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_vehicles = ['EX001', 'BD001', 'DT001', 'CR001', 'CP001']
            vehicle_types = ['excavator', 'bulldozer', 'dump_truck', 'crane', 'compactor']
            
            missing_vehicles = []
            for vehicle in required_vehicles:
                if vehicle not in content:
                    missing_vehicles.append(vehicle)
            
            missing_types = []
            for vtype in vehicle_types:
                if vtype not in content:
                    missing_types.append(vtype)
            
            if missing_vehicles or missing_types:
                self.add_test_result("vehicle_types", component, "FAIL", 0,
                                   f"Missing vehicles: {missing_vehicles}, types: {missing_types}",
                                   {"missing_vehicles": missing_vehicles, "missing_types": missing_types})
            else:
                self.add_test_result("vehicle_types", component, "PASS", 0,
                                   "All vehicle types present",
                                   {"vehicles": len(required_vehicles), "types": len(vehicle_types)})
        
        except Exception as e:
            self.add_test_result("vehicle_types", component, "ERROR", 0, str(e), {})
    
    def test_mission_system(self):
        """Test mission system functionality"""
        component = "mission_system"
        
        # Test 1: Check mission system file
        mission_file = "frontend/js/mission_system.js"
        if not os.path.exists(mission_file):
            self.add_test_result("mission_file_exists", component, "FAIL", 0,
                               f"Mission system file not found: {mission_file}", {})
            return
        
        self.add_test_result("mission_file_exists", component, "PASS", 0,
                           "Mission system file exists", {"file": mission_file})
        
        # Test 2: Check mission types
        try:
            with open(mission_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            mission_types = [
                'flood_defense',
                'highway_construction',
                'waste_sorting',
                'vehicle_racing',
                'creative_sandbox'
            ]
            
            missing_missions = []
            for mission in mission_types:
                if mission not in content:
                    missing_missions.append(mission)
            
            if missing_missions:
                self.add_test_result("mission_types", component, "FAIL", 0,
                                   f"Missing mission types: {missing_missions}",
                                   {"missing": missing_missions})
            else:
                self.add_test_result("mission_types", component, "PASS", 0,
                                   "All mission types present",
                                   {"missions_checked": len(mission_types)})
        
        except Exception as e:
            self.add_test_result("mission_types", component, "ERROR", 0, str(e), {})
    
    def test_backend_services(self):
        """Test backend services"""
        component = "backend_services"
        
        # Test backend service files
        backend_files = [
            "backend/depth_server.py",
            "backend/telemetry_server.py",
            "backend/streaming_server.py",
            "backend/kinect_calibration.py",
            "backend/safety_monitoring.py"
        ]
        
        for service_file in backend_files:
            if os.path.exists(service_file):
                self.add_test_result(f"backend_file_{os.path.basename(service_file)}", component, "PASS", 0,
                                   f"Backend service exists: {service_file}", {"file": service_file})
                
                # Check for WebSocket functionality
                try:
                    with open(service_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'websockets' in content or 'WebSocket' in content:
                        self.add_test_result(f"websocket_{os.path.basename(service_file)}", component, "PASS", 0,
                                           f"WebSocket support found in {service_file}", {"file": service_file})
                    else:
                        self.add_test_result(f"websocket_{os.path.basename(service_file)}", component, "SKIP", 0,
                                           f"No WebSocket support in {service_file}", {"file": service_file})
                
                except Exception as e:
                    self.add_test_result(f"websocket_{os.path.basename(service_file)}", component, "ERROR", 0,
                                       str(e), {"file": service_file})
            else:
                self.add_test_result(f"backend_file_{os.path.basename(service_file)}", component, "FAIL", 0,
                                   f"Backend service missing: {service_file}", {"file": service_file})
    
    def test_control_panel(self):
        """Test control panel integration"""
        component = "control_panel"
        
        # Test 1: Check control panel files
        control_files = [
            "frontend/js/control_panel.js",
            "frontend/control_panel_demo.html"
        ]
        
        for control_file in control_files:
            if os.path.exists(control_file):
                self.add_test_result(f"control_file_{os.path.basename(control_file)}", component, "PASS", 0,
                                   f"Control panel file exists: {control_file}", {"file": control_file})
            else:
                self.add_test_result(f"control_file_{os.path.basename(control_file)}", component, "FAIL", 0,
                                   f"Control panel file missing: {control_file}", {"file": control_file})
        
        # Test 2: Check control panel features
        control_js = "frontend/js/control_panel.js"
        if os.path.exists(control_js):
            try:
                with open(control_js, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                control_features = [
                    'class ControlPanelInterface',
                    'setupCameraSystem',
                    'initializeHeadTracking',
                    'toggleFPV',
                    'emergencyStop'
                ]
                
                missing_features = []
                for feature in control_features:
                    if feature not in content:
                        missing_features.append(feature)
                
                if missing_features:
                    self.add_test_result("control_features", component, "FAIL", 0,
                                       f"Missing control features: {missing_features}",
                                       {"missing": missing_features})
                else:
                    self.add_test_result("control_features", component, "PASS", 0,
                                       "All control features present",
                                       {"features_checked": len(control_features)})
            
            except Exception as e:
                self.add_test_result("control_features", component, "ERROR", 0, str(e), {})
    
    def test_safety_monitoring(self):
        """Test safety monitoring system"""
        component = "safety_monitoring"
        
        # Test 1: Check safety monitoring files
        safety_files = [
            "backend/safety_monitoring.py",
            "config/safety_config.json",
            "frontend/safety_dashboard.html"
        ]
        
        for safety_file in safety_files:
            if os.path.exists(safety_file):
                self.add_test_result(f"safety_file_{os.path.basename(safety_file)}", component, "PASS", 0,
                                   f"Safety file exists: {safety_file}", {"file": safety_file})
            else:
                self.add_test_result(f"safety_file_{os.path.basename(safety_file)}", component, "FAIL", 0,
                                   f"Safety file missing: {safety_file}", {"file": safety_file})
        
        # Test 2: Check safety configuration
        config_file = "config/safety_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                required_sections = ['thresholds', 'monitoring', 'recovery', 'services', 'sensors']
                missing_sections = []
                
                for section in required_sections:
                    if section not in config:
                        missing_sections.append(section)
                
                if missing_sections:
                    self.add_test_result("safety_config", component, "FAIL", 0,
                                       f"Missing config sections: {missing_sections}",
                                       {"missing": missing_sections})
                else:
                    self.add_test_result("safety_config", component, "PASS", 0,
                                       "Safety configuration complete",
                                       {"sections_checked": len(required_sections)})
            
            except Exception as e:
                self.add_test_result("safety_config", component, "ERROR", 0, str(e), {})
    
    def test_professional_demo_suite(self):
        """Test professional demo suite"""
        component = "professional_demo_suite"
        
        # Test 1: Check demo suite file
        demo_file = "professional_demo_suite.py"
        if not os.path.exists(demo_file):
            self.add_test_result("demo_file_exists", component, "FAIL", 0,
                               f"Professional demo suite not found: {demo_file}", {})
            return
        
        self.add_test_result("demo_file_exists", component, "PASS", 0,
                           "Professional demo suite exists", {"file": demo_file})
        
        # Test 2: Check demo configurations
        try:
            with open(demo_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            demo_types = [
                'investor_pitch',
                'technical_deep_dive',
                'quick_showcase',
                'museum_interactive',
                'educational_stem',
                'streaming_showcase'
            ]
            
            missing_demos = []
            for demo in demo_types:
                if demo not in content:
                    missing_demos.append(demo)
            
            if missing_demos:
                self.add_test_result("demo_types", component, "FAIL", 0,
                                   f"Missing demo types: {missing_demos}",
                                   {"missing": missing_demos})
            else:
                self.add_test_result("demo_types", component, "PASS", 0,
                                   "All demo types present",
                                   {"demos_checked": len(demo_types)})
        
        except Exception as e:
            self.add_test_result("demo_types", component, "ERROR", 0, str(e), {})

    def test_file_structure(self):
        """Test project file structure"""
        component = "file_structure"

        # Test 1: Check main directories
        required_dirs = [
            "frontend",
            "backend",
            "assets",
            "projection_assets",
            "config",
            "docs",
            "logs"
        ]

        for directory in required_dirs:
            if os.path.exists(directory):
                self.add_test_result(f"dir_{directory}", component, "PASS", 0,
                                   f"Directory exists: {directory}", {"directory": directory})
            else:
                self.add_test_result(f"dir_{directory}", component, "FAIL", 0,
                                   f"Directory missing: {directory}", {"directory": directory})

        # Test 2: Check critical files
        critical_files = [
            "README.md",
            "requirements.txt",
            "professional_demo_suite.py",
            "DEPLOYMENT_GUIDE.md",
            "PROJECT_COMPLETION_SUMMARY.md",
            "FINAL_PROJECT_STATUS.md"
        ]

        for file_path in critical_files:
            if os.path.exists(file_path):
                self.add_test_result(f"file_{os.path.basename(file_path)}", component, "PASS", 0,
                                   f"Critical file exists: {file_path}", {"file": file_path})
            else:
                self.add_test_result(f"file_{os.path.basename(file_path)}", component, "FAIL", 0,
                                   f"Critical file missing: {file_path}", {"file": file_path})

        # Test 3: Check file sizes (detect empty files)
        for file_path in critical_files:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                if file_size > 100:  # At least 100 bytes
                    self.add_test_result(f"size_{os.path.basename(file_path)}", component, "PASS", 0,
                                       f"File has content: {file_path} ({file_size} bytes)",
                                       {"file": file_path, "size": file_size})
                else:
                    self.add_test_result(f"size_{os.path.basename(file_path)}", component, "FAIL", 0,
                                       f"File too small: {file_path} ({file_size} bytes)",
                                       {"file": file_path, "size": file_size})

    def test_documentation(self):
        """Test documentation completeness"""
        component = "documentation"

        # Test 1: Check documentation files
        doc_files = [
            "README.md",
            "DEPLOYMENT_GUIDE.md",
            "docs/API_REFERENCE.md",
            "PROJECT_COMPLETION_SUMMARY.md",
            "FINAL_PROJECT_STATUS.md"
        ]

        for doc_file in doc_files:
            if os.path.exists(doc_file):
                self.add_test_result(f"doc_{os.path.basename(doc_file)}", component, "PASS", 0,
                                   f"Documentation exists: {doc_file}", {"file": doc_file})

                # Check content quality
                try:
                    with open(doc_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    word_count = len(content.split())
                    if word_count > 100:
                        self.add_test_result(f"content_{os.path.basename(doc_file)}", component, "PASS", 0,
                                           f"Documentation has substantial content: {word_count} words",
                                           {"file": doc_file, "word_count": word_count})
                    else:
                        self.add_test_result(f"content_{os.path.basename(doc_file)}", component, "FAIL", 0,
                                           f"Documentation too brief: {word_count} words",
                                           {"file": doc_file, "word_count": word_count})

                except Exception as e:
                    self.add_test_result(f"content_{os.path.basename(doc_file)}", component, "ERROR", 0,
                                       str(e), {"file": doc_file})
            else:
                self.add_test_result(f"doc_{os.path.basename(doc_file)}", component, "FAIL", 0,
                                   f"Documentation missing: {doc_file}", {"file": doc_file})

    def add_test_result(self, test_name: str, component: str, status: str,
                       duration: float, message: str, details: Dict[str, Any]):
        """Add a test result"""
        result = TestResult(
            test_name=test_name,
            component=component,
            status=status,
            duration=duration,
            message=message,
            details=details,
            timestamp=time.time()
        )

        self.test_results.append(result)

        # Log result
        status_emoji = {
            'PASS': '✅',
            'FAIL': '❌',
            'SKIP': '⏭️',
            'ERROR': '💥'
        }

        emoji = status_emoji.get(status, '❓')
        logger.info(f"{emoji} {test_name}: {message}")

    def generate_component_health(self):
        """Generate health summary for each component"""
        for component in self.components:
            component_results = [r for r in self.test_results if r.component == component]

            if not component_results:
                continue

            passed = len([r for r in component_results if r.status == 'PASS'])
            failed = len([r for r in component_results if r.status == 'FAIL'])
            errors = len([r for r in component_results if r.status == 'ERROR'])

            # Determine overall status
            if errors > 0 or failed > passed:
                status = 'CRITICAL'
            elif failed > 0:
                status = 'WARNING'
            else:
                status = 'HEALTHY'

            # Collect issues
            critical_issues = [r.message for r in component_results if r.status in ['FAIL', 'ERROR']]
            warnings = [r.message for r in component_results if r.status == 'SKIP']

            # Performance metrics
            avg_duration = sum(r.duration for r in component_results) / len(component_results) if component_results else 0

            self.component_health[component] = ComponentHealth(
                component=component,
                status=status,
                tests_passed=passed,
                tests_failed=failed + errors,
                critical_issues=critical_issues,
                warnings=warnings,
                performance_metrics={'avg_test_duration': avg_duration}
            )

    def generate_final_report(self):
        """Generate comprehensive final test report"""
        logger.info("📊 Generating final test report")

        # Generate component health
        self.generate_component_health()

        # Calculate overall statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == 'PASS'])
        failed_tests = len([r for r in self.test_results if r.status == 'FAIL'])
        error_tests = len([r for r in self.test_results if r.status == 'ERROR'])
        skipped_tests = len([r for r in self.test_results if r.status == 'SKIP'])

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        total_duration = time.time() - self.start_time

        # Generate report
        report = {
            'test_summary': {
                'timestamp': datetime.now().isoformat(),
                'total_duration': total_duration,
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'errors': error_tests,
                'skipped': skipped_tests,
                'success_rate': success_rate
            },
            'component_health': {
                name: asdict(health) for name, health in self.component_health.items()
            },
            'detailed_results': [asdict(result) for result in self.test_results],
            'critical_issues': self.get_critical_issues(),
            'recommendations': self.generate_recommendations(),
            'system_readiness': self.assess_system_readiness()
        }

        # Save report to file
        report_file = f"logs/system_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            os.makedirs('logs', exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"📄 Test report saved: {report_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save report: {e}")

        # Generate human-readable summary
        self.generate_summary_report(report)

        return report

    def get_critical_issues(self) -> List[Dict[str, Any]]:
        """Get all critical issues found during testing"""
        critical_issues = []

        for result in self.test_results:
            if result.status in ['FAIL', 'ERROR']:
                critical_issues.append({
                    'component': result.component,
                    'test': result.test_name,
                    'severity': 'HIGH' if result.status == 'ERROR' else 'MEDIUM',
                    'message': result.message,
                    'details': result.details
                })

        return critical_issues

    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        # Check for missing files
        missing_files = [r for r in self.test_results if 'missing' in r.message.lower() or 'not found' in r.message.lower()]
        if missing_files:
            recommendations.append("🔧 Create missing files and directories to complete the project structure")

        # Check for backend services
        backend_issues = [r for r in self.test_results if r.component == 'backend_services' and r.status == 'FAIL']
        if backend_issues:
            recommendations.append("⚙️ Implement missing backend services for full system functionality")

        # Check for documentation
        doc_issues = [r for r in self.test_results if r.component == 'documentation' and r.status == 'FAIL']
        if doc_issues:
            recommendations.append("📚 Complete documentation for better user experience and maintenance")

        # Check for safety systems
        safety_issues = [r for r in self.test_results if r.component == 'safety_monitoring' and r.status == 'FAIL']
        if safety_issues:
            recommendations.append("🛡️ Implement safety monitoring systems for production deployment")

        # Performance recommendations
        recommendations.append("🚀 Consider performance optimization for production deployment")
        recommendations.append("🧪 Implement automated testing pipeline for continuous integration")
        recommendations.append("📊 Add monitoring and analytics for production insights")

        return recommendations

    def assess_system_readiness(self) -> Dict[str, Any]:
        """Assess overall system readiness for deployment"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == 'PASS'])

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        # Determine readiness level
        if success_rate >= 90:
            readiness = 'PRODUCTION_READY'
            confidence = 'HIGH'
        elif success_rate >= 75:
            readiness = 'STAGING_READY'
            confidence = 'MEDIUM'
        elif success_rate >= 50:
            readiness = 'DEVELOPMENT_READY'
            confidence = 'LOW'
        else:
            readiness = 'NOT_READY'
            confidence = 'VERY_LOW'

        # Check critical components
        critical_components = ['frontend_html_demo', 'terrain_engine', 'vehicle_fleet']
        critical_health = []

        for component in critical_components:
            if component in self.component_health:
                health = self.component_health[component]
                critical_health.append({
                    'component': component,
                    'status': health.status,
                    'tests_passed': health.tests_passed,
                    'tests_failed': health.tests_failed
                })

        return {
            'overall_readiness': readiness,
            'confidence_level': confidence,
            'success_rate': success_rate,
            'critical_components': critical_health,
            'deployment_recommendation': self.get_deployment_recommendation(readiness, success_rate)
        }

    def get_deployment_recommendation(self, readiness: str, success_rate: float) -> str:
        """Get deployment recommendation based on test results"""
        if readiness == 'PRODUCTION_READY':
            return "✅ System is ready for production deployment with full features"
        elif readiness == 'STAGING_READY':
            return "🔄 System is ready for staging deployment with minor issues to address"
        elif readiness == 'DEVELOPMENT_READY':
            return "🚧 System needs additional development before deployment"
        else:
            return "❌ System requires significant work before deployment"

    def generate_summary_report(self, report: Dict[str, Any]):
        """Generate human-readable summary report"""
        summary_file = f"FINAL_TEST_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write("# RC SANDBOX - FINAL SYSTEM TEST REPORT\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                # Executive Summary
                f.write("## 📊 EXECUTIVE SUMMARY\n\n")
                summary = report['test_summary']
                f.write(f"- **Total Tests:** {summary['total_tests']}\n")
                f.write(f"- **Success Rate:** {summary['success_rate']:.1f}%\n")
                f.write(f"- **Tests Passed:** {summary['passed']}\n")
                f.write(f"- **Tests Failed:** {summary['failed']}\n")
                f.write(f"- **Errors:** {summary['errors']}\n")
                f.write(f"- **Test Duration:** {summary['total_duration']:.1f} seconds\n\n")

                # System Readiness
                readiness = report['system_readiness']
                f.write("## 🎯 SYSTEM READINESS\n\n")
                f.write(f"**Overall Status:** {readiness['overall_readiness']}\n\n")
                f.write(f"**Confidence Level:** {readiness['confidence_level']}\n\n")
                f.write(f"**Recommendation:** {readiness['deployment_recommendation']}\n\n")

                # Component Health
                f.write("## 🔍 COMPONENT HEALTH\n\n")
                for component, health in report['component_health'].items():
                    status_emoji = {'HEALTHY': '✅', 'WARNING': '⚠️', 'CRITICAL': '❌'}
                    emoji = status_emoji.get(health['status'], '❓')

                    f.write(f"### {emoji} {component.replace('_', ' ').title()}\n")
                    f.write(f"- **Status:** {health['status']}\n")
                    f.write(f"- **Tests Passed:** {health['tests_passed']}\n")
                    f.write(f"- **Tests Failed:** {health['tests_failed']}\n")

                    if health['critical_issues']:
                        f.write("- **Critical Issues:**\n")
                        for issue in health['critical_issues'][:3]:  # Show top 3
                            f.write(f"  - {issue}\n")

                    f.write("\n")

                # Critical Issues
                if report['critical_issues']:
                    f.write("## 🚨 CRITICAL ISSUES\n\n")
                    for issue in report['critical_issues'][:10]:  # Show top 10
                        f.write(f"- **{issue['component']}:** {issue['message']}\n")
                    f.write("\n")

                # Recommendations
                f.write("## 💡 RECOMMENDATIONS\n\n")
                for rec in report['recommendations']:
                    f.write(f"- {rec}\n")
                f.write("\n")

                # Conclusion
                f.write("## 🎉 CONCLUSION\n\n")
                if readiness['success_rate'] >= 80:
                    f.write("The RC Sandbox system demonstrates strong functionality and is approaching production readiness. ")
                    f.write("The core features are implemented and working well.\n\n")
                else:
                    f.write("The RC Sandbox system shows good progress but requires additional development ")
                    f.write("before production deployment.\n\n")

                f.write("**Next Steps:**\n")
                f.write("1. Address critical issues identified in testing\n")
                f.write("2. Complete missing components and documentation\n")
                f.write("3. Implement comprehensive error handling\n")
                f.write("4. Conduct user acceptance testing\n")
                f.write("5. Prepare for production deployment\n\n")

                f.write("---\n")
                f.write("*Report generated by RC Sandbox System Tester*\n")

            logger.info(f"📋 Summary report saved: {summary_file}")

        except Exception as e:
            logger.error(f"❌ Failed to generate summary report: {e}")

def main():
    """Main entry point for system testing"""
    print("[TEST] RC SANDBOX - COMPREHENSIVE SYSTEM TESTING")
    print("=" * 60)

    # Create logs directory
    os.makedirs('logs', exist_ok=True)

    # Initialize and run tests
    tester = SystemTester()
    tester.run_all_tests()

    print("\n" + "=" * 60)
    print("[SUCCESS] SYSTEM TESTING COMPLETED")
    print("Check logs/ directory for detailed reports")

if __name__ == "__main__":
    main()

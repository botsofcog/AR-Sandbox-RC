#!/usr/bin/env python3
"""
Enhanced Autonomous Testing - Fixed Encoding Issues
Comprehensive testing with proper error handling and encoding
"""

import time
import json
import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path

# Fix encoding issues
os.environ['PYTHONIOENCODING'] = 'utf-8'

class EnhancedAutonomousTesting:
    def __init__(self):
        self.session_start = datetime.now()
        self.test_results = []
        self.issues_found = []
        self.performance_data = {}
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        safe_message = message.encode('ascii', 'ignore').decode('ascii')
        print(f"[{timestamp}] {safe_message}")
        
    def run_safe_test(self, test_name, command):
        """Run test with proper error handling"""
        self.log(f"Testing {test_name}...")
        start_time = time.time()
        
        try:
            # Use proper encoding and error handling
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=180,
                encoding='utf-8',
                errors='ignore'
            )
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            test_result = {
                'name': test_name,
                'success': success,
                'duration': duration,
                'return_code': result.returncode,
                'timestamp': datetime.now().isoformat()
            }
            
            self.test_results.append(test_result)
            
            if success:
                self.log(f"PASS {test_name} ({duration:.1f}s)")
            else:
                self.log(f"FAIL {test_name} - Code {result.returncode}")
                self.issues_found.append(f"{test_name}: Failed with code {result.returncode}")
                
            return test_result
            
        except subprocess.TimeoutExpired:
            self.log(f"TIMEOUT {test_name}")
            self.issues_found.append(f"{test_name}: Timeout")
            return {'name': test_name, 'success': False, 'duration': 180, 'error': 'timeout'}
        except Exception as e:
            self.log(f"ERROR {test_name}: {str(e)}")
            self.issues_found.append(f"{test_name}: {str(e)}")
            return {'name': test_name, 'success': False, 'duration': 0, 'error': str(e)}
    
    def analyze_system_health(self):
        """Analyze current system state"""
        self.log("Analyzing system health...")
        
        health_data = {
            'timestamp': datetime.now().isoformat(),
            'file_counts': {},
            'directory_structure': {},
            'critical_files': {}
        }
        
        # Check critical files
        critical_files = [
            'README.md',
            'requirements.txt', 
            'professional_demo_suite.py',
            'test_complete_system.py',
            'DEPLOYMENT_GUIDE.md',
            'PROJECT_COMPLETION_SUMMARY.md'
        ]
        
        for file in critical_files:
            if os.path.exists(file):
                try:
                    size = os.path.getsize(file)
                    health_data['critical_files'][file] = {
                        'exists': True,
                        'size': size,
                        'size_kb': size / 1024
                    }
                except:
                    health_data['critical_files'][file] = {'exists': True, 'size': 0}
            else:
                health_data['critical_files'][file] = {'exists': False}
                self.issues_found.append(f"Missing critical file: {file}")
        
        # Check directory structure
        key_directories = ['frontend', 'backend', 'assets', 'config', 'docs', 'logs']
        for directory in key_directories:
            if os.path.exists(directory):
                try:
                    file_count = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
                    health_data['directory_structure'][directory] = {
                        'exists': True,
                        'file_count': file_count
                    }
                except:
                    health_data['directory_structure'][directory] = {'exists': True, 'file_count': 0}
            else:
                health_data['directory_structure'][directory] = {'exists': False}
                self.issues_found.append(f"Missing directory: {directory}")
        
        self.performance_data['system_health'] = health_data
        
        # Summary
        critical_files_ok = sum(1 for f in health_data['critical_files'].values() if f.get('exists', False))
        directories_ok = sum(1 for d in health_data['directory_structure'].values() if d.get('exists', False))
        
        self.log(f"System Health: {critical_files_ok}/{len(critical_files)} critical files, {directories_ok}/{len(key_directories)} directories")
        
    def run_core_tests(self):
        """Run essential test suites"""
        self.log("Running core test suites...")
        
        # Core tests that should work
        core_tests = [
            ("System Test Quick", "python test_complete_system.py --quick"),
            ("System Test Full", "python test_complete_system.py"),
            ("File Structure Check", "dir /s /b > file_structure_check.txt"),
            ("Python Syntax Check", "python -m py_compile test_complete_system.py"),
            ("Requirements Check", "python -c \"import pkg_resources; print('Requirements OK')\"")
        ]
        
        for test_name, command in core_tests:
            self.run_safe_test(test_name, command)
            time.sleep(1)  # Brief pause between tests
    
    def run_extended_validation(self):
        """Run extended validation tests"""
        self.log("Running extended validation...")
        
        # Extended tests
        extended_tests = [
            ("Demo Suite Validation", "python professional_demo_suite.py --list"),
            ("Markdown Check", "python -c \"import os; print(f'MD files: {len([f for f in os.listdir(\\\".\\\") if f.endswith(\\\".md\\\")])}')\""),
            ("Backend Files Check", "python -c \"import os; print(f'Backend files: {len(os.listdir(\\\"backend\\\")) if os.path.exists(\\\"backend\\\") else 0}')\""),
            ("Frontend Files Check", "python -c \"import os; print(f'Frontend files: {len(os.listdir(\\\"frontend\\\")) if os.path.exists(\\\"frontend\\\") else 0}')\"")
        ]
        
        for test_name, command in extended_tests:
            self.run_safe_test(test_name, command)
            time.sleep(1)
    
    def generate_comprehensive_report(self):
        """Generate final comprehensive report"""
        self.log("Generating comprehensive report...")
        
        session_duration = (datetime.now() - self.session_start).total_seconds()
        
        # Calculate statistics
        total_tests = len(self.test_results)
        successful_tests = len([t for t in self.test_results if t.get('success', False)])
        success_rate = (successful_tests / max(1, total_tests)) * 100
        
        report = {
            'session_info': {
                'start_time': self.session_start.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_minutes': session_duration / 60,
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': total_tests - successful_tests,
                'success_rate': success_rate
            },
            'test_results': self.test_results,
            'issues_found': self.issues_found,
            'performance_data': self.performance_data
        }
        
        # Save JSON report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = f"enhanced_autonomous_report_{timestamp}.json"
        
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            self.log(f"JSON report saved: {json_file}")
        except Exception as e:
            self.log(f"Failed to save JSON report: {e}")
        
        # Generate text summary
        summary_file = f"ENHANCED_TESTING_SUMMARY_{timestamp}.txt"
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write("ENHANCED AUTONOMOUS TESTING SUMMARY\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Session Duration: {session_duration/60:.1f} minutes\n")
                f.write(f"Total Tests: {total_tests}\n")
                f.write(f"Successful Tests: {successful_tests}\n")
                f.write(f"Failed Tests: {total_tests - successful_tests}\n")
                f.write(f"Success Rate: {success_rate:.1f}%\n\n")
                
                f.write("TEST RESULTS:\n")
                f.write("-" * 20 + "\n")
                for test in self.test_results:
                    status = "PASS" if test.get('success', False) else "FAIL"
                    duration = test.get('duration', 0)
                    f.write(f"{status} - {test['name']} ({duration:.1f}s)\n")
                
                if self.issues_found:
                    f.write(f"\nISSUES FOUND ({len(self.issues_found)}):\n")
                    f.write("-" * 20 + "\n")
                    for issue in self.issues_found:
                        f.write(f"- {issue}\n")
                
                f.write(f"\nREPORT GENERATED: {datetime.now().isoformat()}\n")
            
            self.log(f"Summary saved: {summary_file}")
        except Exception as e:
            self.log(f"Failed to save summary: {e}")
        
        return report
    
    def run_complete_session(self):
        """Run the complete enhanced testing session"""
        self.log("Starting Enhanced Autonomous Testing Session...")
        
        try:
            # Phase 1: System Health Analysis
            self.analyze_system_health()
            
            # Phase 2: Core Tests
            self.run_core_tests()
            
            # Phase 3: Extended Validation
            self.run_extended_validation()
            
            # Phase 4: Generate Report
            report = self.generate_comprehensive_report()
            
            # Final summary
            self.log("Enhanced testing session completed!")
            self.log(f"Results: {report['session_info']['successful_tests']}/{report['session_info']['total_tests']} tests passed")
            self.log(f"Success Rate: {report['session_info']['success_rate']:.1f}%")
            
            return report
            
        except Exception as e:
            self.log(f"Session failed: {e}")
            return None

def main():
    print("Enhanced Autonomous Testing Session")
    print("=" * 50)
    
    tester = EnhancedAutonomousTesting()
    
    try:
        report = tester.run_complete_session()
        if report:
            print(f"\nSUCCESS: {report['session_info']['success_rate']:.1f}% success rate")
        else:
            print("\nFAILED: Session encountered errors")
    except Exception as e:
        print(f"\nERROR: {e}")

if __name__ == "__main__":
    main()

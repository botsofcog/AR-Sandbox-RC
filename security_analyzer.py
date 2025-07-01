#!/usr/bin/env python3
"""
Security Analyzer - Comprehensive Security Assessment
Analyzes project for security vulnerabilities and suggests improvements
"""

import os
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path

class SecurityAnalyzer:
    def __init__(self):
        self.security_findings = []
        self.recommendations = []
        
        # Security patterns to check
        self.security_patterns = {
            'hardcoded_secrets': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
                r'private_key\s*=\s*["\'][^"\']+["\']'
            ],
            'sql_injection_risks': [
                r'execute\s*\(\s*["\'][^"\']*%[^"\']*["\']',
                r'query\s*\(\s*["\'][^"\']*\+[^"\']*["\']',
                r'SELECT\s+.*\+.*FROM',
                r'INSERT\s+.*\+.*VALUES'
            ],
            'xss_risks': [
                r'innerHTML\s*=\s*[^;]+\+',
                r'document\.write\s*\([^)]*\+',
                r'eval\s*\([^)]*\+',
                r'setTimeout\s*\([^)]*\+'
            ],
            'insecure_protocols': [
                r'http://(?!localhost|127\.0\.0\.1)',
                r'ftp://',
                r'telnet://'
            ]
        }
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[SEC {timestamp}] {message}")
        
    def scan_file_for_security_issues(self, file_path):
        """Scan individual file for security issues"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Check each security pattern category
                for category, patterns in self.security_patterns.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            issues.append({
                                'file': file_path,
                                'line': line_num,
                                'category': category,
                                'pattern': pattern,
                                'match': match.group()[:100],  # First 100 chars
                                'severity': self.get_severity(category)
                            })
                            
        except (OSError, PermissionError, UnicodeDecodeError):
            pass
            
        return issues
    
    def get_severity(self, category):
        """Get severity level for security category"""
        severity_map = {
            'hardcoded_secrets': 'high',
            'sql_injection_risks': 'high',
            'xss_risks': 'medium',
            'insecure_protocols': 'medium'
        }
        return severity_map.get(category, 'low')
    
    def analyze_file_permissions(self):
        """Analyze file permissions for security issues"""
        self.log("Analyzing file permissions...")
        
        permission_issues = []
        sensitive_files = []
        
        for root, dirs, files in os.walk('.'):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check for sensitive file types
                if any(pattern in file.lower() for pattern in [
                    '.key', '.pem', '.p12', '.pfx', '.env', 
                    'password', 'secret', 'token', 'credential'
                ]):
                    sensitive_files.append({
                        'path': file_path,
                        'type': 'sensitive_file',
                        'risk': 'medium'
                    })
                
                # Check for executable files in unexpected locations
                if file.endswith(('.exe', '.bat', '.sh', '.ps1')):
                    if not any(allowed in root for allowed in ['bin', 'scripts', 'tools']):
                        permission_issues.append({
                            'path': file_path,
                            'issue': 'executable_in_unexpected_location',
                            'risk': 'low'
                        })
        
        self.security_findings.append({
            'category': 'file_permissions',
            'sensitive_files': len(sensitive_files),
            'permission_issues': len(permission_issues),
            'details': {
                'sensitive_files': sensitive_files[:10],
                'permission_issues': permission_issues[:10]
            }
        })
        
        self.log(f"Found {len(sensitive_files)} sensitive files, {len(permission_issues)} permission issues")
    
    def analyze_dependencies_security(self):
        """Analyze dependencies for known security vulnerabilities"""
        self.log("Analyzing dependency security...")
        
        dependency_files = []
        
        # Check for dependency files
        dep_files = ['requirements.txt', 'package.json', 'Pipfile', 'yarn.lock', 'package-lock.json']
        
        for dep_file in dep_files:
            if os.path.exists(dep_file):
                dependency_files.append({
                    'file': dep_file,
                    'type': 'dependency_manifest',
                    'exists': True
                })
        
        # Check for outdated dependency patterns
        outdated_patterns = []
        
        if os.path.exists('requirements.txt'):
            try:
                with open('requirements.txt', 'r') as f:
                    content = f.read()
                    # Look for unpinned versions
                    unpinned = re.findall(r'^([^=<>!]+)(?![=<>!])', content, re.MULTILINE)
                    if unpinned:
                        outdated_patterns.append({
                            'file': 'requirements.txt',
                            'issue': 'unpinned_versions',
                            'count': len(unpinned),
                            'risk': 'medium'
                        })
            except:
                pass
        
        self.security_findings.append({
            'category': 'dependency_security',
            'dependency_files': len(dependency_files),
            'outdated_patterns': len(outdated_patterns),
            'details': {
                'files': dependency_files,
                'patterns': outdated_patterns
            }
        })
        
        self.log(f"Analyzed {len(dependency_files)} dependency files")
    
    def analyze_code_security(self):
        """Analyze code files for security vulnerabilities"""
        self.log("Analyzing code security...")
        
        all_issues = []
        files_scanned = 0
        
        # Scan code files
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith(('.py', '.js', '.html', '.php', '.java', '.cpp', '.c')):
                    file_path = os.path.join(root, file)
                    issues = self.scan_file_for_security_issues(file_path)
                    all_issues.extend(issues)
                    files_scanned += 1
        
        # Categorize issues by severity
        high_severity = [i for i in all_issues if i['severity'] == 'high']
        medium_severity = [i for i in all_issues if i['severity'] == 'medium']
        low_severity = [i for i in all_issues if i['severity'] == 'low']
        
        self.security_findings.append({
            'category': 'code_security',
            'files_scanned': files_scanned,
            'total_issues': len(all_issues),
            'high_severity': len(high_severity),
            'medium_severity': len(medium_severity),
            'low_severity': len(low_severity),
            'sample_issues': all_issues[:20]  # First 20 for reporting
        })
        
        self.log(f"Scanned {files_scanned} code files, found {len(all_issues)} potential security issues")
    
    def generate_security_recommendations(self):
        """Generate security improvement recommendations"""
        self.log("Generating security recommendations...")
        
        recommendations = []
        
        # Analyze findings and generate recommendations
        for finding in self.security_findings:
            category = finding['category']
            
            if category == 'code_security':
                if finding['high_severity'] > 0:
                    recommendations.append({
                        'priority': 'critical',
                        'category': 'code_security',
                        'title': f'Address {finding["high_severity"]} high-severity security issues',
                        'description': 'Found potential hardcoded secrets or SQL injection vulnerabilities',
                        'action': 'Review and fix high-severity security issues immediately'
                    })
                
                if finding['medium_severity'] > 5:
                    recommendations.append({
                        'priority': 'high',
                        'category': 'code_security',
                        'title': f'Review {finding["medium_severity"]} medium-severity security issues',
                        'description': 'Found potential XSS vulnerabilities or insecure protocols',
                        'action': 'Implement input validation and use secure protocols'
                    })
            
            elif category == 'file_permissions':
                if finding['sensitive_files'] > 0:
                    recommendations.append({
                        'priority': 'high',
                        'category': 'file_security',
                        'title': f'Secure {finding["sensitive_files"]} sensitive files',
                        'description': 'Found files that may contain sensitive information',
                        'action': 'Review file permissions and consider encryption'
                    })
            
            elif category == 'dependency_security':
                if finding['outdated_patterns']:
                    recommendations.append({
                        'priority': 'medium',
                        'category': 'dependency_security',
                        'title': 'Pin dependency versions',
                        'description': 'Found unpinned dependency versions',
                        'action': 'Pin all dependency versions to prevent supply chain attacks'
                    })
        
        # Add general security recommendations
        recommendations.extend([
            {
                'priority': 'medium',
                'category': 'general_security',
                'title': 'Implement security headers',
                'description': 'Add security headers to web applications',
                'action': 'Implement CSP, HSTS, and other security headers'
            },
            {
                'priority': 'low',
                'category': 'monitoring',
                'title': 'Set up security monitoring',
                'description': 'Implement security event logging and monitoring',
                'action': 'Add security logging and alerting systems'
            }
        ])
        
        self.recommendations = recommendations
        self.log(f"Generated {len(recommendations)} security recommendations")
    
    def save_security_report(self):
        """Save comprehensive security report"""
        self.log("Saving security report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report = {
            'scan_info': {
                'timestamp': datetime.now().isoformat(),
                'scan_type': 'comprehensive_security_analysis'
            },
            'findings': self.security_findings,
            'recommendations': self.recommendations,
            'summary': {
                'total_findings': len(self.security_findings),
                'total_recommendations': len(self.recommendations),
                'critical_issues': len([r for r in self.recommendations if r['priority'] == 'critical']),
                'high_priority_issues': len([r for r in self.recommendations if r['priority'] == 'high']),
                'medium_priority_issues': len([r for r in self.recommendations if r['priority'] == 'medium'])
            }
        }
        
        # Save JSON report
        json_file = f"security_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save text summary
        txt_file = f"SECURITY_SUMMARY_{timestamp}.txt"
        with open(txt_file, 'w') as f:
            f.write("SECURITY ANALYSIS REPORT\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            f.write("SECURITY FINDINGS:\n")
            f.write("-" * 20 + "\n")
            for finding in self.security_findings:
                f.write(f"- {finding['category']}: ")
                if 'total_issues' in finding:
                    f.write(f"{finding['total_issues']} issues found\n")
                elif 'sensitive_files' in finding:
                    f.write(f"{finding['sensitive_files']} sensitive files\n")
                else:
                    f.write("analyzed\n")
            
            f.write(f"\nSECURITY RECOMMENDATIONS:\n")
            f.write("-" * 30 + "\n")
            for rec in self.recommendations:
                f.write(f"[{rec['priority'].upper()}] {rec['title']}\n")
                f.write(f"  {rec['description']}\n")
                f.write(f"  Action: {rec['action']}\n\n")
        
        self.log(f"Security reports saved: {json_file}, {txt_file}")
        return report
    
    def run_security_analysis(self):
        """Run complete security analysis"""
        self.log("Starting comprehensive security analysis...")
        
        try:
            # Run all security analysis modules
            self.analyze_file_permissions()
            self.analyze_dependencies_security()
            self.analyze_code_security()
            
            # Generate recommendations
            self.generate_security_recommendations()
            
            # Save comprehensive report
            report = self.save_security_report()
            
            self.log("Security analysis completed successfully!")
            return report
            
        except Exception as e:
            self.log(f"Security analysis failed: {e}")
            return None

def main():
    print("SECURITY ANALYZER - COMPREHENSIVE SECURITY ASSESSMENT")
    print("=" * 70)
    print("Analyzing project for security vulnerabilities and risks...")
    print("=" * 70)
    
    analyzer = SecurityAnalyzer()
    
    try:
        report = analyzer.run_security_analysis()
        
        if report:
            print(f"\nSECURITY ANALYSIS COMPLETE!")
            print(f"Findings: {report['summary']['total_findings']}")
            print(f"Recommendations: {report['summary']['total_recommendations']}")
            print(f"Critical Issues: {report['summary']['critical_issues']}")
            print(f"High Priority: {report['summary']['high_priority_issues']}")
            print(f"Medium Priority: {report['summary']['medium_priority_issues']}")
        else:
            print("Security analysis failed to generate report")
            
    except KeyboardInterrupt:
        print("\nSecurity analysis stopped by user")
    except Exception as e:
        print(f"\nSecurity analysis failed: {e}")

if __name__ == "__main__":
    main()

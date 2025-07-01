#!/usr/bin/env python3
"""
Enhanced Continuous Optimizer - Fixed Encoding Issues
Never stops finding improvements while preserving all functionality
"""

import os
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path

class EnhancedContinuousOptimizer:
    def __init__(self):
        self.session_start = datetime.now()
        self.findings = []
        self.improvements = []
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        # Remove emojis for Windows compatibility
        clean_message = message.encode('ascii', 'ignore').decode('ascii')
        print(f"[{timestamp}] {clean_message}")
        
    def analyze_large_files(self):
        """Find large files that could be optimized"""
        self.log("Analyzing large files...")
        
        large_files = []
        total_size = 0
        
        for root, dirs, files in os.walk('.'):
            # Skip system directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    total_size += size
                    
                    # Files larger than 1MB
                    if size > 1024 * 1024:
                        large_files.append({
                            'path': file_path,
                            'size_mb': round(size / (1024 * 1024), 2),
                            'extension': Path(file).suffix.lower()
                        })
                except (OSError, PermissionError):
                    continue
        
        # Sort by size
        large_files.sort(key=lambda x: x['size_mb'], reverse=True)
        
        self.findings.append({
            'category': 'large_files',
            'count': len(large_files),
            'total_size_gb': round(total_size / (1024**3), 2),
            'top_10_large_files': large_files[:10]
        })
        
        self.log(f"Found {len(large_files)} files >1MB, total project size: {round(total_size / (1024**3), 2)}GB")
        
    def analyze_duplicate_patterns(self):
        """Find potential duplicate files and patterns"""
        self.log("Analyzing duplicate patterns...")
        
        file_patterns = {}
        potential_duplicates = []
        
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                # Group by filename patterns
                base_name = file.lower()
                
                # Look for versioned files (file_v1.txt, file_v2.txt, etc.)
                if '_v' in base_name or '_version' in base_name:
                    potential_duplicates.append(os.path.join(root, file))
                
                # Look for backup files
                if base_name.endswith(('.bak', '.backup', '.old', '.orig')):
                    potential_duplicates.append(os.path.join(root, file))
                
                # Group by extension
                ext = Path(file).suffix.lower()
                if ext not in file_patterns:
                    file_patterns[ext] = 0
                file_patterns[ext] += 1
        
        self.findings.append({
            'category': 'duplicate_patterns',
            'potential_duplicates': len(potential_duplicates),
            'file_type_distribution': dict(sorted(file_patterns.items(), key=lambda x: x[1], reverse=True)[:20])
        })
        
        self.log(f"Found {len(potential_duplicates)} potential duplicate/backup files")
        
    def analyze_code_metrics(self):
        """Analyze code quality metrics"""
        self.log("Analyzing code metrics...")
        
        code_stats = {
            'python': {'files': 0, 'lines': 0, 'with_docstrings': 0},
            'javascript': {'files': 0, 'lines': 0, 'with_comments': 0},
            'html': {'files': 0, 'lines': 0, 'with_doctype': 0},
            'css': {'files': 0, 'lines': 0},
            'json': {'files': 0, 'valid': 0}
        }
        
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = os.path.join(root, file)
                ext = Path(file).suffix.lower()
                
                try:
                    if ext == '.py':
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            code_stats['python']['files'] += 1
                            code_stats['python']['lines'] += len(content.split('\n'))
                            if '"""' in content or "'''" in content:
                                code_stats['python']['with_docstrings'] += 1
                                
                    elif ext == '.js':
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            code_stats['javascript']['files'] += 1
                            code_stats['javascript']['lines'] += len(content.split('\n'))
                            if '//' in content or '/*' in content:
                                code_stats['javascript']['with_comments'] += 1
                                
                    elif ext == '.html':
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            code_stats['html']['files'] += 1
                            code_stats['html']['lines'] += len(content.split('\n'))
                            if '<!DOCTYPE' in content:
                                code_stats['html']['with_doctype'] += 1
                                
                    elif ext == '.css':
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            code_stats['css']['files'] += 1
                            code_stats['css']['lines'] += len(content.split('\n'))
                            
                    elif ext == '.json':
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                json.load(f)
                                code_stats['json']['files'] += 1
                                code_stats['json']['valid'] += 1
                        except json.JSONDecodeError:
                            code_stats['json']['files'] += 1
                            
                except (OSError, PermissionError, UnicodeDecodeError):
                    continue
        
        self.findings.append({
            'category': 'code_metrics',
            'statistics': code_stats
        })
        
        total_files = sum(stats['files'] for stats in code_stats.values())
        total_lines = sum(stats.get('lines', 0) for stats in code_stats.values())
        
        self.log(f"Code analysis: {total_files} code files, {total_lines} total lines")
        
    def analyze_test_coverage(self):
        """Analyze test coverage and suggest improvements"""
        self.log("Analyzing test coverage...")
        
        test_files = []
        source_files = []
        
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                if file.startswith('test_') or file.endswith('_test.py') or 'test' in file.lower():
                    test_files.append(file_path)
                elif file.endswith(('.py', '.js')):
                    source_files.append(file_path)
        
        test_coverage_ratio = len(test_files) / max(1, len(source_files))
        
        self.findings.append({
            'category': 'test_coverage',
            'test_files': len(test_files),
            'source_files': len(source_files),
            'coverage_ratio': round(test_coverage_ratio, 3),
            'coverage_percentage': round(test_coverage_ratio * 100, 1)
        })
        
        self.log(f"Test coverage: {len(test_files)} test files for {len(source_files)} source files ({round(test_coverage_ratio * 100, 1)}%)")
        
    def analyze_documentation_quality(self):
        """Analyze documentation completeness"""
        self.log("Analyzing documentation quality...")
        
        doc_files = []
        readme_files = []
        
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    doc_files.append(file_path)
                    
                    if file.lower().startswith('readme'):
                        readme_files.append(file_path)
        
        # Analyze README quality
        main_readme_exists = os.path.exists('README.md')
        main_readme_size = 0
        
        if main_readme_exists:
            try:
                main_readme_size = os.path.getsize('README.md')
            except:
                pass
        
        self.findings.append({
            'category': 'documentation',
            'total_md_files': len(doc_files),
            'readme_files': len(readme_files),
            'main_readme_exists': main_readme_exists,
            'main_readme_size_kb': round(main_readme_size / 1024, 1)
        })
        
        self.log(f"Documentation: {len(doc_files)} markdown files, main README: {main_readme_size/1024:.1f}KB")
        
    def generate_improvement_suggestions(self):
        """Generate actionable improvement suggestions"""
        self.log("Generating improvement suggestions...")
        
        suggestions = []
        
        # Analyze findings and generate suggestions
        for finding in self.findings:
            category = finding['category']
            
            if category == 'large_files' and finding['count'] > 0:
                suggestions.append({
                    'priority': 'medium',
                    'category': 'performance',
                    'title': f'Optimize {finding["count"]} large files',
                    'description': f'Found {finding["count"]} files >1MB that could be compressed or optimized',
                    'safe': True
                })
            
            if category == 'duplicate_patterns' and finding['potential_duplicates'] > 0:
                suggestions.append({
                    'priority': 'low',
                    'category': 'cleanup',
                    'title': f'Review {finding["potential_duplicates"]} potential duplicate files',
                    'description': 'Consider archiving or removing backup/versioned files',
                    'safe': True
                })
            
            if category == 'code_metrics':
                stats = finding['statistics']
                if stats['python']['files'] > 0:
                    docstring_ratio = stats['python']['with_docstrings'] / stats['python']['files']
                    if docstring_ratio < 0.8:
                        suggestions.append({
                            'priority': 'medium',
                            'category': 'documentation',
                            'title': 'Improve Python docstring coverage',
                            'description': f'Only {docstring_ratio*100:.1f}% of Python files have docstrings',
                            'safe': True
                        })
            
            if category == 'test_coverage':
                if finding['coverage_percentage'] < 50:
                    suggestions.append({
                        'priority': 'high',
                        'category': 'testing',
                        'title': 'Increase test coverage',
                        'description': f'Current test coverage is {finding["coverage_percentage"]}% - consider adding more tests',
                        'safe': True
                    })
        
        self.improvements = suggestions
        self.log(f"Generated {len(suggestions)} improvement suggestions")
        
    def save_optimization_report(self):
        """Save comprehensive optimization report"""
        self.log("Saving optimization report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report = {
            'session_info': {
                'start_time': self.session_start.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_minutes': round((datetime.now() - self.session_start).total_seconds() / 60, 2)
            },
            'findings': self.findings,
            'improvement_suggestions': self.improvements,
            'summary': {
                'total_findings': len(self.findings),
                'total_suggestions': len(self.improvements),
                'high_priority_suggestions': len([s for s in self.improvements if s['priority'] == 'high']),
                'medium_priority_suggestions': len([s for s in self.improvements if s['priority'] == 'medium']),
                'low_priority_suggestions': len([s for s in self.improvements if s['priority'] == 'low'])
            }
        }
        
        # Save JSON report
        json_file = f"optimization_report_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=True)
        
        # Save text summary
        txt_file = f"OPTIMIZATION_SUMMARY_{timestamp}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("CONTINUOUS OPTIMIZATION REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Duration: {report['session_info']['duration_minutes']} minutes\n\n")
            
            f.write("FINDINGS SUMMARY:\n")
            f.write("-" * 20 + "\n")
            for finding in self.findings:
                f.write(f"- {finding['category']}: ")
                if finding['category'] == 'large_files':
                    f.write(f"{finding['count']} files, {finding['total_size_gb']}GB total\n")
                elif finding['category'] == 'code_metrics':
                    stats = finding['statistics']
                    f.write(f"Python: {stats['python']['files']} files, JS: {stats['javascript']['files']} files\n")
                elif finding['category'] == 'test_coverage':
                    f.write(f"{finding['coverage_percentage']}% coverage\n")
                else:
                    f.write("analyzed\n")
            
            f.write(f"\nIMPROVEMENT SUGGESTIONS ({len(self.improvements)}):\n")
            f.write("-" * 30 + "\n")
            for suggestion in self.improvements:
                f.write(f"[{suggestion['priority'].upper()}] {suggestion['title']}\n")
                f.write(f"  {suggestion['description']}\n\n")
        
        self.log(f"Reports saved: {json_file}, {txt_file}")
        return report
        
    def run_optimization_cycle(self):
        """Run complete optimization analysis cycle"""
        self.log("Starting optimization analysis cycle...")
        
        try:
            # Run all analysis modules
            self.analyze_large_files()
            self.analyze_duplicate_patterns()
            self.analyze_code_metrics()
            self.analyze_test_coverage()
            self.analyze_documentation_quality()
            
            # Generate suggestions
            self.generate_improvement_suggestions()
            
            # Save comprehensive report
            report = self.save_optimization_report()
            
            self.log("Optimization cycle completed successfully!")
            return report
            
        except Exception as e:
            self.log(f"Optimization cycle failed: {e}")
            return None

def main():
    print("ENHANCED CONTINUOUS OPTIMIZER")
    print("=" * 50)
    print("Analyzing project for optimization opportunities...")
    print("Safe mode: No changes will be made to existing files")
    print("=" * 50)
    
    optimizer = EnhancedContinuousOptimizer()
    
    try:
        report = optimizer.run_optimization_cycle()
        
        if report:
            print(f"\nOPTIMIZATION ANALYSIS COMPLETE!")
            print(f"Duration: {report['session_info']['duration_minutes']} minutes")
            print(f"Findings: {report['summary']['total_findings']}")
            print(f"Suggestions: {report['summary']['total_suggestions']}")
            print(f"High Priority: {report['summary']['high_priority_suggestions']}")
            print(f"Medium Priority: {report['summary']['medium_priority_suggestions']}")
            print(f"Low Priority: {report['summary']['low_priority_suggestions']}")
        else:
            print("Optimization analysis encountered issues")
            
    except KeyboardInterrupt:
        print("\nOptimization stopped by user")
    except Exception as e:
        print(f"\nOptimization failed: {e}")

if __name__ == "__main__":
    main()

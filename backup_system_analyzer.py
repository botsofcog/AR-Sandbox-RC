#!/usr/bin/env python3
"""
Backup System Analyzer - Comprehensive Backup Strategy Assessment
Analyzes backup needs and creates backup recommendations
"""

import os
import shutil
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path

class BackupSystemAnalyzer:
    def __init__(self):
        self.backup_analysis = {}
        self.recommendations = []
        self.critical_files = []
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[BACKUP {timestamp}] {message}")
        
    def identify_critical_files(self):
        """Identify files that are critical for backup"""
        self.log("Identifying critical files...")
        
        critical_patterns = [
            # Configuration files
            ('config', ['.json', '.yaml', '.yml', '.ini', '.conf', '.cfg']),
            # Source code
            ('source_code', ['.py', '.js', '.html', '.css', '.cpp', '.java', '.c']),
            # Documentation
            ('documentation', ['.md', '.txt', '.rst', '.doc', '.docx']),
            # Data files
            ('data', ['.csv', '.xlsx', '.db', '.sqlite', '.sql']),
            # Project files
            ('project', ['requirements.txt', 'package.json', 'Makefile', 'Dockerfile']),
            # Assets
            ('assets', ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico'])
        ]
        
        file_categories = {category: [] for category, _ in critical_patterns}
        total_size_by_category = {category: 0 for category, _ in critical_patterns}
        
        for root, dirs, files in os.walk('.'):
            # Skip hidden and cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = Path(file).suffix.lower()
                file_name = file.lower()
                
                try:
                    file_size = os.path.getsize(file_path)
                    
                    # Categorize file
                    categorized = False
                    for category, extensions in critical_patterns:
                        if file_ext in extensions or any(pattern in file_name for pattern in extensions if not pattern.startswith('.')):
                            file_categories[category].append({
                                'path': file_path,
                                'size': file_size,
                                'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                            })
                            total_size_by_category[category] += file_size
                            categorized = True
                            break
                    
                    # Mark as critical if it's a key project file
                    if not categorized and any(key in file_name for key in [
                        'readme', 'license', 'changelog', 'version', 'setup'
                    ]):
                        file_categories['project'].append({
                            'path': file_path,
                            'size': file_size,
                            'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                        })
                        total_size_by_category['project'] += file_size
                        
                except (OSError, PermissionError):
                    continue
        
        self.backup_analysis['file_categories'] = file_categories
        self.backup_analysis['size_by_category'] = {
            category: round(size / (1024**2), 2) for category, size in total_size_by_category.items()
        }
        
        # Identify most critical files
        self.critical_files = []
        for category, files in file_categories.items():
            if category in ['source_code', 'config', 'project']:
                self.critical_files.extend(files[:10])  # Top 10 per critical category
        
        total_critical_size = sum(f['size'] for f in self.critical_files)
        
        self.log(f"Identified {len(self.critical_files)} critical files ({total_critical_size/(1024**2):.1f}MB)")
        
    def analyze_backup_frequency_needs(self):
        """Analyze how frequently different files change"""
        self.log("Analyzing backup frequency needs...")
        
        change_analysis = {
            'recently_modified': [],
            'frequently_changing': [],
            'stable_files': []
        }
        
        now = datetime.now()
        recent_threshold = now - timedelta(days=7)
        old_threshold = now - timedelta(days=30)
        
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    file_size = os.path.getsize(file_path)
                    
                    file_info = {
                        'path': file_path,
                        'size': file_size,
                        'last_modified': mtime.isoformat(),
                        'days_since_modified': (now - mtime).days
                    }
                    
                    if mtime > recent_threshold:
                        change_analysis['recently_modified'].append(file_info)
                    elif mtime < old_threshold:
                        change_analysis['stable_files'].append(file_info)
                    else:
                        change_analysis['frequently_changing'].append(file_info)
                        
                except (OSError, PermissionError):
                    continue
        
        # Sort by modification time
        for category in change_analysis:
            change_analysis[category].sort(key=lambda x: x['last_modified'], reverse=True)
            change_analysis[category] = change_analysis[category][:20]  # Top 20 per category
        
        self.backup_analysis['change_patterns'] = {
            'recently_modified_count': len(change_analysis['recently_modified']),
            'frequently_changing_count': len(change_analysis['frequently_changing']),
            'stable_files_count': len(change_analysis['stable_files']),
            'details': change_analysis
        }
        
        self.log(f"Change analysis: {len(change_analysis['recently_modified'])} recent, "
                f"{len(change_analysis['frequently_changing'])} frequent, "
                f"{len(change_analysis['stable_files'])} stable")
        
    def analyze_storage_requirements(self):
        """Analyze storage requirements for backup"""
        self.log("Analyzing storage requirements...")
        
        total_size = 0
        file_count = 0
        large_files = []
        
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                try:
                    size = os.path.getsize(file_path)
                    total_size += size
                    file_count += 1
                    
                    # Track large files (>10MB)
                    if size > 10 * 1024 * 1024:
                        large_files.append({
                            'path': file_path,
                            'size_mb': round(size / (1024**2), 2)
                        })
                        
                except (OSError, PermissionError):
                    continue
        
        # Sort large files by size
        large_files.sort(key=lambda x: x['size_mb'], reverse=True)
        
        self.backup_analysis['storage_requirements'] = {
            'total_size_gb': round(total_size / (1024**3), 2),
            'total_files': file_count,
            'large_files_count': len(large_files),
            'large_files': large_files[:10],  # Top 10 largest
            'estimated_compressed_size_gb': round((total_size * 0.7) / (1024**3), 2),  # Assume 30% compression
            'recommended_backup_storage_gb': round((total_size * 1.5) / (1024**3), 2)  # 50% overhead
        }
        
        self.log(f"Storage analysis: {total_size/(1024**3):.2f}GB total, {file_count} files")
        
    def generate_backup_strategy(self):
        """Generate comprehensive backup strategy recommendations"""
        self.log("Generating backup strategy...")
        
        strategies = []
        
        # Critical files backup strategy
        critical_size = sum(f['size'] for f in self.critical_files) / (1024**2)
        if critical_size < 100:  # Less than 100MB
            strategies.append({
                'type': 'critical_files_daily',
                'priority': 'high',
                'description': f'Daily backup of {len(self.critical_files)} critical files ({critical_size:.1f}MB)',
                'frequency': 'daily',
                'retention': '30 days',
                'storage_needed_mb': critical_size * 30
            })
        
        # Full project backup strategy
        total_size_gb = self.backup_analysis['storage_requirements']['total_size_gb']
        if total_size_gb < 10:  # Less than 10GB
            strategies.append({
                'type': 'full_project_weekly',
                'priority': 'medium',
                'description': f'Weekly full project backup ({total_size_gb:.1f}GB)',
                'frequency': 'weekly',
                'retention': '12 weeks',
                'storage_needed_gb': total_size_gb * 12
            })
        else:
            strategies.append({
                'type': 'incremental_backup',
                'priority': 'medium',
                'description': f'Incremental backup for large project ({total_size_gb:.1f}GB)',
                'frequency': 'daily incremental, weekly full',
                'retention': '4 weeks incremental, 12 weeks full',
                'storage_needed_gb': total_size_gb * 4
            })
        
        # Archive strategy for stable files
        stable_count = self.backup_analysis['change_patterns']['stable_files_count']
        if stable_count > 100:
            strategies.append({
                'type': 'archive_stable_files',
                'priority': 'low',
                'description': f'Archive {stable_count} stable files (unchanged >30 days)',
                'frequency': 'monthly',
                'retention': 'permanent',
                'storage_needed_gb': total_size_gb * 0.3  # Estimate 30% are stable
            })
        
        self.backup_analysis['backup_strategies'] = strategies
        
        # Generate specific recommendations
        recommendations = []
        
        recommendations.append({
            'category': 'backup_frequency',
            'priority': 'high',
            'title': 'Implement daily critical file backup',
            'description': f'Backup {len(self.critical_files)} critical files daily',
            'implementation': 'Use automated script to backup source code, config, and project files'
        })
        
        recommendations.append({
            'category': 'backup_storage',
            'priority': 'medium',
            'title': f'Allocate {self.backup_analysis["storage_requirements"]["recommended_backup_storage_gb"]:.1f}GB backup storage',
            'description': 'Ensure adequate storage for backup retention',
            'implementation': 'Set up cloud storage or external drive with sufficient capacity'
        })
        
        if len(self.backup_analysis['storage_requirements']['large_files']) > 0:
            recommendations.append({
                'category': 'large_file_strategy',
                'priority': 'medium',
                'title': f'Special handling for {len(self.backup_analysis["storage_requirements"]["large_files"])} large files',
                'description': 'Large files may need different backup strategy',
                'implementation': 'Consider compression or separate archive for large files'
            })
        
        self.recommendations = recommendations
        
        self.log(f"Generated {len(strategies)} backup strategies and {len(recommendations)} recommendations")
        
    def save_backup_analysis_report(self):
        """Save comprehensive backup analysis report"""
        self.log("Saving backup analysis report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report = {
            'analysis_info': {
                'timestamp': datetime.now().isoformat(),
                'analysis_type': 'comprehensive_backup_assessment'
            },
            'backup_analysis': self.backup_analysis,
            'recommendations': self.recommendations,
            'summary': {
                'total_files_analyzed': self.backup_analysis['storage_requirements']['total_files'],
                'total_size_gb': self.backup_analysis['storage_requirements']['total_size_gb'],
                'critical_files_count': len(self.critical_files),
                'backup_strategies': len(self.backup_analysis['backup_strategies']),
                'recommendations_count': len(self.recommendations)
            }
        }
        
        # Save JSON report
        json_file = f"backup_analysis_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save text summary
        txt_file = f"BACKUP_ANALYSIS_SUMMARY_{timestamp}.txt"
        with open(txt_file, 'w') as f:
            f.write("BACKUP SYSTEM ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            f.write("PROJECT OVERVIEW:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total Size: {report['summary']['total_size_gb']:.2f}GB\n")
            f.write(f"Total Files: {report['summary']['total_files_analyzed']:,}\n")
            f.write(f"Critical Files: {report['summary']['critical_files_count']}\n\n")
            
            f.write("BACKUP STRATEGIES:\n")
            f.write("-" * 20 + "\n")
            for strategy in self.backup_analysis['backup_strategies']:
                f.write(f"[{strategy['priority'].upper()}] {strategy['type']}\n")
                f.write(f"  {strategy['description']}\n")
                f.write(f"  Frequency: {strategy['frequency']}\n")
                f.write(f"  Retention: {strategy['retention']}\n\n")
            
            f.write("RECOMMENDATIONS:\n")
            f.write("-" * 20 + "\n")
            for rec in self.recommendations:
                f.write(f"[{rec['priority'].upper()}] {rec['title']}\n")
                f.write(f"  {rec['description']}\n")
                f.write(f"  Implementation: {rec['implementation']}\n\n")
        
        self.log(f"Backup analysis reports saved: {json_file}, {txt_file}")
        return report
        
    def run_backup_analysis(self):
        """Run complete backup system analysis"""
        self.log("Starting comprehensive backup system analysis...")
        
        try:
            # Run all backup analysis modules
            self.identify_critical_files()
            self.analyze_backup_frequency_needs()
            self.analyze_storage_requirements()
            self.generate_backup_strategy()
            
            # Save comprehensive report
            report = self.save_backup_analysis_report()
            
            self.log("Backup analysis completed successfully!")
            return report
            
        except Exception as e:
            self.log(f"Backup analysis failed: {e}")
            return None

def main():
    print("BACKUP SYSTEM ANALYZER - COMPREHENSIVE BACKUP ASSESSMENT")
    print("=" * 80)
    print("Analyzing backup needs and creating backup strategy recommendations...")
    print("=" * 80)
    
    analyzer = BackupSystemAnalyzer()
    
    try:
        report = analyzer.run_backup_analysis()
        
        if report:
            print(f"\nBACKUP ANALYSIS COMPLETE!")
            print(f"Total Size: {report['summary']['total_size_gb']:.2f}GB")
            print(f"Total Files: {report['summary']['total_files_analyzed']:,}")
            print(f"Critical Files: {report['summary']['critical_files_count']}")
            print(f"Backup Strategies: {report['summary']['backup_strategies']}")
            print(f"Recommendations: {report['summary']['recommendations_count']}")
        else:
            print("Backup analysis failed to generate report")
            
    except KeyboardInterrupt:
        print("\nBackup analysis stopped by user")
    except Exception as e:
        print(f"\nBackup analysis failed: {e}")

if __name__ == "__main__":
    main()

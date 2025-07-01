#!/usr/bin/env python3
"""
Scalability Testing Suite for AR Sandbox RC
Tests system performance under various load conditions
"""

import asyncio
import json
import logging
import time
import psutil
import websockets
import aiohttp
import concurrent.futures
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScalabilityTester:
    def __init__(self):
        self.test_results = []
        self.performance_baseline = None
        self.load_test_scenarios = [
            {'name': 'Light Load', 'concurrent_users': 10, 'duration': 60},
            {'name': 'Medium Load', 'concurrent_users': 50, 'duration': 120},
            {'name': 'Heavy Load', 'concurrent_users': 100, 'duration': 180},
            {'name': 'Peak Load', 'concurrent_users': 250, 'duration': 300},
            {'name': 'Stress Test', 'concurrent_users': 500, 'duration': 600},
            {'name': 'Extreme Load', 'concurrent_users': 1000, 'duration': 300}
        ]
        
        self.endpoints = {
            'frontend': 'http://localhost:8080',
            'depth_server': 'ws://localhost:8765',
            'telemetry_server': 'ws://localhost:8766',
            'streaming_server': 'http://localhost:8767',
            'analytics_dashboard': 'http://localhost:8768'
        }
        
        # Performance targets for 100% scalability
        self.performance_targets = {
            'response_time_p95': 200,    # 95th percentile < 200ms
            'response_time_p99': 500,    # 99th percentile < 500ms
            'error_rate': 0.01,          # < 1% error rate
            'throughput_min': 100,       # > 100 requests/second
            'cpu_usage_max': 85,         # < 85% CPU usage
            'memory_usage_max': 90,      # < 90% memory usage
            'concurrent_users_max': 1000 # Support 1000+ concurrent users
        }
    
    async def run_scalability_tests(self) -> Dict[str, Any]:
        """Run comprehensive scalability test suite"""
        logger.info("🚀 Starting scalability testing suite...")
        
        # Establish performance baseline
        await self.establish_baseline()
        
        # Run load test scenarios
        for scenario in self.load_test_scenarios:
            logger.info(f"🔄 Running {scenario['name']} scenario...")
            result = await self.run_load_test_scenario(scenario)
            self.test_results.append(result)
            
            # Brief cooldown between tests
            await asyncio.sleep(30)
        
        # Generate comprehensive report
        report = self.generate_scalability_report()
        
        # Save results
        self.save_test_results(report)
        
        return report
    
    async def establish_baseline(self):
        """Establish performance baseline with no load"""
        logger.info("📊 Establishing performance baseline...")
        
        baseline_metrics = []
        
        # Collect baseline metrics over 60 seconds
        for _ in range(12):  # 12 samples over 60 seconds
            start_time = time.time()
            
            # Test each endpoint
            endpoint_metrics = {}
            for name, url in self.endpoints.items():
                try:
                    if url.startswith('ws://'):
                        response_time = await self.test_websocket_endpoint(url)
                    else:
                        response_time = await self.test_http_endpoint(url)
                    
                    endpoint_metrics[name] = {
                        'response_time': response_time,
                        'success': True
                    }
                except Exception as e:
                    endpoint_metrics[name] = {
                        'response_time': -1,
                        'success': False,
                        'error': str(e)
                    }
            
            # Collect system metrics
            system_metrics = {
                'cpu_usage': psutil.cpu_percent(interval=1),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_io': psutil.net_io_counters()._asdict()
            }
            
            baseline_metrics.append({
                'timestamp': datetime.now().isoformat(),
                'endpoints': endpoint_metrics,
                'system': system_metrics
            })
            
            await asyncio.sleep(5)
        
        self.performance_baseline = {
            'metrics': baseline_metrics,
            'avg_response_time': statistics.mean([
                m['endpoints'][name]['response_time'] 
                for m in baseline_metrics 
                for name in self.endpoints.keys()
                if m['endpoints'][name]['success']
            ]),
            'avg_cpu_usage': statistics.mean([m['system']['cpu_usage'] for m in baseline_metrics]),
            'avg_memory_usage': statistics.mean([m['system']['memory_usage'] for m in baseline_metrics])
        }
        
        logger.info(f"✅ Baseline established: {self.performance_baseline['avg_response_time']:.1f}ms avg response time")
    
    async def run_load_test_scenario(self, scenario: Dict) -> Dict[str, Any]:
        """Run a specific load test scenario"""
        concurrent_users = scenario['concurrent_users']
        duration = scenario['duration']
        
        logger.info(f"🔥 Testing {concurrent_users} concurrent users for {duration} seconds...")
        
        start_time = time.time()
        end_time = start_time + duration
        
        # Metrics collection
        response_times = []
        error_count = 0
        success_count = 0
        system_metrics = []
        
        # Create semaphore to limit concurrent connections
        semaphore = asyncio.Semaphore(concurrent_users)
        
        async def user_simulation():
            """Simulate a single user session"""
            nonlocal response_times, error_count, success_count
            
            async with semaphore:
                while time.time() < end_time:
                    try:
                        # Random endpoint selection
                        endpoint_name = list(self.endpoints.keys())[
                            int(time.time() * 1000) % len(self.endpoints)
                        ]
                        endpoint_url = self.endpoints[endpoint_name]
                        
                        # Test endpoint
                        if endpoint_url.startswith('ws://'):
                            response_time = await self.test_websocket_endpoint(endpoint_url)
                        else:
                            response_time = await self.test_http_endpoint(endpoint_url)
                        
                        response_times.append(response_time)
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        logger.debug(f"User simulation error: {e}")
                    
                    # Random delay between requests (0.1 to 2 seconds)
                    await asyncio.sleep(0.1 + (time.time() * 1000 % 19) / 10)
        
        # Start user simulations
        user_tasks = [asyncio.create_task(user_simulation()) for _ in range(concurrent_users)]
        
        # System monitoring during load test
        async def system_monitor():
            while time.time() < end_time:
                metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'cpu_usage': psutil.cpu_percent(interval=1),
                    'memory_usage': psutil.virtual_memory().percent,
                    'disk_usage': psutil.disk_usage('/').percent,
                    'network_io': psutil.net_io_counters()._asdict(),
                    'active_connections': len([task for task in user_tasks if not task.done()])
                }
                system_metrics.append(metrics)
                await asyncio.sleep(5)
        
        # Run load test and monitoring
        monitor_task = asyncio.create_task(system_monitor())
        
        try:
            await asyncio.gather(*user_tasks, monitor_task, return_exceptions=True)
        except Exception as e:
            logger.error(f"Load test error: {e}")
        
        # Calculate results
        total_requests = success_count + error_count
        test_duration = time.time() - start_time
        
        if response_times:
            response_times.sort()
            p50 = response_times[len(response_times) // 2]
            p95 = response_times[int(len(response_times) * 0.95)]
            p99 = response_times[int(len(response_times) * 0.99)]
            avg_response_time = statistics.mean(response_times)
        else:
            p50 = p95 = p99 = avg_response_time = 0
        
        # System performance during test
        if system_metrics:
            avg_cpu = statistics.mean([m['cpu_usage'] for m in system_metrics])
            max_cpu = max([m['cpu_usage'] for m in system_metrics])
            avg_memory = statistics.mean([m['memory_usage'] for m in system_metrics])
            max_memory = max([m['memory_usage'] for m in system_metrics])
        else:
            avg_cpu = max_cpu = avg_memory = max_memory = 0
        
        result = {
            'scenario': scenario,
            'duration': test_duration,
            'total_requests': total_requests,
            'successful_requests': success_count,
            'failed_requests': error_count,
            'error_rate': error_count / total_requests if total_requests > 0 else 0,
            'throughput': total_requests / test_duration,
            'response_times': {
                'average': avg_response_time,
                'p50': p50,
                'p95': p95,
                'p99': p99,
                'min': min(response_times) if response_times else 0,
                'max': max(response_times) if response_times else 0
            },
            'system_performance': {
                'avg_cpu_usage': avg_cpu,
                'max_cpu_usage': max_cpu,
                'avg_memory_usage': avg_memory,
                'max_memory_usage': max_memory
            },
            'performance_score': self.calculate_performance_score(
                p95, error_count / total_requests if total_requests > 0 else 0, 
                total_requests / test_duration, max_cpu, max_memory
            )
        }
        
        logger.info(f"✅ {scenario['name']} completed: "
                   f"{success_count}/{total_requests} requests successful, "
                   f"P95: {p95:.1f}ms, "
                   f"Error rate: {result['error_rate']:.2%}")
        
        return result
    
    async def test_http_endpoint(self, url: str) -> float:
        """Test HTTP endpoint and return response time"""
        start_time = time.time()
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(url) as response:
                await response.read()
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
        
        return (time.time() - start_time) * 1000  # Convert to milliseconds
    
    async def test_websocket_endpoint(self, url: str) -> float:
        """Test WebSocket endpoint and return response time"""
        start_time = time.time()
        
        async with websockets.connect(url, timeout=10) as websocket:
            await websocket.ping()
        
        return (time.time() - start_time) * 1000  # Convert to milliseconds
    
    def calculate_performance_score(self, p95_response_time: float, error_rate: float, 
                                  throughput: float, max_cpu: float, max_memory: float) -> float:
        """Calculate overall performance score (0-100)"""
        score = 100
        
        # Response time penalty
        if p95_response_time > self.performance_targets['response_time_p95']:
            score -= min(30, (p95_response_time - self.performance_targets['response_time_p95']) / 10)
        
        # Error rate penalty
        if error_rate > self.performance_targets['error_rate']:
            score -= min(40, (error_rate - self.performance_targets['error_rate']) * 1000)
        
        # Throughput bonus/penalty
        if throughput < self.performance_targets['throughput_min']:
            score -= min(20, (self.performance_targets['throughput_min'] - throughput) / 5)
        
        # Resource usage penalty
        if max_cpu > self.performance_targets['cpu_usage_max']:
            score -= min(15, (max_cpu - self.performance_targets['cpu_usage_max']) / 2)
        
        if max_memory > self.performance_targets['memory_usage_max']:
            score -= min(15, (max_memory - self.performance_targets['memory_usage_max']) / 2)
        
        return max(0, score)
    
    def generate_scalability_report(self) -> Dict[str, Any]:
        """Generate comprehensive scalability report"""
        if not self.test_results:
            return {'error': 'No test results available'}
        
        # Overall performance analysis
        avg_performance_score = statistics.mean([r['performance_score'] for r in self.test_results])
        max_concurrent_users = max([r['scenario']['concurrent_users'] for r in self.test_results 
                                  if r['performance_score'] >= 70])  # 70% threshold for acceptable performance
        
        # Best and worst performing scenarios
        best_scenario = max(self.test_results, key=lambda x: x['performance_score'])
        worst_scenario = min(self.test_results, key=lambda x: x['performance_score'])
        
        # Scalability assessment
        scalability_grade = self.assess_scalability_grade(avg_performance_score, max_concurrent_users)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'test_summary': {
                'total_scenarios': len(self.test_results),
                'avg_performance_score': avg_performance_score,
                'max_supported_users': max_concurrent_users,
                'scalability_grade': scalability_grade,
                'meets_targets': max_concurrent_users >= self.performance_targets['concurrent_users_max']
            },
            'performance_baseline': self.performance_baseline,
            'test_results': self.test_results,
            'best_scenario': best_scenario,
            'worst_scenario': worst_scenario,
            'performance_targets': self.performance_targets,
            'recommendations': self.generate_recommendations(avg_performance_score, max_concurrent_users)
        }
        
        return report
    
    def assess_scalability_grade(self, avg_score: float, max_users: int) -> str:
        """Assess overall scalability grade"""
        if avg_score >= 90 and max_users >= 1000:
            return 'A+ (Excellent)'
        elif avg_score >= 80 and max_users >= 500:
            return 'A (Very Good)'
        elif avg_score >= 70 and max_users >= 250:
            return 'B (Good)'
        elif avg_score >= 60 and max_users >= 100:
            return 'C (Acceptable)'
        else:
            return 'D (Needs Improvement)'
    
    def generate_recommendations(self, avg_score: float, max_users: int) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        if avg_score < 80:
            recommendations.append("🔧 Optimize application performance to improve response times")
        
        if max_users < 500:
            recommendations.append("⚡ Implement horizontal scaling to support more concurrent users")
        
        # Analyze specific bottlenecks
        high_cpu_scenarios = [r for r in self.test_results 
                            if r['system_performance']['max_cpu_usage'] > 80]
        if high_cpu_scenarios:
            recommendations.append("🖥️ Optimize CPU-intensive operations or add more CPU cores")
        
        high_memory_scenarios = [r for r in self.test_results 
                               if r['system_performance']['max_memory_usage'] > 85]
        if high_memory_scenarios:
            recommendations.append("💾 Optimize memory usage or increase available RAM")
        
        slow_response_scenarios = [r for r in self.test_results 
                                 if r['response_times']['p95'] > 200]
        if slow_response_scenarios:
            recommendations.append("🚀 Implement caching and optimize database queries")
        
        if not recommendations:
            recommendations.append("✅ System performance is excellent - no immediate optimizations needed")
        
        return recommendations
    
    def save_test_results(self, report: Dict[str, Any]):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scalability_test_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📄 Scalability test report saved: {filename}")

async def main():
    """Main entry point"""
    print("⚡ AR Sandbox RC - Scalability Testing Suite")
    print("=" * 60)
    print("Testing system performance under various load conditions")
    print("=" * 60)
    
    tester = ScalabilityTester()
    
    try:
        report = await tester.run_scalability_tests()
        
        print(f"\n🏆 SCALABILITY TEST RESULTS:")
        print(f"Average Performance Score: {report['test_summary']['avg_performance_score']:.1f}/100")
        print(f"Max Supported Users: {report['test_summary']['max_supported_users']}")
        print(f"Scalability Grade: {report['test_summary']['scalability_grade']}")
        print(f"Meets 1000+ User Target: {'✅ YES' if report['test_summary']['meets_targets'] else '❌ NO'}")
        
        print(f"\n📋 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"  {rec}")
        
    except KeyboardInterrupt:
        print("\n🛑 Scalability testing stopped by user")
    except Exception as e:
        print(f"\n❌ Scalability testing failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())

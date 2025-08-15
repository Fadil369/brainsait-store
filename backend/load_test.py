#!/usr/bin/env python3
"""
Load testing script for BrainSAIT Store API
Tests critical endpoints under various load conditions
"""

import asyncio
import aiohttp
import time
import json
import statistics
from typing import List, Dict, Any
from dataclasses import dataclass
import argparse

@dataclass
class TestResult:
    endpoint: str
    method: str
    status_code: int
    response_time: float
    success: bool
    error: str = None

class LoadTester:
    def __init__(self, base_url: str, concurrent_users: int = 10):
        self.base_url = base_url.rstrip('/')
        self.concurrent_users = concurrent_users
        self.results: List[TestResult] = []
        
    async def make_request(self, session: aiohttp.ClientSession, method: str, endpoint: str, **kwargs) -> TestResult:
        """Make a single HTTP request and record metrics"""
        start_time = time.time()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with session.request(method, url, **kwargs) as response:
                response_time = time.time() - start_time
                
                # Read response to ensure full request completion
                await response.text()
                
                return TestResult(
                    endpoint=endpoint,
                    method=method,
                    status_code=response.status,
                    response_time=response_time,
                    success=200 <= response.status < 400
                )
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                endpoint=endpoint,
                method=method,
                status_code=0,
                response_time=response_time,
                success=False,
                error=str(e)
            )
    
    async def user_workflow(self, session: aiohttp.ClientSession, user_id: int):
        """Simulate a typical user workflow"""
        
        # 1. Health check
        result = await self.make_request(session, 'GET', '/health')
        self.results.append(result)
        
        # 2. Get API info
        result = await self.make_request(session, 'GET', '/api/v1/info')
        self.results.append(result)
        
        # 3. List categories
        result = await self.make_request(session, 'GET', '/api/v1/store/categories')
        self.results.append(result)
        
        # 4. List products
        result = await self.make_request(session, 'GET', '/api/v1/store/products?page=1&per_page=20')
        self.results.append(result)
        
        # 5. Search products
        result = await self.make_request(session, 'GET', '/api/v1/store/products?search=brain')
        self.results.append(result)
        
        # 6. Get metrics (if available)
        result = await self.make_request(session, 'GET', '/metrics')
        self.results.append(result)
        
        # Small delay between requests to simulate real user behavior
        await asyncio.sleep(0.1)
    
    async def stress_test_endpoint(self, session: aiohttp.ClientSession, endpoint: str, method: str = 'GET', count: int = 100):
        """Stress test a specific endpoint"""
        tasks = []
        
        for i in range(count):
            task = self.make_request(session, method, endpoint)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, TestResult):
                self.results.append(result)
            else:
                # Handle exceptions
                self.results.append(TestResult(
                    endpoint=endpoint,
                    method=method,
                    status_code=0,
                    response_time=0,
                    success=False,
                    error=str(result)
                ))
    
    async def run_load_test(self, duration_seconds: int = 60):
        """Run load test for specified duration"""
        
        print(f"🚀 Starting load test with {self.concurrent_users} concurrent users for {duration_seconds} seconds")
        print(f"🎯 Target: {self.base_url}")
        
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            start_time = time.time()
            tasks = []
            
            # Create user workflow tasks
            while time.time() - start_time < duration_seconds:
                # Batch users to avoid overwhelming the server
                batch_tasks = []
                for user_id in range(self.concurrent_users):
                    task = self.user_workflow(session, user_id)
                    batch_tasks.append(task)
                
                await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Small delay between batches
                await asyncio.sleep(1)
        
        return self.analyze_results()
    
    async def run_stress_test(self, endpoint: str = '/api/v1/store/products', requests_count: int = 1000):
        """Run stress test on specific endpoint"""
        
        print(f"⚡ Starting stress test on {endpoint} with {requests_count} requests")
        
        connector = aiohttp.TCPConnector(limit=200, limit_per_host=100)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            await self.stress_test_endpoint(session, endpoint, count=requests_count)
        
        return self.analyze_results()
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze test results and generate report"""
        
        if not self.results:
            return {"error": "No results to analyze"}
        
        # Group results by endpoint
        endpoint_stats = {}
        
        for result in self.results:
            key = f"{result.method} {result.endpoint}"
            if key not in endpoint_stats:
                endpoint_stats[key] = {
                    'requests': 0,
                    'successes': 0,
                    'failures': 0,
                    'response_times': [],
                    'status_codes': {},
                    'errors': []
                }
            
            stats = endpoint_stats[key]
            stats['requests'] += 1
            
            if result.success:
                stats['successes'] += 1
            else:
                stats['failures'] += 1
                if result.error:
                    stats['errors'].append(result.error)
            
            stats['response_times'].append(result.response_time)
            
            status_key = str(result.status_code)
            stats['status_codes'][status_key] = stats['status_codes'].get(status_key, 0) + 1
        
        # Calculate statistics
        analysis = {
            'summary': {
                'total_requests': len(self.results),
                'total_successes': sum(1 for r in self.results if r.success),
                'total_failures': sum(1 for r in self.results if not r.success),
                'success_rate': (sum(1 for r in self.results if r.success) / len(self.results)) * 100,
            },
            'endpoints': {}
        }
        
        for endpoint, stats in endpoint_stats.items():
            response_times = stats['response_times']
            
            if response_times:
                analysis['endpoints'][endpoint] = {
                    'requests': stats['requests'],
                    'successes': stats['successes'],
                    'failures': stats['failures'],
                    'success_rate': (stats['successes'] / stats['requests']) * 100,
                    'response_time': {
                        'min': min(response_times),
                        'max': max(response_times),
                        'avg': statistics.mean(response_times),
                        'median': statistics.median(response_times),
                        'p95': statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times),
                        'p99': statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else max(response_times),
                    },
                    'status_codes': stats['status_codes'],
                    'unique_errors': list(set(stats['errors'])) if stats['errors'] else []
                }
        
        return analysis
    
    def print_report(self, analysis: Dict[str, Any]):
        """Print formatted test report"""
        
        print("\n" + "="*60)
        print("📊 LOAD TEST REPORT")
        print("="*60)
        
        summary = analysis['summary']
        print(f"Total Requests: {summary['total_requests']}")
        print(f"Successful: {summary['total_successes']}")
        print(f"Failed: {summary['total_failures']}")
        print(f"Success Rate: {summary['success_rate']:.2f}%")
        
        print("\n📈 ENDPOINT PERFORMANCE:")
        print("-" * 60)
        
        for endpoint, stats in analysis['endpoints'].items():
            print(f"\n{endpoint}")
            print(f"  Requests: {stats['requests']}")
            print(f"  Success Rate: {stats['success_rate']:.2f}%")
            
            rt = stats['response_time']
            print(f"  Response Time (ms):")
            print(f"    Min: {rt['min']*1000:.1f}")
            print(f"    Avg: {rt['avg']*1000:.1f}")
            print(f"    Max: {rt['max']*1000:.1f}")
            print(f"    P95: {rt['p95']*1000:.1f}")
            print(f"    P99: {rt['p99']*1000:.1f}")
            
            if stats['unique_errors']:
                print(f"  Errors: {', '.join(stats['unique_errors'][:3])}")

async def main():
    parser = argparse.ArgumentParser(description='Load test BrainSAIT Store API')
    parser.add_argument('--url', default='http://localhost:8000', help='Base URL of the API')
    parser.add_argument('--users', type=int, default=10, help='Number of concurrent users')
    parser.add_argument('--duration', type=int, default=60, help='Test duration in seconds')
    parser.add_argument('--stress', action='store_true', help='Run stress test instead of load test')
    parser.add_argument('--endpoint', default='/api/v1/store/products', help='Endpoint for stress test')
    parser.add_argument('--requests', type=int, default=1000, help='Number of requests for stress test')
    
    args = parser.parse_args()
    
    tester = LoadTester(args.url, args.users)
    
    try:
        if args.stress:
            analysis = await tester.run_stress_test(args.endpoint, args.requests)
        else:
            analysis = await tester.run_load_test(args.duration)
        
        tester.print_report(analysis)
        
        # Save results to file
        with open('load_test_results.json', 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\n📄 Results saved to load_test_results.json")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during test: {e}")

if __name__ == "__main__":
    asyncio.run(main())
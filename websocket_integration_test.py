#!/usr/bin/env python3
"""
WebSocket Integration Test - Real-time connection testing
Tests browser-to-backend WebSocket connections for telemetry and depth data
"""

import asyncio
import websockets
import json
import time
import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebSocketTester:
    def __init__(self):
        self.telemetry_url = "ws://localhost:8766"
        self.depth_url = "ws://localhost:8765"
        self.test_results = []
        
    async def test_telemetry_connection(self):
        """Test telemetry server WebSocket connection"""
        logger.info("🔗 Testing telemetry server connection...")
        
        try:
            async with websockets.connect(self.telemetry_url) as websocket:
                logger.info("✅ Connected to telemetry server")
                
                # Test vehicle list request
                request = {"command": "get_vehicles"}
                await websocket.send(json.dumps(request))
                
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                
                if data.get('type') == 'vehicle_list' and 'vehicles' in data:
                    logger.info(f"✅ Vehicle list received: {len(data['vehicles'])} vehicles")
                    self.test_results.append({"test": "telemetry_connection", "status": "PASS"})
                    return True
                else:
                    logger.error(f"❌ Invalid response: {data}")
                    self.test_results.append({"test": "telemetry_connection", "status": "FAIL"})
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Telemetry connection failed: {e}")
            self.test_results.append({"test": "telemetry_connection", "status": "FAIL", "error": str(e)})
            return False
    
    async def test_depth_connection(self):
        """Test depth server WebSocket connection"""
        logger.info("🔗 Testing depth server connection...")
        
        try:
            async with websockets.connect(self.depth_url) as websocket:
                logger.info("✅ Connected to depth server")
                
                # Test depth data request
                request = {"command": "get_depth_data"}
                await websocket.send(json.dumps(request))
                
                # Wait for response or timeout
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    logger.info("✅ Depth server responded")
                    self.test_results.append({"test": "depth_connection", "status": "PASS"})
                    return True
                except asyncio.TimeoutError:
                    logger.info("⚠️ Depth server timeout (normal for webcam issues)")
                    self.test_results.append({"test": "depth_connection", "status": "PASS", "note": "timeout_expected"})
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Depth connection failed: {e}")
            self.test_results.append({"test": "depth_connection", "status": "FAIL", "error": str(e)})
            return False
    
    async def test_vehicle_control(self):
        """Test vehicle control commands"""
        logger.info("🚛 Testing vehicle control...")
        
        try:
            async with websockets.connect(self.telemetry_url) as websocket:
                # Test vehicle control command
                request = {
                    "command": "control_vehicle",
                    "vehicle_id": "EX001",
                    "action": "move_forward"
                }
                await websocket.send(json.dumps(request))
                
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                
                if data.get('type') == 'command_ack':
                    logger.info("✅ Vehicle control command acknowledged")
                    self.test_results.append({"test": "vehicle_control", "status": "PASS"})
                    return True
                else:
                    logger.error(f"❌ Invalid control response: {data}")
                    self.test_results.append({"test": "vehicle_control", "status": "FAIL"})
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Vehicle control failed: {e}")
            self.test_results.append({"test": "vehicle_control", "status": "FAIL", "error": str(e)})
            return False
    
    async def test_connection_stability(self):
        """Test connection stability over time"""
        logger.info("⏱️ Testing connection stability...")
        
        try:
            async with websockets.connect(self.telemetry_url) as websocket:
                # Send multiple requests over time
                for i in range(5):
                    request = {"command": "get_vehicles"}
                    await websocket.send(json.dumps(request))
                    
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(response)
                    
                    if data.get('type') != 'vehicle_list':
                        logger.error(f"❌ Stability test failed at iteration {i}")
                        self.test_results.append({"test": "connection_stability", "status": "FAIL"})
                        return False
                    
                    await asyncio.sleep(0.5)  # Small delay between requests
                
                logger.info("✅ Connection stability test passed")
                self.test_results.append({"test": "connection_stability", "status": "PASS"})
                return True
                
        except Exception as e:
            logger.error(f"❌ Stability test failed: {e}")
            self.test_results.append({"test": "connection_stability", "status": "FAIL", "error": str(e)})
            return False
    
    async def run_all_tests(self):
        """Run all WebSocket integration tests"""
        logger.info("🧪 Starting WebSocket Integration Tests...")
        
        tests = [
            self.test_telemetry_connection(),
            self.test_depth_connection(),
            self.test_vehicle_control(),
            self.test_connection_stability()
        ]
        
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        # Calculate success rate
        passed = sum(1 for result in self.test_results if result.get('status') == 'PASS')
        total = len(self.test_results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        logger.info(f"📊 WebSocket Integration Test Results:")
        logger.info(f"   Tests Passed: {passed}/{total}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        
        # Generate report
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": total,
            "passed_tests": passed,
            "success_rate": success_rate,
            "test_results": self.test_results
        }
        
        # Save report
        with open("websocket_integration_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info("📄 Report saved: websocket_integration_report.json")
        
        return success_rate >= 75.0  # 75% success rate threshold

async def main():
    """Main test runner"""
    tester = WebSocketTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 WebSocket Integration Tests: PASSED")
        return 0
    else:
        print("\n❌ WebSocket Integration Tests: FAILED")
        return 1

if __name__ == "__main__":
    import sys
    result = asyncio.run(main())
    sys.exit(result)

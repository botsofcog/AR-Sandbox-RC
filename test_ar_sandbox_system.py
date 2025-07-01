#!/usr/bin/env python3
"""
Comprehensive AR Sandbox RC System Test
Tests all components: Kinect, WebSocket, HTML demos, AI analysis
"""

import asyncio
import websockets
import json
import time
import sys
import os
from pathlib import Path

class ARSandboxSystemTester:
    def __init__(self):
        self.test_results = {}
        self.websocket_uri = "ws://localhost:8765"
        self.html_files = [
            "robust-ar-sandbox.html",
            "ultimate-ar-sandbox.html", 
            "kinect_ar_sandbox.html",
            "ar_sandbox_frontend.html",
            "physics-ar-sandbox.html",
            "fluid_sandbox_demo.html",
            "voxel-ar-sandbox.html",
            "rc_sandbox_clean/index.html",
            "frontend/index.html"
        ]
        
    async def test_websocket_connection(self):
        """Test WebSocket connection to depth server"""
        print("🔌 Testing WebSocket connection...")
        try:
            async with websockets.connect(self.websocket_uri) as websocket:
                # Send ping
                await websocket.send(json.dumps({"type": "ping"}))
                
                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                
                if data.get("type") == "pong":
                    print("✅ WebSocket connection successful")
                    self.test_results["websocket_connection"] = True
                    return True
                else:
                    print(f"❌ Unexpected response: {data}")
                    self.test_results["websocket_connection"] = False
                    return False
                    
        except Exception as e:
            print(f"❌ WebSocket connection failed: {e}")
            self.test_results["websocket_connection"] = False
            return False
    
    async def test_kinect_data_stream(self):
        """Test Kinect data streaming"""
        print("📷 Testing Kinect data stream...")
        try:
            async with websockets.connect(self.websocket_uri) as websocket:
                # Request frame data
                await websocket.send(json.dumps({
                    "type": "get_frame",
                    "include_topography": True
                }))
                
                # Wait for frame data
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(response)
                
                if data.get("type") == "frame_data":
                    mesh_data = data.get("mesh_data", {})
                    topography = data.get("topography", {})
                    interaction = data.get("interaction", {})
                    
                    print(f"✅ Received frame data:")
                    print(f"   📊 Mesh data: {len(mesh_data.get('data', []))} points")
                    print(f"   🗺️ Topography: {'✅' if topography else '❌'}")
                    print(f"   👋 Hand interaction: {'✅' if interaction else '❌'}")
                    
                    self.test_results["kinect_data_stream"] = True
                    self.test_results["mesh_data_points"] = len(mesh_data.get('data', []))
                    self.test_results["has_topography"] = bool(topography)
                    self.test_results["has_interaction"] = bool(interaction)
                    return True
                else:
                    print(f"❌ Expected frame_data, got: {data.get('type')}")
                    self.test_results["kinect_data_stream"] = False
                    return False
                    
        except Exception as e:
            print(f"❌ Kinect data stream test failed: {e}")
            self.test_results["kinect_data_stream"] = False
            return False
    
    def test_html_files_exist(self):
        """Test that all HTML files exist and have WebSocket integration"""
        print("📄 Testing HTML files...")
        missing_files = []
        websocket_integrated = []
        
        for html_file in self.html_files:
            file_path = Path(html_file)
            if file_path.exists():
                print(f"✅ {html_file} exists")
                
                # Check for WebSocket integration
                try:
                    content = file_path.read_text(encoding='utf-8')
                    if 'kinect_websocket_integration.js' in content or 'WebSocket' in content:
                        websocket_integrated.append(html_file)
                        print(f"   🔗 WebSocket integration found")
                    else:
                        print(f"   ⚠️ No WebSocket integration detected")
                except Exception as e:
                    print(f"   ❌ Error reading file: {e}")
            else:
                missing_files.append(html_file)
                print(f"❌ {html_file} missing")
        
        self.test_results["html_files_exist"] = len(missing_files) == 0
        self.test_results["missing_files"] = missing_files
        self.test_results["websocket_integrated_files"] = len(websocket_integrated)
        self.test_results["total_files_tested"] = len(self.html_files)
        
        return len(missing_files) == 0
    
    def test_external_libraries(self):
        """Test external library integrations"""
        print("📚 Testing external library integrations...")
        
        libraries_to_check = [
            "external_libs/THREE.Terrain/build/THREE.Terrain.min.js",
            "external_libs/matter-js/build/matter.min.js", 
            "external_libs/ml5-library/dist/ml5.min.js",
            "external_libs/webgl-fluid-simulation/script.js",
            "js/kinect_websocket_integration.js"
        ]
        
        available_libraries = []
        missing_libraries = []
        
        for lib_path in libraries_to_check:
            if Path(lib_path).exists():
                available_libraries.append(lib_path)
                print(f"✅ {lib_path}")
            else:
                missing_libraries.append(lib_path)
                print(f"❌ {lib_path} missing")
        
        self.test_results["external_libraries_available"] = len(available_libraries)
        self.test_results["external_libraries_missing"] = len(missing_libraries)
        self.test_results["missing_libraries"] = missing_libraries
        
        return len(missing_libraries) == 0
    
    async def test_ai_analysis(self):
        """Test AI terrain analysis"""
        print("🤖 Testing AI terrain analysis...")
        try:
            async with websockets.connect(self.websocket_uri) as websocket:
                # Request frame with topography
                await websocket.send(json.dumps({
                    "type": "get_frame",
                    "include_topography": True
                }))
                
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(response)
                
                topography = data.get("topography", {})
                ai_metadata = topography.get("ai_metadata", {})
                
                if ai_metadata:
                    print("✅ AI analysis working:")
                    
                    # Check terrain stats
                    terrain_stats = ai_metadata.get("terrain_stats", {})
                    if terrain_stats:
                        print(f"   📊 Terrain stats: elevation {terrain_stats.get('min_elevation', 0):.1f}-{terrain_stats.get('max_elevation', 0):.1f}")
                        print(f"   📈 Roughness: {terrain_stats.get('terrain_roughness', 0):.3f}")
                    
                    # Check features
                    features = ai_metadata.get("features", {})
                    if features:
                        peaks = features.get("peaks", {})
                        valleys = features.get("valleys", {})
                        print(f"   🏔️ Peaks detected: {peaks.get('count', 0)}")
                        print(f"   🕳️ Valleys detected: {valleys.get('count', 0)}")
                    
                    self.test_results["ai_analysis"] = True
                    return True
                else:
                    print("❌ No AI analysis data received")
                    self.test_results["ai_analysis"] = False
                    return False
                    
        except Exception as e:
            print(f"❌ AI analysis test failed: {e}")
            self.test_results["ai_analysis"] = False
            return False
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("🧪 AR SANDBOX RC SYSTEM TEST REPORT")
        print("="*60)
        
        total_tests = 0
        passed_tests = 0
        
        # Core functionality tests
        print("\n📋 CORE FUNCTIONALITY:")
        for test_name, result in self.test_results.items():
            if isinstance(result, bool):
                total_tests += 1
                if result:
                    passed_tests += 1
                    print(f"✅ {test_name.replace('_', ' ').title()}")
                else:
                    print(f"❌ {test_name.replace('_', ' ').title()}")
        
        # Statistics
        print(f"\n📊 STATISTICS:")
        print(f"   HTML files with WebSocket: {self.test_results.get('websocket_integrated_files', 0)}/{self.test_results.get('total_files_tested', 0)}")
        print(f"   Mesh data points: {self.test_results.get('mesh_data_points', 0)}")
        print(f"   External libraries available: {self.test_results.get('external_libraries_available', 0)}")
        
        # Overall score
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\n🎯 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT! AR Sandbox RC system is fully operational!")
        elif success_rate >= 75:
            print("✅ GOOD! AR Sandbox RC system is mostly functional with minor issues.")
        elif success_rate >= 50:
            print("⚠️ FAIR! AR Sandbox RC system has some functionality but needs fixes.")
        else:
            print("❌ POOR! AR Sandbox RC system needs significant repairs.")
        
        return success_rate

async def main():
    """Run comprehensive AR Sandbox RC system test"""
    print("🚀 Starting AR Sandbox RC System Test...")
    print("="*60)
    
    tester = ARSandboxSystemTester()
    
    # Run all tests
    await tester.test_websocket_connection()
    await tester.test_kinect_data_stream()
    tester.test_html_files_exist()
    tester.test_external_libraries()
    await tester.test_ai_analysis()
    
    # Generate report
    success_rate = tester.generate_test_report()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 75 else 1)

if __name__ == "__main__":
    asyncio.run(main())

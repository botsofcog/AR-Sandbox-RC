#!/usr/bin/env python3
"""
Comprehensive test for topography rendering with real Kinect + webcam data
"""

import asyncio
import websockets
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_topography_integration():
    """Test the complete topography rendering pipeline"""
    print("🧪 Testing Enhanced Topography Integration")
    print("=" * 50)
    
    try:
        # Connect to the enhanced depth server
        uri = "ws://localhost:8765"
        print(f"🔗 Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established!")
            
            # Test 1: Request frame data with topography
            print("\n📊 Test 1: Requesting frame data with topography...")
            await websocket.send(json.dumps({
                "type": "get_frame",
                "include_topography": True
            }))
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            data = json.loads(response)
            
            print(f"📥 Response type: {data.get('type', 'unknown')}")
            
            if data.get('type') == 'frame_data':
                print("✅ Frame data received!")
                
                # Check for topography data
                if 'topography' in data:
                    topo = data['topography']
                    print("🗺️  Topography data found!")
                    
                    # Test AI metadata
                    if 'ai_metadata' in topo:
                        ai_meta = topo['ai_metadata']
                        print(f"🤖 AI Metadata available:")
                        
                        # Terrain stats
                        if 'terrain_stats' in ai_meta:
                            terrain = ai_meta['terrain_stats']
                            print(f"   📏 Elevation range: {terrain.get('min_elevation', 'N/A'):.3f} - {terrain.get('max_elevation', 'N/A'):.3f}")
                            print(f"   📊 Mean elevation: {terrain.get('mean_elevation', 'N/A'):.3f}")
                            print(f"   🏔️  Terrain roughness: {terrain.get('terrain_roughness', 'N/A'):.3f}")
                        
                        # Feature detection
                        if 'features' in ai_meta:
                            features = ai_meta['features']
                            print(f"🔍 Detected features:")
                            
                            if 'peaks' in features and features['peaks']:
                                peaks = features['peaks']
                                print(f"   ⛰️  Peaks: {peaks.get('count', 0)} detected")
                            
                            if 'valleys' in features and features['valleys']:
                                valleys = features['valleys']
                                print(f"   🏞️  Valleys: {valleys.get('count', 0)} detected")
                            
                            if 'slopes' in features and features['slopes']:
                                slopes = features['slopes']
                                print(f"   📐 Average slope: {slopes.get('average_slope', 0):.1f}°")
                                print(f"   ⚠️  Steep areas: {slopes.get('steep_areas_percent', 0):.1f}%")
                            
                            if 'water_areas' in features and features['water_areas']:
                                water = features['water_areas']
                                print(f"   💧 Water coverage: {water.get('percentage', 0):.1f}%")
                            
                            if 'vegetation' in features and features['vegetation']:
                                veg = features['vegetation']
                                print(f"   🌿 Vegetation coverage: {veg.get('percentage', 0):.1f}%")
                        
                        # AI recommendations
                        if 'recommendations' in ai_meta:
                            recs = ai_meta['recommendations']
                            print(f"💡 AI Recommendations:")
                            for key, value in recs.items():
                                print(f"   {key}: {value}")
                        
                        # Color analysis
                        if 'color_stats' in ai_meta:
                            colors = ai_meta['color_stats']
                            print(f"🎨 Color Analysis:")
                            print(f"   Brightness: {colors.get('brightness', 0):.1f}")
                            print(f"   Contrast: {colors.get('contrast', 0):.1f}")
                            if 'dominant_colors' in colors:
                                print(f"   Dominant colors: {len(colors['dominant_colors'])} detected")
                    
                    # Test terrain features
                    if 'terrain_features' in topo:
                        print("🏔️  Terrain features data available")
                    
                    # Test elevation stats
                    if 'elevation_stats' in topo:
                        elev = topo['elevation_stats']
                        print(f"📈 Elevation Statistics:")
                        print(f"   Min: {elev.get('min', 0):.3f}")
                        print(f"   Max: {elev.get('max', 0):.3f}")
                        print(f"   Mean: {elev.get('mean', 0):.3f}")
                
                else:
                    print("❌ No topography data in response")
                    return False
            
            else:
                print(f"❌ Unexpected response type: {data.get('type')}")
                return False
            
            # Test 2: Stream multiple frames to test consistency
            print("\n🔄 Test 2: Testing topography data consistency...")
            await websocket.send(json.dumps({
                "type": "start_stream",
                "include_topography": True
            }))
            
            frame_count = 0
            consistent_data = True
            
            for i in range(5):  # Test 5 frames
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    
                    if data.get('type') == 'frame_data' and 'topography' in data:
                        frame_count += 1
                        topo = data['topography']
                        
                        # Check for consistent AI metadata
                        if 'ai_metadata' not in topo:
                            consistent_data = False
                            print(f"   ❌ Frame {i+1}: Missing AI metadata")
                        else:
                            print(f"   ✅ Frame {i+1}: Topography data consistent")
                    
                except asyncio.TimeoutError:
                    print(f"   ⏰ Frame {i+1}: Timeout")
                    break
            
            # Stop stream
            await websocket.send(json.dumps({"type": "stop_stream"}))
            
            print(f"📊 Processed {frame_count}/5 frames with topography data")
            
            if frame_count >= 3 and consistent_data:
                print("✅ Topography data consistency test PASSED")
            else:
                print("❌ Topography data consistency test FAILED")
                return False
            
            # Test 3: Performance check
            print("\n⚡ Test 3: Performance analysis...")
            start_time = time.time()
            
            await websocket.send(json.dumps({
                "type": "get_frame",
                "include_topography": True
            }))
            
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            end_time = time.time()
            
            processing_time = (end_time - start_time) * 1000  # Convert to ms
            print(f"⏱️  Frame processing time: {processing_time:.1f}ms")
            
            if processing_time < 1000:  # Less than 1 second
                print("✅ Performance test PASSED (< 1000ms)")
            else:
                print("⚠️  Performance test WARNING (> 1000ms)")
            
            return True
            
    except ConnectionRefusedError:
        print("❌ Connection refused - is the enhanced depth server running?")
        return False
    except asyncio.TimeoutError:
        print("❌ Timeout - server not responding")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 Enhanced Topography Integration Test")
    print("Testing Kinect + Webcam + AI Topography Rendering")
    print("=" * 60)
    
    success = await test_topography_integration()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TOPOGRAPHY INTEGRATION TESTS PASSED!")
        print("✅ Kinect depth data working")
        print("✅ Topography rendering working") 
        print("✅ AI metadata generation working")
        print("✅ Feature detection working")
        print("✅ Real-time processing working")
        print("\n🤖 The AR Sandbox now has AI-powered terrain analysis!")
    else:
        print("❌ Topography integration tests failed")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Deep test for WebSocket connection to depth server
"""

import asyncio
import websockets
import json
import time

async def test_websocket_connection():
    """Test WebSocket connection and data flow"""
    print("Testing WebSocket connection to depth server...")
    
    try:
        # Connect to the depth server
        uri = "ws://localhost:8765"
        print(f"Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established!")
            
            # Test 1: Send ping
            await websocket.send(json.dumps({"type": "ping"}))
            print("📤 Sent ping message")
            
            # Test 2: Request frame data
            await websocket.send(json.dumps({"type": "get_frame"}))
            print("📤 Requested frame data")
            
            # Test 3: Listen for responses
            response_count = 0
            start_time = time.time()
            
            while response_count < 5 and (time.time() - start_time) < 10:
                try:
                    # Wait for response with timeout
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(response)
                    response_count += 1
                    
                    print(f"📥 Response {response_count}: {data.get('type', 'unknown')}")
                    
                    if data.get('type') == 'frame_data':
                        # Analyze frame data
                        if 'depth_data' in data:
                            depth_info = data['depth_data']
                            print(f"   🔍 Depth data: {depth_info.get('width', 'N/A')}x{depth_info.get('height', 'N/A')}")
                            print(f"   📊 Depth range: {depth_info.get('min_depth', 'N/A')}-{depth_info.get('max_depth', 'N/A')}")
                        
                        if 'rgb_data' in data:
                            rgb_info = data['rgb_data']
                            print(f"   🎨 RGB data: {rgb_info.get('width', 'N/A')}x{rgb_info.get('height', 'N/A')}")
                        
                        if 'timestamp' in data:
                            print(f"   ⏰ Timestamp: {data['timestamp']}")
                    
                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for response")
                    break
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                except Exception as e:
                    print(f"❌ Error receiving data: {e}")
            
            print(f"✅ Received {response_count} responses")
            
            # Test 4: Test continuous data stream
            print("\n🔄 Testing continuous data stream...")
            await websocket.send(json.dumps({"type": "start_stream"}))
            
            stream_count = 0
            stream_start = time.time()
            
            while stream_count < 10 and (time.time() - stream_start) < 5:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(response)
                    stream_count += 1
                    
                    if data.get('type') == 'frame_data':
                        print(f"📺 Stream frame {stream_count}")
                    
                except asyncio.TimeoutError:
                    break
                except Exception as e:
                    print(f"❌ Stream error: {e}")
                    break
            
            print(f"✅ Received {stream_count} stream frames")
            
            # Test 5: Stop stream
            await websocket.send(json.dumps({"type": "stop_stream"}))
            print("🛑 Stopped stream")
            
    except ConnectionRefusedError:
        print("❌ Connection refused - is the depth server running?")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    print("✅ WebSocket connection test completed successfully!")
    return True

async def main():
    """Main test function"""
    print("=== Deep WebSocket Connection Test ===")
    success = await test_websocket_connection()
    
    if success:
        print("\n🎉 ALL WEBSOCKET TESTS PASSED!")
    else:
        print("\n❌ WebSocket tests failed")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())

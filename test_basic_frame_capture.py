#!/usr/bin/env python3
"""
Basic test for frame capture functionality
"""

import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_basic_frame_capture():
    """Test basic frame capture without topography"""
    print("🧪 Testing Basic Frame Capture")
    print("=" * 40)
    
    try:
        # Connect to the depth server
        uri = "ws://localhost:8765"
        print(f"🔗 Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established!")
            
            # Test 1: Simple ping
            print("\n📡 Test 1: Ping test...")
            await websocket.send(json.dumps({"type": "ping"}))
            
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)
            
            if data.get('type') == 'pong':
                print("✅ Ping test PASSED")
            else:
                print(f"❌ Ping test FAILED: {data}")
                return False
            
            # Test 2: Basic frame request (no topography)
            print("\n📊 Test 2: Basic frame request...")
            await websocket.send(json.dumps({"type": "get_frame"}))
            
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            data = json.loads(response)
            
            print(f"📥 Response type: {data.get('type', 'unknown')}")
            
            if data.get('type') == 'error':
                print(f"❌ Frame capture error: {data.get('message', 'Unknown error')}")
                return False
            elif data.get('type') == 'frame_data':
                print("✅ Basic frame capture PASSED")
                
                # Check what data we got
                if 'mesh_data' in data:
                    print("   📐 Mesh data available")
                if 'timestamp' in data:
                    print(f"   ⏰ Timestamp: {data['timestamp']}")
                if 'rgb_frame' in data:
                    print("   🎨 RGB frame data available")
                
                return True
            else:
                print(f"❌ Unexpected response: {data.get('type')}")
                return False
            
    except ConnectionRefusedError:
        print("❌ Connection refused - is the depth server running?")
        return False
    except asyncio.TimeoutError:
        print("❌ Timeout - server not responding")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 Basic Frame Capture Test")
    print("Testing fundamental server functionality")
    print("=" * 50)
    
    success = await test_basic_frame_capture()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 BASIC FRAME CAPTURE TEST PASSED!")
        print("✅ WebSocket communication working")
        print("✅ Message handling working")
        print("✅ Frame capture working")
    else:
        print("❌ Basic frame capture test failed")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())

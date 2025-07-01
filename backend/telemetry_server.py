#!/usr/bin/env python3
"""
Telemetry Server - WebSocket/MQTT server for RC vehicle data
Part of the RC Sandbox modular architecture
Updated: 2025-06-27 - Enhanced vehicle tracking and performance monitoring
Integrated with Magic Sand AR sandbox system
"""

import asyncio
import websockets
import json
import time
import random
import math
import logging
import serial
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class VehicleState:
    """RC Vehicle telemetry data structure"""
    vehicle_id: str
    vehicle_type: str  # excavator, bulldozer, dump_truck, crane, compactor
    x: float
    y: float
    rotation: float  # degrees
    speed: float  # units/sec
    battery_level: float  # 0-100%
    attachment_state: str  # raised, lowered, dumping, etc.
    task_status: str  # idle, working, moving, error
    timestamp: float

class TelemetryServer:
    """WebSocket server for streaming RC vehicle telemetry"""
    
    def __init__(self, port: int = 8766):
        self.port = port
        self.clients = set()
        self.vehicles: Dict[str, VehicleState] = {}
        self.running = False
        
        # Simulation parameters for demo mode
        self.demo_mode = True
        self.sandbox_width = 1000  # sandbox units
        self.sandbox_height = 750
        
        print(f"🚛 Telemetry Server initializing on port {port}")
        self.initialize_demo_vehicles()
    
    def initialize_demo_vehicles(self):
        """Initialize demo vehicles for testing"""
        demo_vehicles = [
            ("EX001", "excavator", 200, 300, 45, 2.0),
            ("BD001", "bulldozer", 400, 200, 90, 2.5),
            ("DT001", "dump_truck", 600, 400, 180, 3.5),
            ("CR001", "crane", 300, 500, 270, 1.5),
            ("CP001", "compactor", 500, 300, 0, 2.0)
        ]
        
        for vid, vtype, x, y, rot, speed in demo_vehicles:
            self.vehicles[vid] = VehicleState(
                vehicle_id=vid,
                vehicle_type=vtype,
                x=x, y=y, rotation=rot, speed=speed,
                battery_level=random.uniform(60, 100),
                attachment_state="idle",
                task_status="idle",
                timestamp=time.time()
            )
        
        print(f"🎮 Initialized {len(self.vehicles)} demo vehicles")
    
    def update_vehicle_simulation(self):
        """Update vehicle positions and states for demo"""
        current_time = time.time()
        
        for vehicle in self.vehicles.values():
            # Simple movement simulation
            if vehicle.task_status == "working":
                # Random movement within bounds
                dx = random.uniform(-vehicle.speed, vehicle.speed)
                dy = random.uniform(-vehicle.speed, vehicle.speed)
                
                new_x = max(50, min(self.sandbox_width - 50, vehicle.x + dx))
                new_y = max(50, min(self.sandbox_height - 50, vehicle.y + dy))
                
                vehicle.x = new_x
                vehicle.y = new_y
                vehicle.rotation = (vehicle.rotation + random.uniform(-5, 5)) % 360
                
                # Simulate battery drain
                vehicle.battery_level = max(0, vehicle.battery_level - 0.01)
                
                # Random task changes
                if random.random() < 0.02:  # 2% chance per update
                    vehicle.task_status = random.choice(["idle", "moving", "working"])
                    vehicle.attachment_state = random.choice(["raised", "lowered", "active"])
            
            elif vehicle.task_status == "moving":
                # Move toward a random target
                target_x = random.uniform(100, self.sandbox_width - 100)
                target_y = random.uniform(100, self.sandbox_height - 100)
                
                # Move toward target
                dx = target_x - vehicle.x
                dy = target_y - vehicle.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > 5:
                    move_x = (dx / distance) * vehicle.speed
                    move_y = (dy / distance) * vehicle.speed
                    vehicle.x += move_x
                    vehicle.y += move_y
                    vehicle.rotation = math.degrees(math.atan2(dy, dx))
                else:
                    vehicle.task_status = "working"
            
            else:  # idle
                if random.random() < 0.01:  # 1% chance to start moving
                    vehicle.task_status = "moving"
            
            vehicle.timestamp = current_time
    
    def get_telemetry_data(self) -> Dict[str, Any]:
        """Get current telemetry data for all vehicles"""
        return {
            'timestamp': time.time(),
            'vehicles': {vid: asdict(vehicle) for vid, vehicle in self.vehicles.items()},
            'sandbox_bounds': {
                'width': self.sandbox_width,
                'height': self.sandbox_height
            },
            'active_vehicles': len([v for v in self.vehicles.values() if v.task_status != "idle"]),
            'total_vehicles': len(self.vehicles)
        }
    
    def process_vehicle_command(self, command: Dict[str, Any]) -> bool:
        """Process incoming vehicle control command"""
        try:
            vehicle_id = command.get('vehicle_id')
            action = command.get('action')

            if vehicle_id not in self.vehicles:
                print(f"⚠️ Unknown vehicle: {vehicle_id}")
                return False

            vehicle = self.vehicles[vehicle_id]

            if action == 'move':
                target_x = command.get('target_x', vehicle.x)
                target_y = command.get('target_y', vehicle.y)
                vehicle.task_status = "moving"
                print(f"🎯 {vehicle_id} moving to ({target_x}, {target_y})")

            elif action == 'work':
                vehicle.task_status = "working"
                vehicle.attachment_state = command.get('attachment', 'active')
                print(f"🔧 {vehicle_id} starting work")

            elif action == 'stop':
                vehicle.task_status = "idle"
                vehicle.attachment_state = "idle"
                print(f"🛑 {vehicle_id} stopped")

            elif action == 'set_speed':
                new_speed = max(0.5, min(5.0, command.get('speed', vehicle.speed)))
                vehicle.speed = new_speed
                print(f"⚡ {vehicle_id} speed set to {new_speed}")

            elif action == 'select':
                print(f"🎯 {vehicle_id} selected for control")
                # Could add selection state tracking here

            elif action == 'emergency_stop':
                vehicle.task_status = "idle"
                vehicle.attachment_state = "idle"
                vehicle.speed = 0
                print(f"🚨 {vehicle_id} EMERGENCY STOP")

            elif action == 'start_mission':
                mission_type = command.get('mission_type', 'flood_defense')
                vehicle.task_status = "working"
                print(f"🎮 {vehicle_id} starting {mission_type} mission")

            return True

        except Exception as e:
            print(f"❌ Command error: {e}")
            return False
    
    async def handle_client(self, websocket):
        """Handle WebSocket client connection"""
        self.clients.add(websocket)
        client_addr = websocket.remote_address
        print(f"🔗 Telemetry client connected: {client_addr}")
        
        try:
            # Send initial vehicle data
            initial_data = self.get_telemetry_data()
            await websocket.send(json.dumps(initial_data))
            
            # Listen for commands
            async for message in websocket:
                try:
                    command = json.loads(message)
                    success = self.process_vehicle_command(command)
                    
                    # Send acknowledgment
                    response = {
                        'type': 'command_response',
                        'success': success,
                        'timestamp': time.time()
                    }
                    await websocket.send(json.dumps(response))
                    
                except json.JSONDecodeError:
                    print(f"⚠️ Invalid JSON from {client_addr}")
                except Exception as e:
                    print(f"❌ Client message error: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            print(f"🔌 Telemetry client disconnected: {client_addr}")
    
    async def broadcast_telemetry(self):
        """Continuously broadcast telemetry data to all clients"""
        while self.running:
            if self.demo_mode:
                self.update_vehicle_simulation()
            
            if self.clients:
                telemetry_data = self.get_telemetry_data()
                message = json.dumps(telemetry_data)
                
                # Send to all connected clients
                disconnected = []
                for client in self.clients:
                    try:
                        await client.send(message)
                    except websockets.exceptions.ConnectionClosed:
                        disconnected.append(client)
                
                # Remove disconnected clients
                for client in disconnected:
                    self.clients.discard(client)
            
            await asyncio.sleep(1/20)  # 20 Hz telemetry rate
    
    async def start_server(self):
        """Start the telemetry WebSocket server"""
        self.running = True
        
        # Start WebSocket server
        server = await websockets.serve(self.handle_client, "localhost", self.port)
        print(f"🚀 Telemetry server running on ws://localhost:{self.port}")
        
        # Start broadcasting
        broadcast_task = asyncio.create_task(self.broadcast_telemetry())
        
        try:
            await server.wait_closed()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down telemetry server...")
        finally:
            self.running = False
            broadcast_task.cancel()
            print("✅ Telemetry server stopped")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RC Sandbox Telemetry Server')
    parser.add_argument('--port', type=int, default=8766, help='WebSocket port')
    parser.add_argument('--no-demo', action='store_true', help='Disable demo mode')
    
    args = parser.parse_args()
    
    server = TelemetryServer(port=args.port)
    if args.no_demo:
        server.demo_mode = False
        print("🔧 Demo mode disabled - waiting for real vehicle data")
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()

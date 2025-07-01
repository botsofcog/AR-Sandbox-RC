#!/usr/bin/env python3
"""
Streaming Server - 24/7 Twitch streaming with viewer interaction
Part of the RC Sandbox modular architecture
"""

import asyncio
import websockets
import json
import time
import subprocess
import threading
import queue
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ViewerCommand:
    """Viewer command from Twitch chat"""
    username: str
    command: str
    parameters: List[str]
    timestamp: float
    channel_points: int = 0
    is_subscriber: bool = False
    is_moderator: bool = False

@dataclass
class StreamStats:
    """Stream statistics"""
    viewers: int
    followers: int
    uptime: float
    commands_processed: int
    vehicles_controlled: int
    terrain_modifications: int

class TwitchChatBot:
    """Twitch chat bot for viewer interaction"""
    
    def __init__(self, channel: str, oauth_token: str):
        self.channel = channel
        self.oauth_token = oauth_token
        self.connected = False
        self.command_queue = queue.Queue()
        
        # Command cooldowns (seconds)
        self.command_cooldowns = {
            'excavate': 30,
            'build': 45,
            'flood': 60,
            'vehicle': 20,
            'mission': 120
        }
        
        # User cooldowns
        self.user_cooldowns = {}
        
        # Allowed commands
        self.commands = {
            '!excavate': self.handle_excavate,
            '!build': self.handle_build,
            '!flood': self.handle_flood,
            '!vehicle': self.handle_vehicle,
            '!mission': self.handle_mission,
            '!help': self.handle_help,
            '!status': self.handle_status
        }
        
        logger.info(f"🤖 Twitch bot initialized for channel: {channel}")
    
    async def connect(self):
        """Connect to Twitch IRC"""
        try:
            self.reader, self.writer = await asyncio.open_connection('irc.chat.twitch.tv', 6667)
            
            # Authenticate
            self.writer.write(f"PASS {self.oauth_token}\r\n".encode())
            self.writer.write(f"NICK {self.channel}\r\n".encode())
            self.writer.write(f"JOIN #{self.channel}\r\n".encode())
            await self.writer.drain()
            
            self.connected = True
            logger.info("✅ Connected to Twitch chat")
            
            # Start listening for messages
            asyncio.create_task(self.listen_for_messages())
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Twitch: {e}")
            self.connected = False
    
    async def listen_for_messages(self):
        """Listen for Twitch chat messages"""
        while self.connected:
            try:
                data = await self.reader.read(2048)
                if not data:
                    break
                
                message = data.decode('utf-8', errors='ignore')
                await self.process_message(message)
                
            except Exception as e:
                logger.error(f"❌ Chat message error: {e}")
                break
    
    async def process_message(self, message: str):
        """Process incoming chat message"""
        lines = message.strip().split('\r\n')
        
        for line in lines:
            if 'PRIVMSG' in line:
                await self.handle_chat_message(line)
            elif line.startswith('PING'):
                # Respond to ping to stay connected
                self.writer.write(b"PONG :tmi.twitch.tv\r\n")
                await self.writer.drain()
    
    async def handle_chat_message(self, line: str):
        """Handle individual chat message"""
        try:
            # Parse Twitch IRC message format
            parts = line.split(':', 2)
            if len(parts) < 3:
                return
            
            user_info = parts[1].split('!')[0]
            message_text = parts[2]
            
            # Extract username and check for commands
            username = user_info.split('@')[0] if '@' in user_info else user_info
            
            if message_text.startswith('!'):
                await self.process_command(username, message_text)
                
        except Exception as e:
            logger.error(f"❌ Message parsing error: {e}")
    
    async def process_command(self, username: str, message: str):
        """Process viewer command"""
        parts = message.split()
        command = parts[0].lower()
        parameters = parts[1:] if len(parts) > 1 else []
        
        # Check if command exists
        if command not in self.commands:
            return
        
        # Check cooldowns
        if not self.check_cooldown(username, command):
            await self.send_message(f"@{username} Command on cooldown, please wait!")
            return
        
        # Create command object
        viewer_command = ViewerCommand(
            username=username,
            command=command,
            parameters=parameters,
            timestamp=time.time()
        )
        
        # Add to command queue
        self.command_queue.put(viewer_command)
        
        # Execute command handler
        try:
            await self.commands[command](viewer_command)
        except Exception as e:
            logger.error(f"❌ Command error: {e}")
            await self.send_message(f"@{username} Command failed: {str(e)}")
    
    def check_cooldown(self, username: str, command: str) -> bool:
        """Check if user can use command (not on cooldown)"""
        now = time.time()
        user_key = f"{username}:{command}"
        
        if user_key in self.user_cooldowns:
            time_since_last = now - self.user_cooldowns[user_key]
            cooldown_time = self.command_cooldowns.get(command.replace('!', ''), 30)
            
            if time_since_last < cooldown_time:
                return False
        
        self.user_cooldowns[user_key] = now
        return True
    
    async def send_message(self, message: str):
        """Send message to Twitch chat"""
        if self.connected:
            try:
                self.writer.write(f"PRIVMSG #{self.channel} :{message}\r\n".encode())
                await self.writer.drain()
            except Exception as e:
                logger.error(f"❌ Failed to send message: {e}")
    
    # Command handlers
    async def handle_excavate(self, cmd: ViewerCommand):
        """Handle excavate command"""
        await self.send_message(f"@{cmd.username} 🚜 Excavator deployed! Digging at random location...")
        logger.info(f"🚜 {cmd.username} triggered excavation")
    
    async def handle_build(self, cmd: ViewerCommand):
        """Handle build command"""
        await self.send_message(f"@{cmd.username} 🏗️ Construction started! Building roads...")
        logger.info(f"🏗️ {cmd.username} triggered construction")
    
    async def handle_flood(self, cmd: ViewerCommand):
        """Handle flood defense command"""
        await self.send_message(f"@{cmd.username} 🌊 Flood defense mission activated!")
        logger.info(f"🌊 {cmd.username} triggered flood defense")
    
    async def handle_vehicle(self, cmd: ViewerCommand):
        """Handle vehicle control command"""
        if cmd.parameters:
            vehicle_id = cmd.parameters[0].upper()
            await self.send_message(f"@{cmd.username} 🚛 Controlling {vehicle_id}!")
        else:
            await self.send_message(f"@{cmd.username} 🚛 Random vehicle selected!")
        logger.info(f"🚛 {cmd.username} controlled vehicle")
    
    async def handle_mission(self, cmd: ViewerCommand):
        """Handle mission command"""
        missions = ['flood_defense', 'construction', 'racing', 'recycling']
        mission = cmd.parameters[0] if cmd.parameters else 'random'
        await self.send_message(f"@{cmd.username} 🎯 Mission '{mission}' started!")
        logger.info(f"🎯 {cmd.username} started mission: {mission}")
    
    async def handle_help(self, cmd: ViewerCommand):
        """Handle help command"""
        help_text = "Commands: !excavate !build !flood !vehicle [ID] !mission [type] !status"
        await self.send_message(f"@{cmd.username} {help_text}")
    
    async def handle_status(self, cmd: ViewerCommand):
        """Handle status command"""
        await self.send_message(f"@{cmd.username} 📊 5 vehicles active, terrain live, mission in progress!")

class StreamingServer:
    """24/7 streaming server with viewer interaction"""
    
    def __init__(self, port: int = 8767):
        self.port = port
        self.clients = set()
        self.running = False
        
        # Streaming configuration
        self.stream_config = {
            'rtmp_url': 'rtmp://live.twitch.tv/live/',
            'stream_key': '',  # Set from environment or config
            'resolution': '1920x1080',
            'framerate': 30,
            'bitrate': '3000k',
            'audio_bitrate': '128k'
        }
        
        # FFmpeg process for streaming
        self.ffmpeg_process = None
        
        # Twitch integration
        self.twitch_bot = None
        self.twitch_channel = ''
        self.twitch_oauth = ''
        
        # Stream statistics
        self.stats = StreamStats(
            viewers=0,
            followers=0,
            uptime=0,
            commands_processed=0,
            vehicles_controlled=0,
            terrain_modifications=0
        )
        
        # Autonomous operation
        self.autonomous_mode = True
        self.last_viewer_interaction = time.time()
        self.autonomous_actions = [
            'random_excavation',
            'patrol_vehicles',
            'terrain_smoothing',
            'mission_rotation'
        ]
        
        logger.info(f"🎥 Streaming Server initialized on port {port}")
    
    def configure_stream(self, stream_key: str, channel: str, oauth_token: str):
        """Configure streaming parameters"""
        self.stream_config['stream_key'] = stream_key
        self.twitch_channel = channel
        self.twitch_oauth = oauth_token
        
        # Initialize Twitch bot
        self.twitch_bot = TwitchChatBot(channel, oauth_token)
        
        logger.info(f"📺 Stream configured for channel: {channel}")
    
    async def start_streaming(self):
        """Start FFmpeg streaming process"""
        if not self.stream_config['stream_key']:
            logger.error("❌ No stream key configured")
            return False
        
        try:
            # FFmpeg command for streaming
            ffmpeg_cmd = [
                'ffmpeg',
                '-f', 'gdigrab',  # Screen capture on Windows
                '-framerate', str(self.stream_config['framerate']),
                '-i', 'desktop',
                '-f', 'dshow',  # Audio capture
                '-i', 'audio="Microphone"',
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-b:v', self.stream_config['bitrate'],
                '-maxrate', self.stream_config['bitrate'],
                '-bufsize', '6000k',
                '-c:a', 'aac',
                '-b:a', self.stream_config['audio_bitrate'],
                '-f', 'flv',
                f"{self.stream_config['rtmp_url']}{self.stream_config['stream_key']}"
            ]
            
            self.ffmpeg_process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            logger.info("🎥 FFmpeg streaming started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start streaming: {e}")
            return False
    
    async def stop_streaming(self):
        """Stop streaming process"""
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            self.ffmpeg_process = None
            logger.info("🛑 Streaming stopped")
    
    async def start_server(self):
        """Start the streaming WebSocket server"""
        self.running = True
        
        # Connect to Twitch chat
        if self.twitch_bot:
            await self.twitch_bot.connect()
        
        # Start streaming
        await self.start_streaming()
        
        # Start WebSocket server for internal communication
        server = await websockets.serve(self.handle_client, "localhost", self.port)
        logger.info(f"🚀 Streaming server running on ws://localhost:{self.port}")
        
        # Start autonomous operation
        autonomous_task = asyncio.create_task(self.autonomous_operation())
        
        # Start viewer command processing
        command_task = asyncio.create_task(self.process_viewer_commands())
        
        try:
            await server.wait_closed()
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutting down streaming server...")
        finally:
            self.running = False
            autonomous_task.cancel()
            command_task.cancel()
            await self.stop_streaming()
            logger.info("✅ Streaming server stopped")
    
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connection"""
        self.clients.add(websocket)
        client_addr = websocket.remote_address
        logger.info(f"🔗 Streaming client connected: {client_addr}")
        
        try:
            await websocket.wait_closed()
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            logger.info(f"🔌 Streaming client disconnected: {client_addr}")
    
    async def process_viewer_commands(self):
        """Process commands from Twitch viewers"""
        while self.running:
            if self.twitch_bot and not self.twitch_bot.command_queue.empty():
                try:
                    command = self.twitch_bot.command_queue.get_nowait()
                    await self.execute_viewer_command(command)
                    self.stats.commands_processed += 1
                    self.last_viewer_interaction = time.time()
                    
                except queue.Empty:
                    pass
                except Exception as e:
                    logger.error(f"❌ Command processing error: {e}")
            
            await asyncio.sleep(0.1)
    
    async def execute_viewer_command(self, command: ViewerCommand):
        """Execute viewer command in the sandbox"""
        logger.info(f"🎮 Executing viewer command: {command.command} by {command.username}")
        
        # Convert Twitch command to sandbox action
        sandbox_command = self.convert_to_sandbox_command(command)
        
        # Broadcast to connected clients
        if self.clients:
            message = json.dumps({
                'type': 'viewer_command',
                'command': sandbox_command,
                'viewer': command.username,
                'timestamp': command.timestamp
            })
            
            disconnected = []
            for client in self.clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.append(client)
            
            # Remove disconnected clients
            for client in disconnected:
                self.clients.discard(client)
    
    def convert_to_sandbox_command(self, command: ViewerCommand) -> Dict[str, Any]:
        """Convert Twitch command to sandbox command"""
        if command.command == '!excavate':
            return {
                'action': 'vehicle_command',
                'vehicle_id': 'EX001',
                'command': 'work',
                'work_type': 'excavate'
            }
        elif command.command == '!build':
            return {
                'action': 'vehicle_command',
                'vehicle_id': 'BD001',
                'command': 'work',
                'work_type': 'level'
            }
        elif command.command == '!flood':
            return {
                'action': 'start_mission',
                'mission_type': 'flood_defense'
            }
        elif command.command == '!vehicle':
            vehicle_id = command.parameters[0] if command.parameters else 'EX001'
            return {
                'action': 'select_vehicle',
                'vehicle_id': vehicle_id.upper()
            }
        elif command.command == '!mission':
            mission_type = command.parameters[0] if command.parameters else 'flood_defense'
            return {
                'action': 'start_mission',
                'mission_type': mission_type
            }
        else:
            return {'action': 'unknown', 'original_command': command.command}
    
    async def autonomous_operation(self):
        """Autonomous operation when no viewers are interacting"""
        while self.running:
            # Check if we should run autonomous actions
            time_since_interaction = time.time() - self.last_viewer_interaction
            
            if self.autonomous_mode and time_since_interaction > 60:  # 1 minute of inactivity
                await self.perform_autonomous_action()
            
            await asyncio.sleep(30)  # Check every 30 seconds
    
    async def perform_autonomous_action(self):
        """Perform autonomous action to keep stream interesting"""
        import random
        
        action = random.choice(self.autonomous_actions)
        logger.info(f"🤖 Autonomous action: {action}")
        
        if action == 'random_excavation':
            # Random excavation
            sandbox_command = {
                'action': 'vehicle_command',
                'vehicle_id': 'EX001',
                'command': 'work',
                'work_type': 'excavate',
                'autonomous': True
            }
        elif action == 'patrol_vehicles':
            # Vehicle patrol
            sandbox_command = {
                'action': 'fleet_command',
                'command': 'patrol_mode',
                'autonomous': True
            }
        elif action == 'terrain_smoothing':
            # Terrain smoothing
            sandbox_command = {
                'action': 'vehicle_command',
                'vehicle_id': 'CP001',
                'command': 'work',
                'work_type': 'smooth',
                'autonomous': True
            }
        elif action == 'mission_rotation':
            # Rotate through missions
            missions = ['flood_defense', 'construction_contract', 'racing_circuit']
            mission = random.choice(missions)
            sandbox_command = {
                'action': 'start_mission',
                'mission_type': mission,
                'autonomous': True
            }
        
        # Broadcast autonomous action
        if self.clients:
            message = json.dumps({
                'type': 'autonomous_action',
                'command': sandbox_command,
                'timestamp': time.time()
            })
            
            for client in self.clients:
                try:
                    await client.send(message)
                except:
                    pass
    
    def get_stream_stats(self) -> Dict[str, Any]:
        """Get current stream statistics"""
        self.stats.uptime = time.time() - getattr(self, 'start_time', time.time())
        
        return {
            'stats': asdict(self.stats),
            'autonomous_mode': self.autonomous_mode,
            'streaming': self.ffmpeg_process is not None,
            'twitch_connected': self.twitch_bot.connected if self.twitch_bot else False,
            'connected_clients': len(self.clients)
        }

def main():
    """Main entry point"""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='RC Sandbox Streaming Server')
    parser.add_argument('--port', type=int, default=8767, help='WebSocket port')
    parser.add_argument('--channel', type=str, required=True, help='Twitch channel name')
    parser.add_argument('--stream-key', type=str, help='Twitch stream key')
    parser.add_argument('--oauth-token', type=str, help='Twitch OAuth token')
    
    args = parser.parse_args()
    
    # Get credentials from environment if not provided
    stream_key = args.stream_key or os.getenv('TWITCH_STREAM_KEY')
    oauth_token = args.oauth_token or os.getenv('TWITCH_OAUTH_TOKEN')
    
    if not stream_key or not oauth_token:
        logger.error("❌ Missing Twitch credentials")
        logger.info("Set TWITCH_STREAM_KEY and TWITCH_OAUTH_TOKEN environment variables")
        return
    
    server = StreamingServer(port=args.port)
    server.configure_stream(stream_key, args.channel, oauth_token)
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logger.info("\n👋 Goodbye!")

if __name__ == "__main__":
    main()

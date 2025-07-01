#!/usr/bin/env python3
"""
Kinect Calibration System - Playing card + hockey puck calibration
Part of the RC Sandbox hardware integration layer
"""

import cv2
import numpy as np
import json
import time
import asyncio
import websockets
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

@dataclass
class CalibrationPoint:
    """Calibration reference point"""
    real_world_x: float  # Real world coordinates in feet
    real_world_y: float
    real_world_z: float
    pixel_x: int         # Pixel coordinates in depth image
    pixel_y: int
    depth_value: float   # Depth sensor reading
    confidence: float    # Detection confidence (0-1)

@dataclass
class CalibrationResult:
    """Complete calibration result"""
    transformation_matrix: np.ndarray
    sandbox_bounds: Dict[str, float]
    depth_range: Dict[str, float]
    pixel_to_world_scale: float
    calibration_error: float
    timestamp: float

class KinectCalibrator:
    """Kinect depth sensor calibration using playing cards and hockey pucks"""
    
    def __init__(self, kinect_type='azure'):
        self.kinect_type = kinect_type  # 'azure' or 'xbox360'
        self.depth_source = None
        self.color_source = None
        
        # Calibration parameters
        self.sandbox_width_feet = 10.0
        self.sandbox_height_feet = 7.5
        self.sandbox_depth_feet = 1.0
        
        # Reference objects
        self.playing_card_size = (3.5, 2.5)  # inches
        self.hockey_puck_diameter = 3.0      # inches
        self.hockey_puck_height = 1.0        # inches
        
        # Calibration state
        self.calibration_points = []
        self.current_calibration = None
        self.is_calibrated = False
        
        # Detection parameters
        self.card_detector = self.setup_card_detector()
        self.puck_detector = self.setup_puck_detector()
        
        print(f"🎯 Kinect Calibrator initialized ({kinect_type})")
    
    def setup_card_detector(self):
        """Setup playing card detection using contour analysis"""
        return {
            'min_area': 1000,
            'max_area': 50000,
            'aspect_ratio_range': (1.2, 1.6),  # Playing card aspect ratio
            'contour_approximation': 0.02
        }
    
    def setup_puck_detector(self):
        """Setup hockey puck detection using circular Hough transform"""
        return {
            'min_radius': 20,
            'max_radius': 100,
            'min_dist': 50,
            'param1': 50,
            'param2': 30
        }
    
    def initialize_kinect(self):
        """Initialize Kinect sensor based on type"""
        try:
            if self.kinect_type == 'azure':
                return self.initialize_azure_kinect()
            elif self.kinect_type == 'xbox360':
                return self.initialize_xbox360_kinect()
            else:
                raise ValueError(f"Unsupported Kinect type: {self.kinect_type}")
                
        except Exception as e:
            print(f"❌ Kinect initialization failed: {e}")
            print("🔄 Falling back to webcam simulation")
            return self.initialize_webcam_fallback()
    
    def initialize_azure_kinect(self):
        """Initialize Azure Kinect DK"""
        try:
            from pykinect_azure import pykinect_azure as pykinect
            
            pykinect.initialize_libraries()
            
            device_config = pykinect.default_configuration
            device_config.color_format = pykinect.K4A_IMAGE_FORMAT_COLOR_BGRA32
            device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_720P
            device_config.depth_mode = pykinect.K4A_DEPTH_MODE_NFOV_UNBINNED
            device_config.camera_fps = pykinect.K4A_FRAMES_PER_SECOND_30
            
            self.depth_source = pykinect.start_device(config=device_config)
            print("✅ Azure Kinect DK initialized")
            return True
            
        except ImportError:
            print("❌ Azure Kinect SDK not found")
            return False
        except Exception as e:
            print(f"❌ Azure Kinect error: {e}")
            return False
    
    def initialize_xbox360_kinect(self):
        """Initialize Xbox 360 Kinect via libfreenect"""
        try:
            import freenect
            
            # Test Kinect connection
            ctx = freenect.init()
            if freenect.num_devices(ctx) == 0:
                print("❌ No Xbox 360 Kinect devices found")
                return False
            
            self.depth_source = freenect
            print("✅ Xbox 360 Kinect initialized")
            return True
            
        except ImportError:
            print("❌ libfreenect not found")
            return False
        except Exception as e:
            print(f"❌ Xbox 360 Kinect error: {e}")
            return False
    
    def initialize_webcam_fallback(self):
        """Fallback to webcam for testing"""
        self.depth_source = cv2.VideoCapture(0)
        if self.depth_source.isOpened():
            print("✅ Webcam fallback initialized")
            return True
        else:
            print("❌ No camera sources available")
            return False
    
    def get_depth_frame(self):
        """Get current depth frame from sensor"""
        if self.kinect_type == 'azure':
            return self.get_azure_depth_frame()
        elif self.kinect_type == 'xbox360':
            return self.get_xbox360_depth_frame()
        else:
            return self.get_webcam_depth_frame()
    
    def get_azure_depth_frame(self):
        """Get depth frame from Azure Kinect"""
        try:
            capture = self.depth_source.update()
            ret_depth, depth_image = capture.get_depth_image()
            ret_color, color_image = capture.get_color_image()
            
            if ret_depth and ret_color:
                return depth_image, color_image
            return None, None
            
        except Exception as e:
            print(f"❌ Azure Kinect frame error: {e}")
            return None, None
    
    def get_xbox360_depth_frame(self):
        """Get depth frame from Xbox 360 Kinect"""
        try:
            import freenect
            
            depth, _ = freenect.sync_get_depth()
            rgb, _ = freenect.sync_get_video()
            
            # Convert to proper format
            depth_image = depth.astype(np.uint16)
            color_image = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            
            return depth_image, color_image
            
        except Exception as e:
            print(f"❌ Xbox 360 Kinect frame error: {e}")
            return None, None
    
    def get_webcam_depth_frame(self):
        """Simulate depth from webcam (for testing)"""
        ret, frame = self.depth_source.read()
        if ret:
            # Create simulated depth from grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            depth_sim = (255 - gray).astype(np.uint16) * 20  # Scale to depth range
            return depth_sim, frame
        return None, None
    
    def detect_playing_cards(self, color_image):
        """Detect playing cards in the image"""
        gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to find white cards
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        cards = []
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if (self.card_detector['min_area'] < area < self.card_detector['max_area']):
                # Approximate contour to rectangle
                epsilon = self.card_detector['contour_approximation'] * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                if len(approx) == 4:  # Rectangle
                    # Check aspect ratio
                    rect = cv2.boundingRect(approx)
                    aspect_ratio = rect[2] / rect[3]
                    
                    if (self.card_detector['aspect_ratio_range'][0] <= aspect_ratio <= 
                        self.card_detector['aspect_ratio_range'][1]):
                        
                        # Calculate center
                        M = cv2.moments(contour)
                        if M['m00'] != 0:
                            cx = int(M['m10'] / M['m00'])
                            cy = int(M['m01'] / M['m00'])
                            
                            cards.append({
                                'center': (cx, cy),
                                'contour': approx,
                                'area': area,
                                'confidence': min(1.0, area / 10000)
                            })
        
        return cards
    
    def detect_hockey_pucks(self, color_image):
        """Detect hockey pucks using circular detection"""
        gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        
        # Detect circles using HoughCircles
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=self.puck_detector['min_dist'],
            param1=self.puck_detector['param1'],
            param2=self.puck_detector['param2'],
            minRadius=self.puck_detector['min_radius'],
            maxRadius=self.puck_detector['max_radius']
        )
        
        pucks = []
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            
            for (x, y, r) in circles:
                # Verify it's actually a puck by checking color/texture
                confidence = self.verify_puck(gray, x, y, r)
                
                if confidence > 0.5:
                    pucks.append({
                        'center': (x, y),
                        'radius': r,
                        'confidence': confidence
                    })
        
        return pucks
    
    def verify_puck(self, gray_image, x, y, radius):
        """Verify detected circle is actually a hockey puck"""
        # Check if the detected circle has puck-like characteristics
        mask = np.zeros(gray_image.shape, dtype=np.uint8)
        cv2.circle(mask, (x, y), radius, 255, -1)
        
        # Calculate mean intensity inside circle
        mean_intensity = cv2.mean(gray_image, mask=mask)[0]
        
        # Hockey pucks are typically dark
        if mean_intensity < 100:  # Dark object
            return 0.8
        else:
            return 0.3
    
    def add_calibration_point(self, real_x, real_y, real_z, pixel_x, pixel_y, depth_value, confidence=1.0):
        """Add a calibration point"""
        point = CalibrationPoint(
            real_world_x=real_x,
            real_world_y=real_y,
            real_world_z=real_z,
            pixel_x=pixel_x,
            pixel_y=pixel_y,
            depth_value=depth_value,
            confidence=confidence
        )
        
        self.calibration_points.append(point)
        print(f"📍 Added calibration point: Real({real_x:.2f}, {real_y:.2f}, {real_z:.2f}) -> Pixel({pixel_x}, {pixel_y})")
    
    def perform_calibration(self):
        """Perform calibration calculation using collected points"""
        if len(self.calibration_points) < 4:
            print("❌ Need at least 4 calibration points")
            return False
        
        print(f"🔧 Performing calibration with {len(self.calibration_points)} points...")
        
        # Prepare point arrays
        real_points = np.array([[p.real_world_x, p.real_world_y, p.real_world_z] 
                               for p in self.calibration_points], dtype=np.float32)
        pixel_points = np.array([[p.pixel_x, p.pixel_y, p.depth_value] 
                                for p in self.calibration_points], dtype=np.float32)
        
        # Calculate transformation matrix using least squares
        transformation_matrix = self.calculate_transformation_matrix(real_points, pixel_points)
        
        # Calculate calibration error
        calibration_error = self.calculate_calibration_error(transformation_matrix, real_points, pixel_points)
        
        # Determine sandbox bounds
        sandbox_bounds = {
            'min_x': 0, 'max_x': self.sandbox_width_feet,
            'min_y': 0, 'max_y': self.sandbox_height_feet,
            'min_z': 0, 'max_z': self.sandbox_depth_feet
        }
        
        # Determine depth range
        depth_values = [p.depth_value for p in self.calibration_points]
        depth_range = {
            'min_depth': min(depth_values),
            'max_depth': max(depth_values)
        }
        
        # Calculate pixel to world scale
        pixel_distances = [np.linalg.norm([p.pixel_x, p.pixel_y]) for p in self.calibration_points]
        world_distances = [np.linalg.norm([p.real_world_x, p.real_world_y]) for p in self.calibration_points]
        pixel_to_world_scale = np.mean(np.array(world_distances) / np.array(pixel_distances))
        
        # Create calibration result
        self.current_calibration = CalibrationResult(
            transformation_matrix=transformation_matrix,
            sandbox_bounds=sandbox_bounds,
            depth_range=depth_range,
            pixel_to_world_scale=pixel_to_world_scale,
            calibration_error=calibration_error,
            timestamp=time.time()
        )
        
        self.is_calibrated = True
        
        print(f"✅ Calibration complete! Error: {calibration_error:.4f}")
        print(f"📏 Scale: {pixel_to_world_scale:.4f} feet/pixel")
        
        return True
    
    def calculate_transformation_matrix(self, real_points, pixel_points):
        """Calculate 3D transformation matrix"""
        # Use least squares to find best fit transformation
        # This is a simplified version - in practice you'd use more sophisticated methods
        
        # For now, use a simple affine transformation
        A = np.column_stack([pixel_points, np.ones(len(pixel_points))])
        transformation_matrix, _, _, _ = np.linalg.lstsq(A, real_points, rcond=None)
        
        return transformation_matrix
    
    def calculate_calibration_error(self, transformation_matrix, real_points, pixel_points):
        """Calculate RMS calibration error"""
        A = np.column_stack([pixel_points, np.ones(len(pixel_points))])
        predicted_real = A @ transformation_matrix
        
        errors = np.linalg.norm(predicted_real - real_points, axis=1)
        rms_error = np.sqrt(np.mean(errors ** 2))
        
        return rms_error
    
    def pixel_to_world(self, pixel_x, pixel_y, depth_value):
        """Convert pixel coordinates to real world coordinates"""
        if not self.is_calibrated:
            return None
        
        pixel_point = np.array([pixel_x, pixel_y, depth_value, 1])
        world_point = pixel_point @ self.current_calibration.transformation_matrix
        
        return {
            'x': world_point[0],
            'y': world_point[1], 
            'z': world_point[2]
        }
    
    def world_to_pixel(self, world_x, world_y, world_z):
        """Convert world coordinates to pixel coordinates (approximate)"""
        if not self.is_calibrated:
            return None
        
        # This would require the inverse transformation
        # Simplified implementation for now
        scale = 1.0 / self.current_calibration.pixel_to_world_scale
        
        return {
            'x': int(world_x * scale),
            'y': int(world_y * scale),
            'depth': world_z * 1000  # Convert to mm
        }
    
    def save_calibration(self, filename):
        """Save calibration to file"""
        if not self.is_calibrated:
            print("❌ No calibration to save")
            return False
        
        calibration_data = {
            'transformation_matrix': self.current_calibration.transformation_matrix.tolist(),
            'sandbox_bounds': self.current_calibration.sandbox_bounds,
            'depth_range': self.current_calibration.depth_range,
            'pixel_to_world_scale': self.current_calibration.pixel_to_world_scale,
            'calibration_error': self.current_calibration.calibration_error,
            'timestamp': self.current_calibration.timestamp,
            'kinect_type': self.kinect_type,
            'calibration_points': [asdict(p) for p in self.calibration_points]
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(calibration_data, f, indent=2)
            print(f"✅ Calibration saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Failed to save calibration: {e}")
            return False
    
    def load_calibration(self, filename):
        """Load calibration from file"""
        try:
            with open(filename, 'r') as f:
                calibration_data = json.load(f)
            
            self.current_calibration = CalibrationResult(
                transformation_matrix=np.array(calibration_data['transformation_matrix']),
                sandbox_bounds=calibration_data['sandbox_bounds'],
                depth_range=calibration_data['depth_range'],
                pixel_to_world_scale=calibration_data['pixel_to_world_scale'],
                calibration_error=calibration_data['calibration_error'],
                timestamp=calibration_data['timestamp']
            )
            
            # Restore calibration points
            self.calibration_points = [
                CalibrationPoint(**point_data) 
                for point_data in calibration_data['calibration_points']
            ]
            
            self.is_calibrated = True
            print(f"✅ Calibration loaded from {filename}")
            print(f"📏 Error: {self.current_calibration.calibration_error:.4f}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load calibration: {e}")
            return False
    
    def run_interactive_calibration(self):
        """Run interactive calibration session"""
        print("\n🎯 INTERACTIVE KINECT CALIBRATION")
        print("=" * 50)
        print("📋 Instructions:")
        print("1. Place playing cards at known positions in sandbox")
        print("2. Place hockey pucks at known heights")
        print("3. Press 'c' to capture calibration point")
        print("4. Press 'q' to finish and calculate calibration")
        print("5. Press 'r' to reset calibration points")
        print()
        
        if not self.initialize_kinect():
            return False
        
        self.calibration_points = []
        
        while True:
            depth_frame, color_frame = self.get_depth_frame()
            
            if depth_frame is None or color_frame is None:
                continue
            
            # Detect reference objects
            cards = self.detect_playing_cards(color_frame)
            pucks = self.detect_hockey_pucks(color_frame)
            
            # Draw detections
            display_frame = color_frame.copy()
            
            # Draw detected cards
            for card in cards:
                cv2.circle(display_frame, card['center'], 5, (0, 255, 0), -1)
                cv2.putText(display_frame, 'CARD', 
                           (card['center'][0] - 20, card['center'][1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Draw detected pucks
            for puck in pucks:
                cv2.circle(display_frame, puck['center'], puck['radius'], (255, 0, 0), 2)
                cv2.putText(display_frame, 'PUCK', 
                           (puck['center'][0] - 20, puck['center'][1] - 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            
            # Draw calibration points
            for i, point in enumerate(self.calibration_points):
                cv2.circle(display_frame, (point.pixel_x, point.pixel_y), 8, (0, 0, 255), -1)
                cv2.putText(display_frame, f'{i+1}', 
                           (point.pixel_x + 10, point.pixel_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            # Show status
            status_text = f"Calibration Points: {len(self.calibration_points)}/4+ | Cards: {len(cards)} | Pucks: {len(pucks)}"
            cv2.putText(display_frame, status_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Kinect Calibration', display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('c'):
                # Capture calibration point
                self.capture_calibration_point(cards, pucks, depth_frame)
            elif key == ord('r'):
                # Reset calibration points
                self.calibration_points = []
                print("🔄 Calibration points reset")
            elif key == ord('q'):
                # Finish calibration
                break
        
        cv2.destroyAllWindows()
        
        if len(self.calibration_points) >= 4:
            return self.perform_calibration()
        else:
            print("❌ Need at least 4 calibration points")
            return False
    
    def capture_calibration_point(self, cards, pucks, depth_frame):
        """Capture a calibration point interactively"""
        if not cards and not pucks:
            print("⚠️ No reference objects detected")
            return
        
        print("\n📍 Capturing calibration point...")
        
        # Get real world coordinates from user
        try:
            real_x = float(input("Enter real world X coordinate (feet): "))
            real_y = float(input("Enter real world Y coordinate (feet): "))
            real_z = float(input("Enter real world Z coordinate (feet): "))
            
            # Use the first detected object
            if cards:
                obj = cards[0]
                obj_type = "card"
            else:
                obj = pucks[0]
                obj_type = "puck"
            
            pixel_x, pixel_y = obj['center']
            depth_value = depth_frame[pixel_y, pixel_x]
            confidence = obj['confidence']
            
            self.add_calibration_point(real_x, real_y, real_z, pixel_x, pixel_y, 
                                     depth_value, confidence)
            
            print(f"✅ Calibration point added using {obj_type}")
            
        except ValueError:
            print("❌ Invalid coordinates entered")
        except Exception as e:
            print(f"❌ Error capturing point: {e}")

def main():
    """Main calibration program"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Kinect Calibration System')
    parser.add_argument('--kinect', choices=['azure', 'xbox360'], default='azure',
                       help='Kinect type to use')
    parser.add_argument('--load', type=str, help='Load existing calibration file')
    parser.add_argument('--save', type=str, default='kinect_calibration.json',
                       help='Save calibration to file')
    
    args = parser.parse_args()
    
    calibrator = KinectCalibrator(kinect_type=args.kinect)
    
    if args.load:
        if calibrator.load_calibration(args.load):
            print("✅ Existing calibration loaded successfully")
        else:
            print("❌ Failed to load calibration, starting fresh")
    
    # Run interactive calibration
    if calibrator.run_interactive_calibration():
        calibrator.save_calibration(args.save)
        print(f"\n🎉 Calibration complete and saved to {args.save}")
    else:
        print("\n❌ Calibration failed")

class CalibrationWebSocketServer:
    """WebSocket server for real-time calibration data"""

    def __init__(self, calibrator: KinectCalibrator, port: int = 8083):
        self.calibrator = calibrator
        self.port = port
        self.logger = logging.getLogger(__name__)

    async def handle_client(self, websocket, path):
        """Handle WebSocket client connections"""
        self.logger.info(f"🔗 Calibration client connected: {websocket.remote_address}")

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    response = await self.process_message(data)
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "error": "Invalid JSON format"
                    }))
                except Exception as e:
                    self.logger.error(f"❌ Error processing message: {e}")
                    await websocket.send(json.dumps({
                        "error": str(e)
                    }))

        except websockets.exceptions.ConnectionClosed:
            self.logger.info("🔌 Calibration client disconnected")
        except Exception as e:
            self.logger.error(f"❌ WebSocket error: {e}")

    async def process_message(self, data: dict) -> dict:
        """Process incoming WebSocket messages"""
        command = data.get("command")

        if command == "get_status":
            return {
                "status": "ready",
                "calibrated": self.calibrator.is_calibrated(),
                "points_count": len(self.calibrator.calibration_points)
            }
        elif command == "get_calibration":
            return {
                "calibration_matrix": self.calibrator.transformation_matrix.tolist() if self.calibrator.transformation_matrix is not None else None,
                "points": [asdict(point) for point in self.calibrator.calibration_points]
            }
        elif command == "reset_calibration":
            self.calibrator.calibration_points.clear()
            self.calibrator.transformation_matrix = None
            return {"status": "reset_complete"}
        else:
            return {"error": f"Unknown command: {command}"}

    async def start_server(self):
        """Start the WebSocket server"""
        self.logger.info(f"🚀 Starting calibration WebSocket server on port {self.port}")

        async with websockets.serve(self.handle_client, "localhost", self.port):
            self.logger.info(f"✅ Calibration WebSocket server running on ws://localhost:{self.port}")
            await asyncio.Future()  # Run forever

def start_websocket_server(port: int = 8083):
    """Start calibration WebSocket server"""
    calibrator = KinectCalibrator()
    server = CalibrationWebSocketServer(calibrator, port)

    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        print("\n🛑 Calibration WebSocket server stopped")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Advanced Topography Renderer
Combines Kinect depth data + webcam RGB data to create rich topographical information for AI
"""

import cv2
import numpy as np
import logging
from typing import Dict, Any, Optional, Tuple
import json
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TopographyData:
    """Rich topographical data structure"""
    height_map: np.ndarray          # Raw height data from Kinect
    rgb_overlay: np.ndarray         # RGB data from webcam
    contour_lines: np.ndarray       # Generated contour lines
    elevation_zones: np.ndarray     # Color-coded elevation zones
    terrain_features: Dict[str, Any] # Detected terrain features
    ai_metadata: Dict[str, Any]     # Metadata for AI processing
    timestamp: float                # Data timestamp

class TopographyRenderer:
    """Advanced topography renderer combining Kinect + webcam data"""
    
    def __init__(self):
        self.calibration_data = None
        self.height_range = (500, 2000)  # Kinect depth range in mm
        self.contour_levels = 20         # Number of contour lines
        self.color_map = self._create_topographic_colormap()
        
        # AI-focused feature detection
        self.feature_detectors = {
            'peaks': self._detect_peaks,
            'valleys': self._detect_valleys,
            'ridges': self._detect_ridges,
            'slopes': self._calculate_slopes,
            'water_areas': self._detect_water_areas,
            'vegetation': self._detect_vegetation
        }
        
    def _create_topographic_colormap(self) -> np.ndarray:
        """Create topographic color map (blue=low, green=mid, brown=high, white=peaks)"""
        colors = np.array([
            [139, 69, 19],    # Brown (high elevation)
            [160, 82, 45],    # Saddle brown
            [210, 180, 140],  # Tan
            [240, 230, 140],  # Khaki
            [154, 205, 50],   # Yellow green
            [34, 139, 34],    # Forest green
            [0, 100, 0],      # Dark green
            [0, 191, 255],    # Deep sky blue
            [0, 0, 255],      # Blue (low elevation)
            [25, 25, 112]     # Midnight blue (water)
        ], dtype=np.uint8)
        return colors
    
    def render_topography(self, kinect_depth: np.ndarray, webcam_rgb: np.ndarray) -> TopographyData:
        """
        Main rendering function - combines Kinect depth + webcam RGB into rich topography
        """
        logger.debug("Rendering topography from Kinect + webcam data")
        
        # Step 1: Process and align data
        aligned_depth, aligned_rgb = self._align_data_sources(kinect_depth, webcam_rgb)
        
        # Step 2: Generate height map
        height_map = self._process_depth_to_height(aligned_depth)
        
        # Step 3: Generate contour lines
        contour_lines = self._generate_contour_lines(height_map)
        
        # Step 4: Create elevation zones
        elevation_zones = self._create_elevation_zones(height_map)
        
        # Step 5: Detect terrain features for AI
        terrain_features = self._detect_terrain_features(height_map, aligned_rgb)
        
        # Step 6: Generate AI metadata
        ai_metadata = self._generate_ai_metadata(height_map, aligned_rgb, terrain_features)
        
        # Step 7: Create final RGB overlay
        rgb_overlay = self._create_rgb_overlay(aligned_rgb, elevation_zones, contour_lines)
        
        return TopographyData(
            height_map=height_map,
            rgb_overlay=rgb_overlay,
            contour_lines=contour_lines,
            elevation_zones=elevation_zones,
            terrain_features=terrain_features,
            ai_metadata=ai_metadata,
            timestamp=time.time()
        )
    
    def _align_data_sources(self, kinect_depth: np.ndarray, webcam_rgb: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Align Kinect depth data with webcam RGB data"""
        # Resize both to common resolution
        target_size = (640, 480)
        
        if kinect_depth.shape[:2] != target_size[::-1]:
            aligned_depth = cv2.resize(kinect_depth, target_size)
        else:
            aligned_depth = kinect_depth.copy()
            
        if webcam_rgb.shape[:2] != target_size[::-1]:
            aligned_rgb = cv2.resize(webcam_rgb, target_size)
        else:
            aligned_rgb = webcam_rgb.copy()
        
        # Apply calibration if available
        if self.calibration_data:
            aligned_depth, aligned_rgb = self._apply_calibration(aligned_depth, aligned_rgb)
        
        return aligned_depth, aligned_rgb
    
    def _process_depth_to_height(self, depth_data: np.ndarray) -> np.ndarray:
        """Convert Kinect depth data to normalized height map"""
        # Filter invalid depth values
        valid_mask = (depth_data > self.height_range[0]) & (depth_data < self.height_range[1])
        
        # Create height map (invert depth - closer = higher)
        height_map = np.zeros_like(depth_data, dtype=np.float32)
        height_map[valid_mask] = self.height_range[1] - depth_data[valid_mask]
        
        # Normalize to 0-1 range
        if height_map.max() > height_map.min():
            height_map = (height_map - height_map.min()) / (height_map.max() - height_map.min())
        
        # Apply smoothing
        height_map = cv2.GaussianBlur(height_map, (5, 5), 1.0)
        
        return height_map
    
    def _generate_contour_lines(self, height_map: np.ndarray) -> np.ndarray:
        """Generate topographic contour lines"""
        contour_image = np.zeros(height_map.shape[:2], dtype=np.uint8)
        
        # Generate contour levels
        levels = np.linspace(0, 1, self.contour_levels)
        
        for level in levels:
            # Create binary mask for this elevation level
            level_mask = np.abs(height_map - level) < 0.02
            
            # Find contours
            contours, _ = cv2.findContours(level_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Draw contours
            cv2.drawContours(contour_image, contours, -1, 255, 1)
        
        return contour_image
    
    def _create_elevation_zones(self, height_map: np.ndarray) -> np.ndarray:
        """Create color-coded elevation zones"""
        # Quantize height map into zones
        num_zones = len(self.color_map)
        zone_indices = (height_map * (num_zones - 1)).astype(np.int32)
        zone_indices = np.clip(zone_indices, 0, num_zones - 1)
        
        # Apply color map
        elevation_zones = self.color_map[zone_indices]
        
        return elevation_zones
    
    def _detect_terrain_features(self, height_map: np.ndarray, rgb_data: np.ndarray) -> Dict[str, Any]:
        """Detect terrain features for AI analysis"""
        features = {}
        
        for feature_name, detector_func in self.feature_detectors.items():
            try:
                features[feature_name] = detector_func(height_map, rgb_data)
            except Exception as e:
                logger.warning(f"Feature detection failed for {feature_name}: {e}")
                features[feature_name] = None
        
        return features
    
    def _detect_peaks(self, height_map: np.ndarray, rgb_data: np.ndarray) -> Dict[str, Any]:
        """Detect peaks and high points"""
        # Find local maxima
        kernel = np.ones((5, 5), np.uint8)
        local_maxima = cv2.dilate(height_map, kernel) == height_map
        
        # Filter by minimum height threshold
        peak_threshold = np.percentile(height_map[height_map > 0], 80)
        peaks = local_maxima & (height_map > peak_threshold)
        
        # Find peak coordinates
        peak_coords = np.column_stack(np.where(peaks))
        
        return {
            'count': len(peak_coords),
            'coordinates': peak_coords.tolist(),
            'average_height': float(np.mean(height_map[peaks])) if len(peak_coords) > 0 else 0.0
        }
    
    def _detect_valleys(self, height_map: np.ndarray, rgb_data: np.ndarray) -> Dict[str, Any]:
        """Detect valleys and low points"""
        # Find local minima
        kernel = np.ones((5, 5), np.uint8)
        local_minima = cv2.erode(height_map, kernel) == height_map
        
        # Filter by maximum height threshold
        valley_threshold = np.percentile(height_map[height_map > 0], 20)
        valleys = local_minima & (height_map < valley_threshold) & (height_map > 0)
        
        # Find valley coordinates
        valley_coords = np.column_stack(np.where(valleys))
        
        return {
            'count': len(valley_coords),
            'coordinates': valley_coords.tolist(),
            'average_depth': float(np.mean(height_map[valleys])) if len(valley_coords) > 0 else 0.0
        }
    
    def _detect_ridges(self, height_map: np.ndarray, rgb_data: np.ndarray) -> Dict[str, Any]:
        """Detect ridges and linear high features"""
        # Calculate gradients
        grad_x = cv2.Sobel(height_map.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(height_map.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
        
        # Calculate ridge strength
        ridge_strength = np.sqrt(grad_x**2 + grad_y**2)
        
        # Threshold for ridge detection
        ridge_threshold = np.percentile(ridge_strength, 85)
        ridges = ridge_strength > ridge_threshold
        
        return {
            'total_length': float(np.sum(ridges)),
            'average_strength': float(np.mean(ridge_strength[ridges])) if np.any(ridges) else 0.0
        }
    
    def _calculate_slopes(self, height_map: np.ndarray, rgb_data: np.ndarray) -> Dict[str, Any]:
        """Calculate slope information"""
        # Calculate gradients
        grad_x = cv2.Sobel(height_map.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(height_map.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
        
        # Calculate slope magnitude
        slope_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Calculate slope angle in degrees
        slope_angle = np.arctan(slope_magnitude) * 180 / np.pi
        
        return {
            'average_slope': float(np.mean(slope_angle)),
            'max_slope': float(np.max(slope_angle)),
            'steep_areas_percent': float(np.sum(slope_angle > 30) / slope_angle.size * 100)
        }
    
    def _detect_water_areas(self, height_map: np.ndarray, rgb_data: np.ndarray) -> Dict[str, Any]:
        """Detect potential water areas using both height and color"""
        # Low elevation areas
        water_height_threshold = np.percentile(height_map[height_map > 0], 10)
        low_areas = height_map < water_height_threshold
        
        # Blue color detection in RGB
        hsv = cv2.cvtColor(rgb_data, cv2.COLOR_BGR2HSV)
        blue_mask = cv2.inRange(hsv, (100, 50, 50), (130, 255, 255))
        
        # Combine height and color information
        water_areas = low_areas & (blue_mask > 0)
        
        return {
            'total_area': float(np.sum(water_areas)),
            'percentage': float(np.sum(water_areas) / water_areas.size * 100)
        }
    
    def _detect_vegetation(self, height_map: np.ndarray, rgb_data: np.ndarray) -> Dict[str, Any]:
        """Detect vegetation using color analysis"""
        # Green color detection
        hsv = cv2.cvtColor(rgb_data, cv2.COLOR_BGR2HSV)
        green_mask = cv2.inRange(hsv, (40, 40, 40), (80, 255, 255))
        
        return {
            'total_area': float(np.sum(green_mask > 0)),
            'percentage': float(np.sum(green_mask > 0) / green_mask.size * 100)
        }
    
    def _generate_ai_metadata(self, height_map: np.ndarray, rgb_data: np.ndarray, features: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive metadata for AI processing"""
        return {
            'terrain_stats': {
                'min_elevation': float(np.min(height_map)),
                'max_elevation': float(np.max(height_map)),
                'mean_elevation': float(np.mean(height_map)),
                'elevation_std': float(np.std(height_map)),
                'terrain_roughness': float(np.std(cv2.Laplacian(height_map.astype(np.float32), cv2.CV_32F)))
            },
            'color_stats': {
                'dominant_colors': self._get_dominant_colors(rgb_data),
                'brightness': float(np.mean(cv2.cvtColor(rgb_data, cv2.COLOR_BGR2GRAY))),
                'contrast': float(np.std(cv2.cvtColor(rgb_data, cv2.COLOR_BGR2GRAY)))
            },
            'features': features,
            'recommendations': self._generate_ai_recommendations(height_map, features)
        }
    
    def _get_dominant_colors(self, rgb_data: np.ndarray, k: int = 5) -> list:
        """Extract dominant colors using k-means clustering"""
        # Reshape image to be a list of pixels
        pixels = rgb_data.reshape(-1, 3).astype(np.float32)
        
        # Apply k-means clustering
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Convert centers back to uint8 and return as list
        return centers.astype(np.uint8).tolist()
    
    def _generate_ai_recommendations(self, height_map: np.ndarray, features: Dict[str, Any]) -> Dict[str, str]:
        """Generate AI recommendations based on terrain analysis"""
        recommendations = {}
        
        # Terrain complexity analysis
        terrain_roughness = np.std(cv2.Laplacian(height_map.astype(np.float32), cv2.CV_32F))
        if terrain_roughness > 0.1:
            recommendations['terrain'] = "Complex terrain detected - suitable for advanced construction challenges"
        else:
            recommendations['terrain'] = "Smooth terrain detected - ideal for basic construction projects"
        
        # Water feature recommendations
        if features.get('water_areas', {}).get('percentage', 0) > 5:
            recommendations['water'] = "Water features detected - consider drainage and bridge construction"
        
        # Slope analysis
        slopes = features.get('slopes', {})
        if slopes and slopes.get('steep_areas_percent', 0) > 20:
            recommendations['construction'] = "Steep slopes detected - recommend terracing or retaining walls"
        
        return recommendations
    
    def _create_rgb_overlay(self, rgb_data: np.ndarray, elevation_zones: np.ndarray, contour_lines: np.ndarray) -> np.ndarray:
        """Create final RGB overlay combining all visual elements"""
        # Start with original RGB
        overlay = rgb_data.copy()
        
        # Blend with elevation zones (30% opacity)
        overlay = cv2.addWeighted(overlay, 0.7, elevation_zones, 0.3, 0)
        
        # Add contour lines
        contour_color = [255, 255, 255]  # White contour lines
        overlay[contour_lines > 0] = contour_color
        
        return overlay
    
    def _apply_calibration(self, depth_data: np.ndarray, rgb_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Apply calibration data to align depth and RGB"""
        # Placeholder for calibration - would use camera calibration matrices
        return depth_data, rgb_data

if __name__ == "__main__":
    # Test the topography renderer
    logging.basicConfig(level=logging.INFO)
    
    # Create test data
    test_depth = np.random.randint(800, 1200, (240, 320)).astype(np.uint16)
    test_rgb = np.random.randint(0, 255, (480, 640, 3)).astype(np.uint8)
    
    renderer = TopographyRenderer()
    topo_data = renderer.render_topography(test_depth, test_rgb)
    
    print("Topography rendering test completed!")
    print(f"AI Metadata: {json.dumps(topo_data.ai_metadata, indent=2)}")

#!/usr/bin/env python3
"""
ToasterOS App Manager - Enhanced Version with Configuration Support
A honeycomb-layout app manager that runs on top of X using SDL2
"""

import sys
import math
import ctypes
import configparser
import os
import sdl2
import sdl2.ext
from typing import List, Tuple


class App:
    """Represents an application in the app manager"""
    
    def __init__(self, name: str, icon_path: str = None, executable: str = None):
        self.name = name
        self.icon_path = icon_path
        self.executable = executable
        self.position = (0, 0)
        self.size = (120, 120)
        self.is_selected = False
        self.texture = None


class HoneycombLayout:
    """Manages honeycomb positioning for apps"""
    
    def __init__(self, center_x: int, center_y: int, hex_size: int = 80):
        self.center_x = center_x
        self.center_y = center_y
        self.hex_size = hex_size
        self.positions = []
        self._generate_positions()
    
    def _generate_positions(self):
        """Generate honeycomb positions starting from center (Apple-style)"""
        # Center position (first app)
        self.positions.append((self.center_x, self.center_y))
        
        # Ring 1: 6 positions around center (starting from top-right, clockwise)
        ring1_distance = self.hex_size * 1.5
        ring1_angles = [math.pi/6, math.pi/2, 5*math.pi/6, 7*math.pi/6, 3*math.pi/2, 11*math.pi/6]
        for angle in ring1_angles:
            x = self.center_x + ring1_distance * math.cos(angle)
            y = self.center_y + ring1_distance * math.sin(angle)
            self.positions.append((int(x), int(y)))
        
        # Ring 2: 12 positions (following Apple's pattern)
        ring2_distance = self.hex_size * 2.6
        ring2_angles = []
        for i in range(12):
            angle = (i * math.pi / 6) + (math.pi / 12)  # Offset for staggered pattern
            ring2_angles.append(angle)
        
        for angle in ring2_angles:
            x = self.center_x + ring2_distance * math.cos(angle)
            y = self.center_y + ring2_distance * math.sin(angle)
            self.positions.append((int(x), int(y)))
        
        # Ring 3: 18 positions
        ring3_distance = self.hex_size * 3.8
        for i in range(18):
            angle = i * math.pi / 9
            x = self.center_x + ring3_distance * math.cos(angle)
            y = self.center_y + ring3_distance * math.sin(angle)
            self.positions.append((int(x), int(y)))
    
    def get_position(self, index: int) -> Tuple[int, int]:
        """Get position for app at given index"""
        if index < len(self.positions):
            return self.positions[index]
        return self.positions[-1]  # Fallback to last position


class AppManager:
    """Main application manager class"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = config_file
        self.config = self._load_config()
        
        # Get configuration values (optimized for touch)
        self.width = self.config.getint('appearance', 'width', fallback=1200)
        self.height = self.config.getint('appearance', 'height', fallback=800)
        hex_size = self.config.getint('appearance', 'hex_size', fallback=100)  # Larger for touch
        
        self.window = None
        self.renderer = None
        self.running = False
        self.apps: List[App] = []
        self.selected_app_index = 0
        self.layout = HoneycombLayout(self.width // 2, self.height // 2, hex_size)
        
        # Touch-specific properties
        self.touch_radius = 70  # Large touch radius for fingers
        self.last_touch_time = 0
        self.touch_hold_duration = 500  # ms for long press
        self.is_touch_held = False
        self.touch_start_pos = None
        self.swipe_threshold = 80  # pixels for swipe detection
        self.zoom_level = 1.0
        self.zoom_center = (self.width // 2, self.height // 2)
        self.touch_feedback_apps = []  # Apps showing touch feedback
        
        # Load colors from config
        self.bg_color = self._parse_color(
            self.config.get('appearance', 'background_color', fallback='20, 25, 40, 255')
        )
        self.app_color = self._parse_color(
            self.config.get('appearance', 'app_color', fallback='60, 70, 90, 255')
        )
        self.selected_color = self._parse_color(
            self.config.get('appearance', 'selected_color', fallback='100, 150, 200, 255')
        )
        self.text_color = self._parse_color(
            self.config.get('appearance', 'text_color', fallback='255, 255, 255, 255')
        )
        self.touch_feedback_color = (255, 255, 255, 100)  # Touch feedback color
        
        self._init_sdl()
        self._load_apps_from_config()
    
    def _load_config(self) -> configparser.ConfigParser:
        """Load configuration from file"""
        config = configparser.ConfigParser()
        
        if os.path.exists(self.config_file):
            config.read(self.config_file)
            print(f"Loaded configuration from {self.config_file}")
        else:
            print(f"Configuration file {self.config_file} not found, using defaults")
            # Create default sections
            config.add_section('apps')
            config.add_section('appearance')
        
        return config
    
    def _parse_color(self, color_str: str) -> Tuple[int, int, int, int]:
        """Parse color string 'R, G, B, A' into tuple"""
        try:
            parts = [int(x.strip()) for x in color_str.split(',')]
            if len(parts) == 4:
                return tuple(parts)
        except ValueError:
            pass
        return (255, 255, 255, 255)  # Default white
    
    def _init_sdl(self):
        """Initialize SDL2"""
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
            raise RuntimeError(f"SDL_Init failed: {sdl2.SDL_GetError()}")
        
        # Create window
        self.window = sdl2.SDL_CreateWindow(
            b"ToasterOS App Manager",
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            self.width,
            self.height,
            sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_RESIZABLE
        )
        
        if not self.window:
            raise RuntimeError(f"SDL_CreateWindow failed: {sdl2.SDL_GetError()}")
        
        # Create renderer
        self.renderer = sdl2.SDL_CreateRenderer(
            self.window, -1,
            sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC
        )
        
        if not self.renderer:
            raise RuntimeError(f"SDL_CreateRenderer failed: {sdl2.SDL_GetError()}")
    
    def _load_apps_from_config(self):
        """Load applications from configuration file"""
        if 'apps' in self.config:
            for name, executable in self.config['apps'].items():
                app = App(name, executable=executable)
                self.register_app(app)
        
        # If no apps in config, register defaults
        if not self.apps:
            self._register_default_apps()
    
    def _register_default_apps(self):
        """Register some default applications"""
        default_apps = [
            App("Terminal", executable="gnome-terminal"),
            App("File Manager", executable="nautilus"),
            App("Web Browser", executable="firefox"),
            App("Text Editor", executable="gedit"),
            App("Calculator", executable="gnome-calculator"),
            App("Settings", executable="gnome-control-center"),
            App("Music Player", executable="rhythmbox"),
        ]
        
        for app in default_apps:
            self.register_app(app)
    
    def register_app(self, app: App):
        """Register a new application"""
        app_index = len(self.apps)
        app.position = self.layout.get_position(app_index)
        self.apps.append(app)
        print(f"Registered app: {app.name} at position {app.position}")
    
    def _draw_hexagon(self, x: int, y: int, size: int, color: Tuple[int, int, int, int], filled: bool = True):
        """Draw a hexagon at given position (Apple-style)"""
        points = []
        for i in range(6):
            angle = i * math.pi / 3 + math.pi / 6  # Rotate 30 degrees for flat-top hexagon
            px = x + size * math.cos(angle)
            py = y + size * math.sin(angle)
            points.extend([int(px), int(py)])
        
        # Set render color
        sdl2.SDL_SetRenderDrawColor(self.renderer, *color)
        
        if filled:
            # Draw filled hexagon using triangular fans
            center_point = (x, y)
            for i in range(6):
                next_i = (i + 1) % 6
                # Draw triangle from center to edge
                self._draw_triangle(
                    center_point,
                    (points[i * 2], points[i * 2 + 1]),
                    (points[next_i * 2], points[next_i * 2 + 1])
                )
        else:
            # Draw hexagon outline
            for i in range(6):
                next_i = (i + 1) % 6
                sdl2.SDL_RenderDrawLine(
                    self.renderer,
                    points[i * 2], points[i * 2 + 1],
                    points[next_i * 2], points[next_i * 2 + 1]
                )
    
    def _draw_triangle(self, p1, p2, p3):
        """Draw a filled triangle using scanline algorithm"""
        # Simple triangle fill - draw lines between edges
        points = [p1, p2, p3]
        points.sort(key=lambda p: p[1])  # Sort by y-coordinate
        
        if points[0][1] == points[2][1]:  # Degenerate triangle
            return
        
        # Draw horizontal lines to fill triangle
        for y in range(int(points[0][1]), int(points[2][1]) + 1):
            x_intersections = []
            
            # Find intersections with triangle edges
            for i in range(3):
                p_start = points[i]
                p_end = points[(i + 1) % 3]
                
                if p_start[1] != p_end[1]:  # Not horizontal line
                    if min(p_start[1], p_end[1]) <= y <= max(p_start[1], p_end[1]):
                        # Calculate x intersection
                        t = (y - p_start[1]) / (p_end[1] - p_start[1])
                        x = p_start[0] + t * (p_end[0] - p_start[0])
                        x_intersections.append(int(x))
            
            # Draw horizontal line between intersections
            if len(x_intersections) >= 2:
                x_intersections.sort()
                sdl2.SDL_RenderDrawLine(
                    self.renderer,
                    x_intersections[0], y,
                    x_intersections[-1], y
                )
    
    def _draw_app(self, app: App, index: int):
        """Draw an application icon (Touch-optimized)"""
        x, y = app.position
        size = int(45 * self.zoom_level)  # Larger base size for touch
        
        # Choose color based on selection and touch feedback
        if index in self.touch_feedback_apps:
            color = (200, 220, 255, 255)  # Light blue for touch feedback
            border_color = (255, 255, 255, 255)  # White border for touch
        elif index == self.selected_app_index:
            color = self.selected_color
            border_color = (255, 255, 255, 255)  # White border for selected
        else:
            color = self.app_color
            border_color = (100, 110, 130, 255)  # Subtle border
        
        # Draw touch area indicator (larger, subtle)
        touch_area_color = (*color[:3], 30)  # Very transparent
        self._draw_hexagon(x, y, int(self.touch_radius * 0.8), touch_area_color, filled=True)
        
        # Draw filled hexagon background
        self._draw_hexagon(x, y, size, color, filled=True)
        
        # Draw hexagon border
        self._draw_hexagon(x, y, size, border_color, filled=False)
        
        # Draw app icon (larger for touch)
        sdl2.SDL_SetRenderDrawColor(self.renderer, *self.text_color)
        
        # Scale icon elements based on zoom
        icon_scale = self.zoom_level
        
        # Draw different symbols based on app type
        app_name_lower = app.name.lower()
        
        if "terminal" in app_name_lower:
            # Draw terminal symbol (rectangle with cursor)
            rect_size = int(25 * icon_scale)
            sdl2.SDL_RenderDrawLine(self.renderer, x - rect_size//2, y - rect_size//2, x + rect_size//2, y - rect_size//2)
            sdl2.SDL_RenderDrawLine(self.renderer, x - rect_size//2, y - rect_size//2, x - rect_size//2, y + rect_size//2)
            sdl2.SDL_RenderDrawLine(self.renderer, x - rect_size//2, y + rect_size//2, x + rect_size//2, y + rect_size//2)
            sdl2.SDL_RenderDrawLine(self.renderer, x + rect_size//2, y - rect_size//2, x + rect_size//2, y + rect_size//2)
            # Cursor
            cursor_size = int(10 * icon_scale)
            sdl2.SDL_RenderDrawLine(self.renderer, x - cursor_size//2, y, x - cursor_size//2, y + cursor_size)
            
        elif "browser" in app_name_lower or "firefox" in app_name_lower:
            # Draw browser symbol (globe)
            globe_radius = int(18 * icon_scale)
            for angle in range(0, 360, 12):
                rad = math.radians(angle)
                px = x + globe_radius * math.cos(rad)
                py = y + globe_radius * math.sin(rad)
                sdl2.SDL_RenderDrawPoint(self.renderer, int(px), int(py))
            # Horizontal and vertical lines
            sdl2.SDL_RenderDrawLine(self.renderer, x - globe_radius, y, x + globe_radius, y)
            sdl2.SDL_RenderDrawLine(self.renderer, x, y - globe_radius, x, y + globe_radius)
            
        elif "file" in app_name_lower or "manager" in app_name_lower:
            # Draw folder symbol
            folder_size = int(20 * icon_scale)
            sdl2.SDL_RenderDrawLine(self.renderer, x - folder_size, y - folder_size//2, x + folder_size, y - folder_size//2)
            sdl2.SDL_RenderDrawLine(self.renderer, x - folder_size, y - folder_size//2, x - folder_size, y + folder_size)
            sdl2.SDL_RenderDrawLine(self.renderer, x - folder_size, y + folder_size, x + folder_size, y + folder_size)
            sdl2.SDL_RenderDrawLine(self.renderer, x + folder_size, y - folder_size//2, x + folder_size, y + folder_size)
            # Folder tab
            tab_size = folder_size // 2
            sdl2.SDL_RenderDrawLine(self.renderer, x - tab_size, y - folder_size//2, x - tab_size, y - folder_size)
            sdl2.SDL_RenderDrawLine(self.renderer, x - tab_size, y - folder_size, x, y - folder_size)
            sdl2.SDL_RenderDrawLine(self.renderer, x, y - folder_size, x, y - folder_size//2)
            
        elif "text" in app_name_lower or "editor" in app_name_lower:
            # Draw text editor symbol (document with lines)
            doc_width, doc_height = int(18 * icon_scale), int(22 * icon_scale)
            sdl2.SDL_RenderDrawLine(self.renderer, x - doc_width, y - doc_height, x + doc_width, y - doc_height)
            sdl2.SDL_RenderDrawLine(self.renderer, x - doc_width, y - doc_height, x - doc_width, y + doc_height)
            sdl2.SDL_RenderDrawLine(self.renderer, x - doc_width, y + doc_height, x + doc_width, y + doc_height)
            sdl2.SDL_RenderDrawLine(self.renderer, x + doc_width, y - doc_height, x + doc_width, y + doc_height)
            # Text lines
            line_spacing = int(6 * icon_scale)
            for i in range(-1, 2):
                sdl2.SDL_RenderDrawLine(self.renderer, x - doc_width + 3, y + i * line_spacing, x + doc_width - 3, y + i * line_spacing)
                
        elif "calculator" in app_name_lower:
            # Draw calculator symbol
            calc_size = int(20 * icon_scale)
            # Calculator body
            sdl2.SDL_RenderDrawLine(self.renderer, x - calc_size, y - calc_size, x + calc_size, y - calc_size)
            sdl2.SDL_RenderDrawLine(self.renderer, x - calc_size, y - calc_size, x - calc_size, y + calc_size)
            sdl2.SDL_RenderDrawLine(self.renderer, x - calc_size, y + calc_size, x + calc_size, y + calc_size)
            sdl2.SDL_RenderDrawLine(self.renderer, x + calc_size, y - calc_size, x + calc_size, y + calc_size)
            # Display
            display_margin = int(2 * icon_scale)
            sdl2.SDL_RenderDrawLine(self.renderer, x - calc_size + display_margin, y - calc_size + display_margin, x + calc_size - display_margin, y - calc_size + display_margin)
            sdl2.SDL_RenderDrawLine(self.renderer, x - calc_size + display_margin, y - calc_size + int(10 * icon_scale), x + calc_size - display_margin, y - calc_size + int(10 * icon_scale))
            # Buttons (simplified)
            button_spacing = int(10 * icon_scale)
            for i in range(3):
                for j in range(3):
                    px = x - button_spacing + i * button_spacing
                    py = y - int(5 * icon_scale) + j * int(8 * icon_scale)
                    sdl2.SDL_RenderDrawPoint(self.renderer, px, py)
                    
        elif "music" in app_name_lower:
            # Draw music note
            stem_length = int(25 * icon_scale)
            note_size = int(8 * icon_scale)
            sdl2.SDL_RenderDrawLine(self.renderer, x + note_size, y - stem_length//2, x + note_size, y + stem_length//2)  # Stem
            # Note head (circle)
            for angle in range(0, 360, 24):
                rad = math.radians(angle)
                px = x + note_size + int(note_size * 0.8 * math.cos(rad))
                py = y + stem_length//2 + int(note_size * 0.6 * math.sin(rad))
                sdl2.SDL_RenderDrawPoint(self.renderer, int(px), int(py))
            # Flag
            flag_size = int(12 * icon_scale)
            sdl2.SDL_RenderDrawLine(self.renderer, x + note_size, y - stem_length//2, x + note_size + flag_size, y - stem_length//2 + flag_size//2)
            sdl2.SDL_RenderDrawLine(self.renderer, x + note_size + flag_size, y - stem_length//2 + flag_size//2, x + note_size, y - stem_length//2 + flag_size)
            
        elif "settings" in app_name_lower:
            # Draw gear symbol
            gear_radius = int(15 * icon_scale)
            for angle in range(0, 360, 24):
                rad = math.radians(angle)
                outer_x = x + gear_radius * math.cos(rad)
                outer_y = y + gear_radius * math.sin(rad)
                inner_x = x + (gear_radius - int(5 * icon_scale)) * math.cos(rad)
                inner_y = y + (gear_radius - int(5 * icon_scale)) * math.sin(rad)
                sdl2.SDL_RenderDrawLine(self.renderer, int(inner_x), int(inner_y), int(outer_x), int(outer_y))
            # Center circle
            center_radius = int(5 * icon_scale)
            for angle in range(0, 360, 15):
                rad = math.radians(angle)
                px = x + center_radius * math.cos(rad)
                py = y + center_radius * math.sin(rad)
                sdl2.SDL_RenderDrawPoint(self.renderer, int(px), int(py))
                
        else:
            # Default app symbol (diamond)
            diamond_size = int(15 * icon_scale)
            sdl2.SDL_RenderDrawLine(self.renderer, x, y - diamond_size, x + diamond_size, y)
            sdl2.SDL_RenderDrawLine(self.renderer, x + diamond_size, y, x, y + diamond_size)
            sdl2.SDL_RenderDrawLine(self.renderer, x, y + diamond_size, x - diamond_size, y)
            sdl2.SDL_RenderDrawLine(self.renderer, x - diamond_size, y, x, y - diamond_size)
    
    def _handle_input(self, event):
        """Handle input events (touch-optimized)"""
        if event.type == sdl2.SDL_QUIT:
            self.running = False
        
        elif event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                self.running = False
            
            elif event.key.keysym.sym == sdl2.SDLK_UP:
                # Apple-style: UP goes left or to center
                self._navigate_apple_up()
            
            elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                # Apple-style: DOWN goes right or to center
                self._navigate_apple_down()
            
            elif event.key.keysym.sym == sdl2.SDLK_LEFT:
                # Navigate counter-clockwise in current ring
                self._navigate_counterclockwise()
            
            elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                # Navigate clockwise in current ring
                self._navigate_clockwise()
            
            elif event.key.keysym.sym == sdl2.SDLK_RETURN or event.key.keysym.sym == sdl2.SDLK_SPACE:
                self._launch_selected_app()
        
        # Touch/Mouse events
        elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
            if event.button.button == sdl2.SDL_BUTTON_LEFT:
                self._handle_touch_start(event.button.x, event.button.y)
        
        elif event.type == sdl2.SDL_MOUSEBUTTONUP:
            if event.button.button == sdl2.SDL_BUTTON_LEFT:
                self._handle_touch_end(event.button.x, event.button.y)
        
        elif event.type == sdl2.SDL_MOUSEMOTION:
            if event.motion.state & sdl2.SDL_BUTTON_LMASK:
                self._handle_touch_move(event.motion.x, event.motion.y)
        
        # Handle finger touch events (SDL 2.0.10+)
        elif event.type == sdl2.SDL_FINGERDOWN:
            # Convert normalized coordinates to screen coordinates
            x = int(event.tfinger.x * self.width)
            y = int(event.tfinger.y * self.height)
            self._handle_touch_start(x, y)
        
        elif event.type == sdl2.SDL_FINGERUP:
            x = int(event.tfinger.x * self.width)
            y = int(event.tfinger.y * self.height)
            self._handle_touch_end(x, y)
        
        elif event.type == sdl2.SDL_FINGERMOTION:
            x = int(event.tfinger.x * self.width)
            y = int(event.tfinger.y * self.height)
            self._handle_touch_move(x, y)
        
        # Pinch-to-zoom (multi-touch)
        elif event.type == sdl2.SDL_MULTIGESTURE:
            if event.mgesture.numFingers == 2:
                # Handle pinch-to-zoom
                self._handle_pinch_zoom(event.mgesture.dDist)
    
    def _get_ring_info(self, index):
        """Get ring number and position within ring for given app index"""
        if index == 0:
            return 0, 0  # Center
        elif index <= 6:
            return 1, index - 1  # Ring 1 (positions 0-5)
        elif index <= 18:
            return 2, index - 7  # Ring 2 (positions 0-11)
        else:
            return 3, index - 19  # Ring 3 (positions 0-17)
    
    def _navigate_apple_up(self):
        """Apple-style UP navigation: go left or to center"""
        current = self.selected_app_index
        ring, pos = self._get_ring_info(current)
        
        if ring == 0:  # At center
            return  # Stay at center
        elif ring == 1:  # Ring 1
            # Move to center
            self.selected_app_index = 0
        elif ring == 2:  # Ring 2
            # Move to left position in Ring 1
            target_pos = (pos + 3) % 6  # Move 3 positions left (opposite side)
            self.selected_app_index = 1 + target_pos
        elif ring == 3:  # Ring 3
            # Move to corresponding position in Ring 2
            target_pos = pos // 2  # Approximate mapping
            if target_pos < 12:
                self.selected_app_index = 7 + target_pos
    
    def _navigate_apple_down(self):
        """Apple-style DOWN navigation: go right or to center"""
        current = self.selected_app_index
        ring, pos = self._get_ring_info(current)
        
        if ring == 0:  # At center
            if len(self.apps) > 1:
                self.selected_app_index = 1  # Go to first app in Ring 1
        elif ring == 1:  # Ring 1
            # Move to right position in Ring 2 if available
            if len(self.apps) > 7:
                target_pos = (pos + 3) % 12  # Move to opposite side
                self.selected_app_index = 7 + target_pos
        elif ring == 2:  # Ring 2
            # Move to corresponding position in Ring 3 if available
            if len(self.apps) > 19:
                target_pos = pos * 2  # Approximate mapping
                if target_pos < 18:
                    self.selected_app_index = 19 + target_pos
    
    def _navigate_clockwise(self):
        """Navigate clockwise within current ring"""
        current = self.selected_app_index
        ring, pos = self._get_ring_info(current)
        
        if ring == 0:  # Center
            return
        elif ring == 1:  # Ring 1 (6 apps)
            next_pos = (pos + 1) % 6
            next_index = 1 + next_pos
            if next_index < len(self.apps):
                self.selected_app_index = next_index
        elif ring == 2:  # Ring 2 (12 apps)
            next_pos = (pos + 1) % 12
            next_index = 7 + next_pos
            if next_index < len(self.apps):
                self.selected_app_index = next_index
        elif ring == 3:  # Ring 3 (18 apps)
            next_pos = (pos + 1) % 18
            next_index = 19 + next_pos
            if next_index < len(self.apps):
                self.selected_app_index = next_index
    
    def _navigate_counterclockwise(self):
        """Navigate counter-clockwise within current ring"""
        current = self.selected_app_index
        ring, pos = self._get_ring_info(current)
        
        if ring == 0:  # Center
            return
        elif ring == 1:  # Ring 1 (6 apps)
            prev_pos = (pos - 1) % 6
            self.selected_app_index = 1 + prev_pos
        elif ring == 2:  # Ring 2 (12 apps)
            prev_pos = (pos - 1) % 12
            prev_index = 7 + prev_pos
            if prev_index >= 7:  # Ensure we don't go below ring start
                self.selected_app_index = prev_index
        elif ring == 3:  # Ring 3 (18 apps)
            prev_pos = (pos - 1) % 18
            prev_index = 19 + prev_pos
            if prev_index >= 19:  # Ensure we don't go below ring start
                self.selected_app_index = prev_index
    
    def _handle_touch_start(self, touch_x: int, touch_y: int):
        """Handle touch/finger down events"""
        import time
        
        self.touch_start_pos = (touch_x, touch_y)
        self.last_touch_time = int(time.time() * 1000)  # Convert to milliseconds
        self.is_touch_held = False
        
        # Check if touch is on an app
        touched_app_index = self._get_app_at_position(touch_x, touch_y)
        if touched_app_index >= 0:
            self.selected_app_index = touched_app_index
            # Add touch feedback
            if touched_app_index not in self.touch_feedback_apps:
                self.touch_feedback_apps.append(touched_app_index)
    
    def _handle_touch_move(self, touch_x: int, touch_y: int):
        """Handle touch/finger move events (for swipe detection)"""
        if self.touch_start_pos is None:
            return
        
        dx = touch_x - self.touch_start_pos[0]
        dy = touch_y - self.touch_start_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        # If moved beyond threshold, it's a swipe
        if distance > self.swipe_threshold:
            self._handle_swipe(dx, dy)
            self.touch_start_pos = None  # Reset to prevent multiple swipes
    
    def _handle_touch_end(self, touch_x: int, touch_y: int):
        """Handle touch/finger up events"""
        import time
        
        current_time = int(time.time() * 1000)
        touch_duration = current_time - self.last_touch_time
        
        # Clear touch feedback
        self.touch_feedback_apps.clear()
        
        if self.touch_start_pos is None:
            return
        
        dx = touch_x - self.touch_start_pos[0]
        dy = touch_y - self.touch_start_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        # If it's a short tap (not a swipe or long press)
        if distance < self.swipe_threshold and touch_duration < self.touch_hold_duration:
            touched_app_index = self._get_app_at_position(touch_x, touch_y)
            if touched_app_index >= 0:
                self.selected_app_index = touched_app_index
                self._launch_selected_app()
        
        # Long press for app info/context menu (future feature)
        elif touch_duration >= self.touch_hold_duration:
            touched_app_index = self._get_app_at_position(touch_x, touch_y)
            if touched_app_index >= 0:
                self._show_app_info(touched_app_index)
        
        self.touch_start_pos = None
    
    def _handle_swipe(self, dx: float, dy: float):
        """Handle swipe gestures"""
        # Determine swipe direction
        if abs(dx) > abs(dy):
            # Horizontal swipe
            if dx > 0:
                # Swipe right - navigate clockwise
                self._navigate_clockwise()
            else:
                # Swipe left - navigate counter-clockwise
                self._navigate_counterclockwise()
        else:
            # Vertical swipe
            if dy > 0:
                # Swipe down - move toward outer rings
                self._navigate_apple_down()
            else:
                # Swipe up - move toward center
                self._navigate_apple_up()
    
    def _handle_pinch_zoom(self, distance_delta: float):
        """Handle pinch-to-zoom gestures"""
        zoom_factor = 1.0 + distance_delta
        new_zoom = self.zoom_level * zoom_factor
        
        # Clamp zoom level
        new_zoom = max(0.5, min(2.0, new_zoom))
        
        if new_zoom != self.zoom_level:
            self.zoom_level = new_zoom
            # Update layout with new zoom
            self._update_layout_for_zoom()
    
    def _get_app_at_position(self, x: int, y: int) -> int:
        """Get app index at given position (with larger touch radius)"""
        for i, app in enumerate(self.apps):
            app_x, app_y = app.position
            distance = math.sqrt((x - app_x) ** 2 + (y - app_y) ** 2)
            
            if distance <= self.touch_radius:
                return i
        return -1
    
    def _show_app_info(self, app_index: int):
        """Show app information on long press (placeholder for future feature)"""
        if 0 <= app_index < len(self.apps):
            app = self.apps[app_index]
            print(f"Long press detected on: {app.name}")
            # Future: Show context menu or app details
    
    def _update_layout_for_zoom(self):
        """Update app positions based on zoom level"""
        center_x, center_y = self.zoom_center
        scaled_hex_size = int(self.layout.hex_size * self.zoom_level)
        
        # Create new layout with scaled size
        new_layout = HoneycombLayout(center_x, center_y, scaled_hex_size)
        
        # Update all app positions
        for i, app in enumerate(self.apps):
            app.position = new_layout.get_position(i)
    
    def _launch_selected_app(self):
        """Launch the currently selected application"""
        if 0 <= self.selected_app_index < len(self.apps):
            app = self.apps[self.selected_app_index]
            print(f"Launching app: {app.name}")
            
            if app.executable:
                import subprocess
                try:
                    # Handle Windows vs Linux executables
                    if os.name == 'nt':  # Windows
                        subprocess.Popen(app.executable, shell=True)
                    else:  # Linux/Unix
                        subprocess.Popen([app.executable])
                    print(f"Successfully launched {app.name}")
                except Exception as e:
                    print(f"Failed to launch {app.name}: {e}")
    
    def _render(self):
        """Render the application manager"""
        # Clear background
        sdl2.SDL_SetRenderDrawColor(self.renderer, *self.bg_color)
        sdl2.SDL_RenderClear(self.renderer)
        
        # Draw all apps
        for i, app in enumerate(self.apps):
            self._draw_app(app, i)
        
        # Draw selection indicator (Apple-style glow)
        if 0 <= self.selected_app_index < len(self.apps):
            selected_app = self.apps[self.selected_app_index]
            x, y = selected_app.position
            
            # Draw multiple concentric selection rings for glow effect
            glow_colors = [
                (255, 255, 100, 150),  # Inner yellow glow
                (255, 255, 150, 100),  # Middle glow
                (255, 255, 200, 50),   # Outer glow
            ]
            
            for i, glow_color in enumerate(glow_colors):
                glow_size = 45 + i * 8
                self._draw_hexagon(x, y, glow_size, glow_color, filled=False)
        
        # Present the frame
        sdl2.SDL_RenderPresent(self.renderer)
    
    def run(self):
        """Main application loop"""
        self.running = True
        event = sdl2.SDL_Event()
        
        print("ToasterOS App Manager started! (Touch-Optimized Apple Honeycomb)")
        print("Touch Controls:")
        print("  TAP: Select and launch app")
        print("  LONG PRESS: Show app info (500ms)")
        print("  SWIPE LEFT/RIGHT: Navigate within ring")
        print("  SWIPE UP: Move toward center")
        print("  SWIPE DOWN: Move toward outer rings")
        print("  PINCH: Zoom in/out (two fingers)")
        print("Keyboard Controls:")
        print("  UP/DOWN: Apple-style navigation")
        print("  LEFT/RIGHT: Navigate within ring")
        print("  Enter/Space: Launch app")
        print("  Escape: Quit")
        print(f"Loaded {len(self.apps)} applications in touch-optimized honeycomb layout")
        print(f"Touch radius: {self.touch_radius}px, Zoom level: {self.zoom_level:.1f}x")
        
        while self.running:
            # Handle events
            while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
                self._handle_input(event)
            
            # Render
            self._render()
            
            # Small delay to prevent high CPU usage
            sdl2.SDL_Delay(16)  # ~60 FPS
    
    def cleanup(self):
        """Clean up SDL resources"""
        if self.renderer:
            sdl2.SDL_DestroyRenderer(self.renderer)
        if self.window:
            sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()


def main():
    """Main entry point"""
    app_manager = None
    
    try:
        app_manager = AppManager()
        app_manager.run()
    
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    finally:
        if app_manager:
            app_manager.cleanup()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

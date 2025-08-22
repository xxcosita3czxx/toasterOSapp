import sdl2
import sdl2.ext

class AppMenu:
    def __init__(self, window, renderer):
        self.window = window
        self.renderer = renderer
        self.is_open = False
        self.apps = [
            {"name": "Calculator", "icon": "[CALC]"},
            {"name": "Settings", "icon": "[SET]"},
            {"name": "File Manager", "icon": "[FILE]"},
            {"name": "Web Browser", "icon": "[WEB]"},
            {"name": "Music Player", "icon": "[MUSIC]"},
            {"name": "Games", "icon": "[GAME]"},
            {"name": "Camera", "icon": "[CAM]"},
            {"name": "Notes", "icon": "[NOTE]"}
        ]
        
    def toggle(self):
        """Toggle the app menu open/closed"""
        self.is_open = not self.is_open
        print(f"App menu {'opened' if self.is_open else 'closed'}")
        
    def draw(self):
        """Draw the app menu overlay graphically"""
        if not self.is_open:
            return
            
        window_width, window_height = self.window.size
        
        # Draw semi-transparent background overlay
        overlay_color = sdl2.ext.Color(0, 0, 0, 180)  # Semi-transparent black
        self.renderer.clear(overlay_color)
        
        # Calculate menu dimensions
        menu_width = min(400, window_width - 40)
        menu_height = min(500, window_height - 40)
        menu_x = (window_width - menu_width) // 2
        menu_y = (window_height - menu_height) // 2
        
        # Draw menu background
        menu_rect = sdl2.SDL_Rect(menu_x, menu_y, menu_width, menu_height)
        menu_color = sdl2.ext.Color(40, 40, 40, 255)  # Dark gray
        self.renderer.fill(menu_rect, menu_color)
        
        # Draw menu border
        border_color = sdl2.ext.Color(100, 100, 100, 255)  # Light gray border
        self.renderer.draw_rect(menu_rect, border_color)
        
        # Draw app grid
        apps_per_row = 2
        app_width = (menu_width - 60) // apps_per_row
        app_height = 80
        start_x = menu_x + 20
        start_y = menu_y + 60
        
        for i, app in enumerate(self.apps):
            row = i // apps_per_row
            col = i % apps_per_row
            
            app_x = start_x + col * (app_width + 20)
            app_y = start_y + row * (app_height + 10)
            
            # Draw app background
            app_rect = sdl2.SDL_Rect(app_x, app_y, app_width, app_height)
            app_bg_color = sdl2.ext.Color(60, 60, 60, 255)  # Slightly lighter gray
            self.renderer.fill(app_rect, app_bg_color)
            
            # Draw app border (highlight if selected)
            app_border_color = sdl2.ext.Color(120, 120, 120, 255)
            self.renderer.draw_rect(app_rect, app_border_color)
            
            # For now, we'll use simple rectangles as app icons
            # In the future, you can load actual icon images
            icon_size = 32
            icon_x = app_x + (app_width - icon_size) // 2
            icon_y = app_y + 10
            icon_rect = sdl2.SDL_Rect(icon_x, icon_y, icon_size, icon_size)
            
            # Different colors for different app types
            icon_colors = [
                sdl2.ext.Color(255, 100, 100, 255),  # Calculator - Red
                sdl2.ext.Color(100, 255, 100, 255),  # Settings - Green
                sdl2.ext.Color(100, 100, 255, 255),  # File Manager - Blue
                sdl2.ext.Color(255, 255, 100, 255),  # Web Browser - Yellow
                sdl2.ext.Color(255, 100, 255, 255),  # Music Player - Magenta
                sdl2.ext.Color(100, 255, 255, 255),  # Games - Cyan
                sdl2.ext.Color(255, 150, 100, 255),  # Camera - Orange
                sdl2.ext.Color(200, 200, 200, 255),  # Notes - Gray
            ]
            
            icon_color = icon_colors[i % len(icon_colors)]
            self.renderer.fill(icon_rect, icon_color)
        
        # Present the rendered frame
        self.renderer.present()
        
    def handle_click(self, x, y):
        """Handle clicks on the app menu"""
        if not self.is_open:
            return False
            
        window_width, window_height = self.window.size
        
        # Calculate menu dimensions (same as in draw method)
        menu_width = min(400, window_width - 40)
        menu_height = min(500, window_height - 40)
        menu_x = (window_width - menu_width) // 2
        menu_y = (window_height - menu_height) // 2
        
        # Check if click is within menu bounds
        if not (menu_x <= x <= menu_x + menu_width and menu_y <= y <= menu_y + menu_height):
            # Click outside menu - close it
            self.toggle()
            return True
            
        # Calculate app grid positions (same as in draw method)
        apps_per_row = 2
        app_width = (menu_width - 60) // apps_per_row
        app_height = 80
        start_x = menu_x + 20
        start_y = menu_y + 60
        
        # Check which app was clicked
        for i, app in enumerate(self.apps):
            row = i // apps_per_row
            col = i % apps_per_row
            
            app_x = start_x + col * (app_width + 20)
            app_y = start_y + row * (app_height + 10)
            
            # Check if click is within this app's bounds
            if (app_x <= x <= app_x + app_width and app_y <= y <= app_y + app_height):
                print(f"Clicked on {app['name']} at ({x}, {y})")
                self.launch_app(i)
                return True
        
        return True  # Click was within menu bounds but not on an app
        
    def launch_app(self, app_index):
        """Launch an app (placeholder functionality)"""
        if 0 <= app_index < len(self.apps):
            app = self.apps[app_index]
            print(f">> Launching {app['name']} {app['icon']}")
            # Add actual app launching logic here later
            self.is_open = False  # Close menu after launching

import os
import sdl2
import sdl2.ext
import json

class AnimationManager:
    def __init__(self, renderer, image_folder, window, interval=2):
        """Initialize the animation manager with a shared window.

        Args:
            image_folder (str): Path to the folder containing images.
            window (sdl2.ext.Window): Pre-created SDL2 window object to use.
            interval (float): Time interval (in seconds) between image transitions.
        """
        self.image_folder = image_folder
        self.window = window
        self.interval = interval
        self.animations = {}
        self.running = True
        self.renderer = renderer

    def get_image_rect(self, sprite, fill_mode):
        """Calculate the destination rectangle for an image based on the fill mode.
        
        Args:
            sprite: The sprite object containing the image
            fill_mode (str): Fill mode - "full", "horizontal", "vertical", or "fit"
            
        Returns:
            sdl2.SDL_Rect: The destination rectangle for rendering
        """
        window_width, window_height = self.window.size
        sprite_width, sprite_height = sprite.size
        
        if fill_mode == "full":
            # Stretch to fill entire window (may distort aspect ratio)
            return sdl2.SDL_Rect(0, 0, window_width, window_height)
        
        elif fill_mode == "horizontal":
            # Fill horizontally, maintain aspect ratio, center vertically
            scale = window_width / sprite_width
            new_width = window_width
            new_height = int(sprite_height * scale)
            y_offset = max(0, (window_height - new_height) // 2)
            return sdl2.SDL_Rect(0, y_offset, new_width, min(new_height, window_height))
        
        elif fill_mode == "vertical":
            # Fill vertically, maintain aspect ratio, center horizontally
            scale = window_height / sprite_height
            new_height = window_height
            new_width = int(sprite_width * scale)
            x_offset = max(0, (window_width - new_width) // 2)
            return sdl2.SDL_Rect(x_offset, 0, min(new_width, window_width), new_height)
        
        elif fill_mode == "fit":
            # Fit entire image in window, maintain aspect ratio, letterbox if needed
            scale_x = window_width / sprite_width
            scale_y = window_height / sprite_height
            scale = min(scale_x, scale_y)
            
            new_width = int(sprite_width * scale)
            new_height = int(sprite_height * scale)
            x_offset = (window_width - new_width) // 2
            y_offset = (window_height - new_height) // 2
            
            return sdl2.SDL_Rect(x_offset, y_offset, new_width, new_height)
        
        else:
            # Default to full if unknown mode
            return sdl2.SDL_Rect(0, 0, window_width, window_height)

    def load_animations(self):
        """Load animations from folders containing images and a JSON configuration file."""
        if not os.path.exists(self.image_folder):
            print(f"Image folder '{self.image_folder}' does not exist.")
            return

        self.animations = {}
        for animation_folder in os.listdir(self.image_folder):
            folder_path = os.path.join(self.image_folder, animation_folder)
            if not os.path.isdir(folder_path):
                continue

            config_path = os.path.join(folder_path, "anim.json")
            if not os.path.exists(config_path):
                print(f"Animation configuration '{config_path}' does not exist in '{folder_path}'. Skipping.")
                continue

            with open(config_path, "r") as config_file:
                animation_data = json.load(config_file)

            sequence = []
            for item in animation_data.get("anim", []):
                if isinstance(item, dict) and "sleep" in item:
                    sequence.append(item)
                elif isinstance(item, str):
                    frame_path = os.path.join(folder_path, item)
                    if not os.path.splitext(frame_path)[1]:  # If no extension, assume .png
                        frame_path += ".png"
                    if os.path.exists(frame_path):
                        sequence.append(frame_path)
                    else:
                        print(f"Frame '{item}' not found in '{folder_path}'. Skipping frame.")

            if not sequence:
                print(f"Animation '{animation_folder}' has an empty sequence. Skipping.")
                continue

            self.animations[animation_folder] = {
                "sequence": sequence,
                "interval": animation_data.get("interval", 0.1),
                "loop": animation_data.get("loop", True),
                "fill": animation_data.get("fill", "full")
            }

    def run(self, selected_animations=None):
        """Run the animation loop application infinitely, cycling through selected animations."""
        if not self.animations:
            print("No animations to display. Exiting.")
            return

        if selected_animations is None:
            selected_animations = list(self.animations.keys())
        else:
            selected_animations = [anim for anim in selected_animations if anim in self.animations]

        if not selected_animations:
            print("No valid animations selected. Exiting.")
            return

        current_animation_index = 0
        while self.running:
            current_animation_name = selected_animations[current_animation_index]
            self.run_animation(current_animation_name, loop=False)
            current_animation_index = (current_animation_index + 1) % len(selected_animations)

    def run_animation(self, animation_name, loop=False):
        """Run a specific animation by name, optionally looping infinitely."""
        if animation_name not in self.animations:
            print(f"Animation '{animation_name}' not found.")
            return

        factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=self.renderer)
        animation_data = self.animations[animation_name]
        sprite_cache = {}
        
        # Pre-load all image sprites
        for item in animation_data["sequence"]:
            if isinstance(item, str) and item.endswith((".png", ".jpg", ".jpeg")):
                if item not in sprite_cache:
                    sprite_cache[item] = factory.from_image(item)

        # Run the animation sequence
        while True:
            for current_item in animation_data["sequence"]:
                if not self.running:  # Only check for global stop
                    return
                
                if isinstance(current_item, str) and current_item.endswith((".png", ".jpg", ".jpeg")):
                    self.renderer.clear(sdl2.ext.Color(0, 0, 0))
                    sprite = sprite_cache[current_item]
                    fill_mode = animation_data.get("fill", "full")
                    dstrect = self.get_image_rect(sprite, fill_mode)
                    self.renderer.copy(sprite, dstrect=dstrect)
                    self.renderer.present()
                    sdl2.SDL_Delay(int(animation_data["interval"] * 1000))
                elif isinstance(current_item, dict) and "sleep" in current_item:
                    # Keep last frame visible during sleep
                    sdl2.SDL_Delay(int(current_item["sleep"] * 1000))

            # If not looping, break after one complete sequence
            if not loop:
                break

    def play_video(self, video_path):
        """Legacy video playback function - no longer used."""
        print(f"Video playback no longer supported: {video_path}")
        print("Videos have been converted to frame sequences.")

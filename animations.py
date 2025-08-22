import os
import sdl2
import sdl2.ext
import time
import json
from PIL import Image

class AnimationManager:
    def __init__(self, image_folder, window, interval=2):
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
        self.renderer = sdl2.ext.Renderer(self.window)

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
                elif isinstance(item, dict) and "video" in item:
                    video_path = os.path.join(folder_path, item["video"])
                    if os.path.exists(video_path):
                        sequence.append({"video": video_path})
                    else:
                        print(f"Video file '{item['video']}' not found in '{folder_path}'. Skipping frame.")
                elif isinstance(item, str):
                    frame_path = os.path.join(folder_path, item)
                    if not os.path.splitext(frame_path)[1]:  # If no extension, assume .png
                        frame_path += ".png"
                    if os.path.exists(frame_path):
                        sequence.append(frame_path)
                    elif frame_path.endswith(".mp4") and os.path.exists(frame_path):
                        sequence.append(frame_path)  # Add MP4 files directly as strings
                    else:
                        print(f"Frame '{item}' not found in '{folder_path}'. Skipping frame.")

            if not sequence:
                print(f"Animation '{animation_folder}' has an empty sequence. Skipping.")
                continue

            self.animations[animation_folder] = {
                "sequence": sequence,
                "interval": animation_data.get("interval", 0.1),
                "loop": animation_data.get("loop", True),
                "fill": animation_data.get("fill", "full")  # Default to "full" for backward compatibility
            }

    def run(self, selected_animations=None):
        """Run the animation loop application infinitely, cycling through selected animations.

        Args:
            selected_animations (list, optional): List of animation names to cycle through. Defaults to all animations.
        """
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

        # Prepare animations
        animation_sprites = {}
        for animation_name in selected_animations:
            animation_data = self.animations[animation_name]
            animation_sprites[animation_name] = [
                sprite
                for frame in animation_data["sequence"]
                for sprite in [self.renderer.factory.from_image(frame)] if isinstance(frame, str) and (frame.endswith(".png") or frame.endswith(".jpg") or frame.endswith(".jpeg"))
            ]

        current_animation_index = 0
        target_frame_duration = 1 / 60  # Target duration for 60 FPS

        while self.running:
            frame_start_time = time.time()
            self.renderer.clear(sdl2.ext.Color(30, 30, 30))

            # Get current animation data
            current_animation_name = selected_animations[current_animation_index]
            animation_data = self.animations[current_animation_name]
            sequence = animation_data["sequence"]
            sprites = animation_sprites[current_animation_name]

            # Handle the current sequence item
            for current_sequence_index, current_item in enumerate(sequence):
                if isinstance(current_item, dict) and "video" in current_item:
                    # Handle video items
                    video_path = os.path.join(animation_data.get("base_path", ""), current_item["video"])
                    if video_path.endswith(".mp4") and os.path.exists(video_path):
                        self.play_video(video_path)
                    else:
                        print(f"Invalid or missing video file '{video_path}'. Skipping.")
                elif isinstance(current_item, dict) and "sleep" in current_item:
                    # Handle sleep items
                    time.sleep(current_item["sleep"])
                elif isinstance(current_item, str):
                    # Handle frame items
                    if current_item.endswith((".png", ".jpg", ".jpeg")):
                        sprite = sprites[current_sequence_index]
                        fill_mode = animation_data.get("fill", "full")
                        dstrect = self.get_image_rect(sprite, fill_mode)
                        self.renderer.copy(sprite, dstrect=dstrect)
                        self.renderer.present()
                    else:
                        print(f"Invalid or unsupported frame file '{current_item}'. Skipping.")
                else:
                    print(f"Unsupported sequence item: {current_item}. Skipping.")

                # Handle events
                events = sdl2.ext.get_events()
                for event in events:
                    if event.type == sdl2.SDL_QUIT:
                        self.running = False

                # Enforce 60 FPS
                frame_end_time = time.time()
                frame_duration = frame_end_time - frame_start_time
                if frame_duration < target_frame_duration:
                    time.sleep(target_frame_duration - frame_duration)

            # Move to the next animation
            current_animation_index = (current_animation_index + 1) % len(selected_animations)

    def run_animation(self, animation_name, loop=False):
        """Run a specific animation by name, optionally looping infinitely.

        Args:
            animation_name (str): The name of the animation to run.
            loop (bool): Whether to loop the animation infinitely. Defaults to False.
        """
        if animation_name not in self.animations:
            print(f"Animation '{animation_name}' not found.")
            return

        self.running = True  # Ensure the animation loop starts running

        factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=self.renderer)  # Ensure factory is used correctly

        # Prepare the animation - create a mapping of frame paths to sprites
        animation_data = self.animations[animation_name]
        sprite_cache = {}
        
        # Pre-load all image sprites
        for item in animation_data["sequence"]:
            if isinstance(item, str) and item.endswith((".png", ".jpg", ".jpeg")):
                if item not in sprite_cache:
                    sprite_cache[item] = factory.from_image(item)

        current_sequence_index = 0
        last_update_time = time.time()
        target_frame_duration = 1 / 60  # Target duration for 60 FPS

        while self.running:
            frame_start_time = time.time()
            self.renderer.clear(sdl2.ext.Color(0, 0, 0))

            # Handle the current sequence item
            current_item = animation_data["sequence"][current_sequence_index]
            if isinstance(current_item, str) and current_item.endswith((".png", ".jpg", ".jpeg")):
                # Display the current frame using the sprite cache
                sprite = sprite_cache[current_item]
                fill_mode = animation_data.get("fill", "full")
                dstrect = self.get_image_rect(sprite, fill_mode)
                self.renderer.copy(sprite, dstrect=dstrect)
                self.renderer.present()
            elif isinstance(current_item, str) and current_item.endswith(".mp4"):
                # Handle MP4 files stored as strings (legacy - should not happen with new frame system)
                print(f"Warning: MP4 file found in sequence: {current_item}")
                print("This should have been converted to frames. Skipping.")
                # Move to next sequence item
                current_sequence_index += 1
                if current_sequence_index >= len(animation_data["sequence"]):
                    if loop:
                        current_sequence_index = 0
                    else:
                        self.running = False
                continue
            elif isinstance(current_item, dict) and "sleep" in current_item:
                # Handle sleep items
                time.sleep(current_item["sleep"])
            else:
                print(f"Unsupported sequence item: {current_item}. Skipping.")

            # Handle events
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    self.running = False

            # Update the current sequence index based on the interval
            now = time.time()
            if isinstance(current_item, str) and now - last_update_time >= animation_data["interval"]:
                current_sequence_index += 1
                if current_sequence_index >= len(animation_data["sequence"]):
                    if loop:
                        current_sequence_index = 0  # Restart the animation if looping
                    else:
                        self.running = False  # Stop after completing the animation
                last_update_time = now
            elif isinstance(current_item, dict) and "sleep" in current_item:
                current_sequence_index += 1
                if current_sequence_index >= len(animation_data["sequence"]):
                    if loop:
                        current_sequence_index = 0  # Restart the animation if looping
                    else:
                        self.running = False  # Stop after completing the animation
                last_update_time = now

            # Enforce 60 FPS
            frame_end_time = time.time()
            frame_duration = frame_end_time - frame_start_time
            if frame_duration < target_frame_duration:
                time.sleep(target_frame_duration - frame_duration)

    def play_video(self, video_path):
        """Legacy video playback function - no longer used.
        Videos have been converted to frame sequences.

        Args:
            video_path (str): Path to the MP4 video file (ignored).
        """
        print(f"Video playback requested for: {video_path}")
        print("Videos have been converted to frame sequences - this function is no longer used.")
        print("Update your animation configuration to use frame sequences instead.")

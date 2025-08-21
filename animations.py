import os
import sdl2
import sdl2.ext
import time
import json
import cv2  # Add OpenCV for video handling

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
                        sequence.append({"video": frame_path})
                    else:
                        print(f"Frame '{item}' not found in '{folder_path}'. Skipping frame.")

            if not sequence:
                print(f"Animation '{animation_folder}' has an empty sequence. Skipping.")
                continue

            self.animations[animation_folder] = {
                "sequence": sequence,
                "interval": animation_data.get("interval", 0.1),
                "loop": animation_data.get("loop", True)
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
                for sprite in [self.renderer.factory.from_image(frame)] if isinstance(frame, str)
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
                    if current_item.endswith(".png"):
                        sprite = sprites[current_sequence_index]
                        window_size = self.window.size
                        dstrect = sdl2.SDL_Rect(0, 0, window_size[0], window_size[1])
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

        # Prepare the animation
        animation_data = self.animations[animation_name]
        sprites = [
            factory.from_image(frame) if isinstance(frame, str) and frame.endswith(".png") else None
            for frame in animation_data["sequence"]
            if isinstance(frame, str) and frame.endswith(".png")
        ]

        current_sequence_index = 0
        last_update_time = time.time()
        target_frame_duration = 1 / 60  # Target duration for 60 FPS

        while self.running:
            frame_start_time = time.time()
            self.renderer.clear(sdl2.ext.Color(30, 30, 30))

            # Handle the current sequence item
            current_item = animation_data["sequence"][current_sequence_index]
            if isinstance(current_item, str) and current_item.endswith(".png"):
                # Display the current frame
                sprite = sprites[current_sequence_index]
                window_size = self.window.size
                dstrect = sdl2.SDL_Rect(0, 0, window_size[0], window_size[1])
                self.renderer.copy(sprite, dstrect=dstrect)
                self.renderer.present()
            elif isinstance(current_item, str) and current_item.endswith(".mp4"):
                # Handle MP4 files stored as strings
                if os.path.exists(current_item):
                    self.play_video(current_item)
                else:
                    print(f"Video file '{current_item}' not found. Skipping.")
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
        """Play an MP4 video in the SDL2 window.

        Args:
            video_path (str): Path to the MP4 video file.
        """
        if not os.path.exists(video_path):
            print(f"Video file '{video_path}' does not exist.")
            return

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Failed to open video file '{video_path}'.")
            return

        # Get video properties for proper frame rate
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_delay = 1.0 / fps if fps > 0 else 1.0 / 30  # Default to 30 FPS if unable to get FPS

        while cap.isOpened() and self.running:
            frame_start_time = time.time()
            
            ret, frame = cap.read()
            if not ret:
                break

            # Convert the frame to SDL2-compatible format
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Calculate aspect ratio preserving resize (fit to window, not crop)
            frame_height, frame_width = frame.shape[:2]
            window_width, window_height = self.window.size
            
            # Calculate scaling factors
            scale_x = window_width / frame_width
            scale_y = window_height / frame_height
            scale = min(scale_x, scale_y)  # Use min to fit the entire video
            
            # Calculate new dimensions
            new_width = int(frame_width * scale)
            new_height = int(frame_height * scale)
            
            # Resize frame
            frame = cv2.resize(frame, (new_width, new_height))
            
            # Add padding to center the video if needed
            if new_width != window_width or new_height != window_height:
                top = (window_height - new_height) // 2
                bottom = window_height - new_height - top
                left = (window_width - new_width) // 2
                right = window_width - new_width - left
                frame = cv2.copyMakeBorder(frame, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0])

            # Create a surface from the frame data
            frame_surface = sdl2.SDL_CreateRGBSurfaceFrom(
                frame.ctypes.data,
                self.window.size[0], self.window.size[1], 24,
                self.window.size[0] * 3,
                0x000000FF, 0x0000FF00, 0x00FF0000, 0
            )
            
            # Create texture from surface using the renderer's factory
            factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=self.renderer)
            texture = factory.from_surface(frame_surface)

            # Render the frame
            self.renderer.clear()
            self.renderer.copy(texture)
            self.renderer.present()
            
            # Clean up the surface
            sdl2.SDL_FreeSurface(frame_surface)

            # Handle events
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    self.running = False

            # Maintain proper video frame rate
            frame_end_time = time.time()
            elapsed_time = frame_end_time - frame_start_time
            if elapsed_time < frame_delay:
                time.sleep(frame_delay - elapsed_time)

        cap.release()

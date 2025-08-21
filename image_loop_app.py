import os
import sdl2
import sdl2.ext
import time
import json

class ImageLoopApp:
    def __init__(self, image_folder, interval=2):
        """Initialize the image loop app.

        Args:
            image_folder (str): Path to the folder containing images.
            interval (float): Time interval (in seconds) between image transitions.
        """
        self.image_folder = image_folder
        self.interval = interval
        self.images = []
        self.current_image_index = 0
        self.last_update_time = time.time()
        self.running = True
        self.window = None
        self.renderer = None
        self.animations = {}

    def load_images(self):
        """Load all images from the specified folder."""
        if not os.path.exists(self.image_folder):
            print(f"Image folder '{self.image_folder}' does not exist.")
            return

        for file_name in os.listdir(self.image_folder):
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                self.images.append(os.path.join(self.image_folder, file_name))

        if not self.images:
            print("No images found in the folder.")

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
                else:
                    frame_path = os.path.join(folder_path, f"{item}.png")
                    if os.path.exists(frame_path):
                        sequence.append(frame_path)
                    else:
                        print(f"Frame '{item}.png' not found in '{folder_path}'. Skipping frame.")

            if not sequence:
                print(f"Animation '{animation_folder}' has an empty sequence. Skipping.")
                continue

            self.animations[animation_folder] = {
                "sequence": sequence,
                "interval": animation_data.get("interval", 0.1),
                "loop": animation_data.get("loop", True)
            }

    def run(self):
        """Run the animation loop application."""
        if not self.animations:
            print("No animations to display. Exiting.")
            return

        sdl2.ext.init()
        display_mode = sdl2.SDL_DisplayMode()
        sdl2.SDL_GetCurrentDisplayMode(0, display_mode)
        self.window = sdl2.ext.Window("Animation Loop App", size=(display_mode.w, display_mode.h), flags=sdl2.SDL_WINDOW_FULLSCREEN)
        self.window.show()

        self.renderer = sdl2.ext.Renderer(self.window)
        factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=self.renderer)

        # Prepare animations
        animation_sprites = {}
        for animation_name, animation_data in self.animations.items():
            animation_sprites[animation_name] = [
                factory.from_image(frame) if isinstance(frame, str) else None
                for frame in animation_data["sequence"] if isinstance(frame, str)
            ]

        current_animation = list(self.animations.keys())[0]  # Start with the first animation
        current_sequence_index = 0
        last_update_time = time.time()
        target_frame_duration = 1 / 60  # Target duration for 60 FPS

        while self.running:
            frame_start_time = time.time()
            self.renderer.clear(sdl2.ext.Color(30, 30, 30))

            # Get current animation data
            animation_data = self.animations[current_animation]
            sequence = animation_data["sequence"]

            # Handle the current sequence item
            current_item = sequence[current_sequence_index]
            if isinstance(current_item, str):
                # Display the current frame
                sprite_index = [i for i, item in enumerate(sequence) if isinstance(item, str)].index(current_sequence_index)
                sprite = animation_sprites[current_animation][sprite_index]
                window_size = self.window.size
                dstrect = sdl2.SDL_Rect(0, 0, window_size[0], window_size[1])
                self.renderer.copy(sprite, dstrect=dstrect)
                self.renderer.present()
            elif isinstance(current_item, dict) and "sleep" in current_item:
                time.sleep(current_item["sleep"])

            # Handle events
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    self.running = False

            # Update the current sequence index based on the interval
            now = time.time()
            if isinstance(current_item, str) and now - last_update_time >= animation_data["interval"]:
                current_sequence_index += 1
                if current_sequence_index >= len(sequence):
                    if animation_data["loop"]:
                        current_sequence_index = 0
                    else:
                        self.running = False  # Stop if the animation does not loop
                last_update_time = now
            elif isinstance(current_item, dict) and "sleep" in current_item:
                current_sequence_index += 1
                if current_sequence_index >= len(sequence):
                    if animation_data["loop"]:
                        current_sequence_index = 0
                    else:
                        self.running = False  # Stop if the animation does not loop
                last_update_time = now

            # Enforce 60 FPS
            frame_end_time = time.time()
            frame_duration = frame_end_time - frame_start_time
            if frame_duration < target_frame_duration:
                time.sleep(target_frame_duration - frame_duration)

if __name__ == "__main__":
    app = ImageLoopApp("Images", interval=0.1)  # Replace "Images" with your folder containing images
    app.load_images()
    app.load_animations()
    app.run()

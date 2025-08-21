import os
import sdl2
import sdl2.ext
import time

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

    def run(self):
        """Run the image loop application."""
        if not self.images:
            print("No images to display. Exiting.")
            return

        sdl2.ext.init()
        display_mode = sdl2.SDL_DisplayMode()
        sdl2.SDL_GetCurrentDisplayMode(0, display_mode)
        self.window = sdl2.ext.Window("Image Loop App", size=(display_mode.w, display_mode.h), flags=sdl2.SDL_WINDOW_FULLSCREEN)
        self.window.show()

        self.renderer = sdl2.ext.Renderer(self.window)
        factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=self.renderer)

        sprites = [factory.from_image(image_path) for image_path in self.images]

        direction = 1  # 1 for forward, -1 for backward
        blink = False  # Blinking state
        while self.running:
            self.renderer.clear(sdl2.ext.Color(30, 30, 30))

            # Display the current image scaled to fullscreen
            if not blink:  # Skip rendering during blink
                sprite = sprites[self.current_image_index]
                window_size = self.window.size
                dstrect = sdl2.SDL_Rect(0, 0, window_size[0], window_size[1])
                self.renderer.copy(sprite, dstrect=dstrect)

            self.renderer.present()

            # Handle events
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    self.running = False

            # Update the current image based on the interval
            now = time.time()
            if now - self.last_update_time >= self.interval:
                if blink:
                    blink = False  # End blinking
                else:
                    self.current_image_index += direction

                    # Reverse direction at the ends and start blinking
                    if self.current_image_index == len(sprites) - 1 or self.current_image_index == 0:
                        direction *= -1
                        blink = True  # Start blinking
                        time.sleep(0.5)  # Short blink delay

                self.last_update_time = now

        sdl2.ext.quit()

if __name__ == "__main__":
    app = ImageLoopApp("Images", interval=1)  # Replace "Images" with your folder containing images
    app.load_images()
    app.run()

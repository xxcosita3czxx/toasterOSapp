import sdl2.ext
from animations import AnimationManager

if __name__ == "__main__":
    print("Starting simple ToasterOS...")    
    # Initialize SDL2
    sdl2.ext.init()
    print("SDL2 initialized")
    
    # Create fullscreen window
    window = sdl2.ext.Window("ToasterOS", size=(800, 600), flags=sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP)
    window.show()
    print("Windowed fullscreen created and shown")
    
    # Create animation manager
    animation_manager = AnimationManager("Anims", window)
    animation_manager.load_animations()
    print("Animations loaded")
    
    # Run animations
    print("Starting animations...")
    animation_manager.run_animation("load")
    animation_manager.run_animation("bootUp")
    while True:
        animation_manager.run_animation("blink")
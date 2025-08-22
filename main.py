import sdl2.ext
from animations import AnimationManager

if __name__ == "__main__":
    print("Starting simple ToasterOS...")    
    # Initialize SDL2
    sdl2.ext.init()
    print("SDL2 initialized")
    
    # Get display dimensions for fullscreen borderless
    display_mode = sdl2.SDL_DisplayMode()
    result = sdl2.SDL_GetCurrentDisplayMode(0, display_mode)
    
    if result == 0:
        screen_width, screen_height = display_mode.w, display_mode.h
    else:
        screen_width, screen_height = 1920, 1080  # fallback
    
    # Create borderless window at full screen size
    window = sdl2.ext.Window(
        "ToasterOS", 
        size=(screen_width, screen_height),
        flags=sdl2.SDL_WINDOW_BORDERLESS | sdl2.SDL_WINDOW_SHOWN
    )
    sdl2.SDL_SetWindowPosition(window.window, 0, 0)
    window.show()
    print(f"Borderless fullscreen window created: {screen_width}x{screen_height}")
    
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
import sdl2.ext
import sdl2
import time
from Libs.animations import AnimationManager
from Libs.menu import draw_menu

MENU_TIMEOUT = 30  # seconds

menu_open = False
last_touch_time = time.time()
running = True


if __name__ == "__main__":        
    # Initialize SDL2
    sdl2.ext.init()
    print("SDL2 initialized")
    
    # Get display dimensions for fullscreen borderless
    display_mode = sdl2.SDL_DisplayMode()
    result = sdl2.SDL_GetCurrentDisplayMode(0, display_mode)
    
    if result == 0:
        screen_width, screen_height = display_mode.w, display_mode.h
    else:
        screen_width, screen_height = 720, 480  # fallback
        print("Failed to get display mode, using fallback 720x480")
    print(f"Display mode: {screen_width}x{screen_height}")
    # Create borderless window at full screen size
    window = sdl2.ext.Window(
        "ToasterOS", 
        size=(screen_width, screen_height),
        flags=sdl2.SDL_WINDOW_BORDERLESS | sdl2.SDL_WINDOW_SHOWN
    )
    sdl2.SDL_SetWindowPosition(window.window, 0, 0)
    window.show()
    print(f"Borderless fullscreen window created: {screen_width}x{screen_height}")
    
    # Create renderer for the display window
    renderer = sdl2.ext.Renderer(window)
    # Create animation manager
    animation_manager = AnimationManager(renderer, "Anims", window)
    animation_manager.load_animations()
    print("Animations loaded")

    # Run animations
    print("Starting animations...")
    animation_manager.run_animation("load")
    animation_manager.run_animation("bootUp")

    while running:
        events = sdl2.ext.get_events()
        touched = False
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
            elif event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                    running = False
            animation_manager.run_animation("blink")
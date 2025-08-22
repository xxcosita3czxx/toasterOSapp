import sdl2.ext
import threading
import time
from animations import AnimationManager
from app_menu import AppMenu

if __name__ == "__main__":
    print("Starting ToasterOS...")
    print("Initializing SDL2...")
    
    # Initialize SDL2
    init_result = sdl2.ext.init()
    print("SDL2 initialized successfully")
    
    # Get display info
    display_mode = sdl2.SDL_DisplayMode()
    result = sdl2.SDL_GetCurrentDisplayMode(0, display_mode)
    
    if result != 0:
        # Use common default resolution
        print("Could not detect display mode, using defaults")
        window_width, window_height = 1920, 1080
        print(f"Using default resolution: {window_width}x{window_height}")
    else:
        window_width, window_height = display_mode.w, display_mode.h
        print(f"Detected display: {window_width}x{window_height}")
    
    # Create window
    print("Creating window...")
    try:
        # Create borderless window for clean display
        window = sdl2.ext.Window(
            "ToasterOS", 
            size=(window_width, window_height),
            flags=sdl2.SDL_WINDOW_BORDERLESS | sdl2.SDL_WINDOW_SHOWN
        )
        
        # Position window at top-left
        sdl2.SDL_SetWindowPosition(window.window, 0, 0)
        print("Created borderless window")
        
    except Exception as e:
        print(f"Borderless window failed: {e}")
        print("Falling back to basic window")
        window = sdl2.ext.Window("ToasterOS", size=(window_width, window_height))
    
    print("Showing window...")
    window.show()
    
    # Try to grab input focus
    try:
        sdl2.SDL_RaiseWindow(window.window)
        sdl2.SDL_SetWindowInputFocus(window.window)
        print("Grabbed input focus")
    except Exception:
        print("Could not grab input focus")
    
    print(f"Window created and shown: {window_width}x{window_height}")
    
    # Brief initialization delay
    time.sleep(0.1)
    print("Initialization complete")

    animation_manager = AnimationManager("Anims", window, interval=0.1)
    animation_manager.load_animations()
    
    # Create app menu
    app_menu = AppMenu(window, animation_manager.renderer)
    
    # Animation control flags
    boot_completed = False
    animation_paused = False
    
    def animation_worker():
        """Worker thread that runs animations"""
        global boot_completed, animation_paused
        if not boot_completed:        
            animation_manager.run_animation("load", loop=False)
            animation_manager.run_animation("bootUp", loop=False)
            boot_completed = True
            print("Boot sequence completed! Menu is now available.")
        
        # After initial animations, run the blink animation in a loop
        print("Starting blink animation loop")
        while animation_manager.running:
            if not animation_paused:
                animation_manager.run_animation("blink", loop=True)
            else:
                time.sleep(0.1)  # Wait while paused
    
    # Start animation thread
    animation_thread = threading.Thread(target=animation_worker, daemon=True)
    animation_thread.start()
    
    # Event handling variables
    swipe_start_x = None
    swipe_threshold = 100
    running = True

    # Main event loop
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                animation_manager.running = False  # Stop animations
                break
            if event.type == sdl2.SDL_KEYDOWN:
                # Quit on Ctrl+Q
                if (event.key.keysym.sym == sdl2.SDLK_q and
                    (event.key.keysym.mod & sdl2.KMOD_CTRL)):
                    running = False
                    animation_manager.running = False
                    break
                # Close app menu on ESC
                elif event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                    if boot_completed and app_menu.is_open:
                        app_menu.toggle()
                        animation_paused = False  # Resume animation
                        print("Menu closed via ESC")
                # Number keys to launch apps when menu is open
                elif boot_completed and app_menu.is_open and sdl2.SDLK_1 <= event.key.keysym.sym <= sdl2.SDLK_8:
                    app_index = event.key.keysym.sym - sdl2.SDLK_1
                    app_menu.launch_app(app_index)
                    animation_paused = False  # Resume animation after app launch
                    print("App launched")

            # Mouse input handling
            if event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                swipe_start_x = event.button.x
            elif event.type == sdl2.SDL_MOUSEBUTTONUP and swipe_start_x is not None:
                swipe_end_x = event.button.x
                swipe_distance = swipe_start_x - swipe_end_x
                
                if abs(swipe_distance) > swipe_threshold:
                    if swipe_distance > 0:
                        # Swipe left - open app menu
                        if boot_completed and not app_menu.is_open:
                            print("Swipe left - Opening app menu!")
                            animation_paused = True  # Pause animation
                            app_menu.toggle()
                    else:
                        # Swipe right - close app menu
                        if boot_completed and app_menu.is_open:
                            print("Swipe right - Closing app menu!")
                            app_menu.toggle()
                            animation_paused = False  # Resume animation
                else:
                    # Regular tap - handle menu clicks
                    if boot_completed and app_menu.handle_click(event.button.x, event.button.y):
                        if not app_menu.is_open:
                            animation_paused = False
                            print("Menu closed via click")
                        
                swipe_start_x = None
        
        # Small delay to prevent excessive CPU usage
        time.sleep(0.001)
        
        # Draw the menu if it's open
        if app_menu.is_open:
            app_menu.draw()
    
    # Clean shutdown
    print("Shutting down...")
    animation_manager.running = False
    animation_thread.join(timeout=1.0)  # Wait for animation thread to finish

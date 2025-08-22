import sdl2.ext
import threading
import time
import os
from animations import AnimationManager
from app_menu import AppMenu

if __name__ == "__main__":
    print("Starting ToasterOS...")
    print("Initializing SDL2 for xinit environment...")
    
    # Initialize SDL2 with explicit settings for xinit (no window manager)
    if 'DISPLAY' in os.environ:
        print(f"X Display detected: {os.environ['DISPLAY']}")
    else:
        print("Warning: No DISPLAY environment variable found")
        # Set default display for xinit
        os.environ['DISPLAY'] = ':0'
        print("Set DISPLAY=:0 for xinit")
    
    # Configure SDL2 for xinit environment (no window manager)
    os.environ['SDL_VIDEODRIVER'] = 'x11'
    # Disable window manager hints since there's no WM
    os.environ['SDL_VIDEO_X11_WMCLASS'] = 'ToasterOS'
    # Force window to be override-redirect (bypass window manager)
    os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
    
    print("SDL2 environment configured for xinit")
    
    # Initialize SDL2
    init_result = sdl2.ext.init()
    print("SDL2 initialized successfully")
    
    # For xinit, we should use the full screen without relying on display mode detection
    # which often fails without a proper window manager
    print("Configuring for xinit (no window manager)...")
    
    # Try to get display info, but use sensible defaults for xinit
    display_mode = sdl2.SDL_DisplayMode()
    result = sdl2.SDL_GetCurrentDisplayMode(0, display_mode)
    
    if result != 0:
        # Common resolutions for xinit setups
        print("Could not detect display mode, using xinit defaults")
        window_width, window_height = 1920, 1080  # Try HD first
        print(f"Using default resolution: {window_width}x{window_height}")
    else:
        window_width, window_height = display_mode.w, display_mode.h
        print(f"Detected display: {window_width}x{window_height}")
    
    # Create window optimized for xinit (no window manager)
    print("Creating xinit-optimized window...")
    try:
        # For xinit, create a borderless window that covers the screen
        window = sdl2.ext.Window(
            "ToasterOS", 
            size=(window_width, window_height),
            flags=sdl2.SDL_WINDOW_BORDERLESS | sdl2.SDL_WINDOW_SHOWN
        )
        
        # Position window at top-left since there's no window manager
        sdl2.SDL_SetWindowPosition(window.window, 0, 0)
        
        print("Created borderless window for xinit")
        
    except Exception as e:
        print(f"Borderless window failed: {e}")
        print("Falling back to basic window")
        window = sdl2.ext.Window("ToasterOS", size=(window_width, window_height))
    
    print("Showing window...")
    window.show()
    
    # For xinit, we need to grab input focus since there's no window manager
    try:
        sdl2.SDL_RaiseWindow(window.window)
        sdl2.SDL_SetWindowInputFocus(window.window)
        print("Grabbed input focus")
    except Exception:
        print("Could not grab input focus (this may be normal for xinit)")
    
    print(f"Window created and shown: {window_width}x{window_height}")
    
    # Longer delay for xinit to initialize properly
    time.sleep(0.5)
    print("Initialization complete")

    animation_manager = AnimationManager("Anims", window, interval=0.1)
    animation_manager.load_animations()
    
    # Create app menu
    app_menu = AppMenu(window, animation_manager.renderer)
    
    # Animation control using a simple flag-based approach
    current_animation_index = 0
    animations_completed = False
    boot_completed = False
    animation_paused = False
    animation_restart = False  # Flag to restart animation
    
    def animation_worker():
        """Worker thread that runs animations"""
        global boot_completed, animation_paused, animation_restart
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
                        animation_restart = True  # Restart animation for responsiveness
                        print("Menu closed via ESC - restarting animation")
                # Number keys to launch apps when menu is open
                elif boot_completed and app_menu.is_open and sdl2.SDLK_1 <= event.key.keysym.sym <= sdl2.SDLK_8:
                    app_index = event.key.keysym.sym - sdl2.SDLK_1
                    app_menu.launch_app(app_index)
                    animation_paused = False  # Resume animation after app launch
                    animation_restart = True  # Restart animation for responsiveness
                    print("App launched - restarting animation")

            # Detect swipe left
            if event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                swipe_start_x = event.button.x
                print(f"Mouse down at: {event.button.x}")
            elif event.type == sdl2.SDL_MOUSEBUTTONUP and swipe_start_x is not None:
                swipe_end_x = event.button.x
                swipe_distance = swipe_start_x - swipe_end_x
                print(f"Mouse up at: {event.button.x}, distance: {swipe_distance}")
                
                if abs(swipe_distance) > swipe_threshold:
                    if swipe_distance > 0:
                        # Swipe left - open app menu (only if boot completed)
                        if boot_completed:
                            print("Swipe left detected - Opening app menu!")
                            if not app_menu.is_open:
                                animation_paused = True  # Pause animation
                                app_menu.toggle()
                                # Menu will be drawn in the main loop
                        else:
                            print("Swipe left detected - Boot sequence still in progress...")
                    else:
                        # Swipe right - close app menu (only if boot completed)
                        if boot_completed:
                            print("Swipe right detected - Closing app menu!")
                            if app_menu.is_open:
                                app_menu.toggle()
                                animation_paused = False  # Resume animation
                                animation_restart = True  # Restart animation for responsiveness
                                print("Menu closed via swipe - restarting animation")
                                animation_thread.join(timeout=1.0)  # Wait for animation thread to finish
                                animation_thread = None
                                animation_thread = threading.Thread(target=animation_worker, daemon=True)
                                animation_thread.start()  # Restart animation thread

                else:
                    # Regular tap - handle menu clicks (only if boot completed)
                    if boot_completed and app_menu.handle_click(event.button.x, event.button.y):
                        # If the menu was closed or an app was launched, resume animation
                        if not app_menu.is_open:
                            animation_paused = False
                            animation_restart = True  # Restart animation for responsiveness
                            print("Menu closed via click - restarting animation")
                        
                swipe_start_x = None
        
        # Small delay to prevent excessive CPU usage in main loop
        time.sleep(0.001)
        
        # Draw the menu if it's open (this ensures the menu stays visible)
        if app_menu.is_open:
            app_menu.draw()
    
    # Clean shutdown
    print("Shutting down...")
    animation_manager.running = False
    animation_thread.join(timeout=1.0)  # Wait for animation thread to finish

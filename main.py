import sdl2.ext
import threading
import time
from animations import AnimationManager
from app_menu import AppMenu

if __name__ == "__main__":
    sdl2.ext.init()
    display_mode = sdl2.SDL_DisplayMode()
    sdl2.SDL_GetCurrentDisplayMode(0, display_mode)
    window = sdl2.ext.Window("System", size=(display_mode.w, display_mode.h), flags=sdl2.SDL_WINDOW_FULLSCREEN)
    window.show()

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
            animation_manager.run_animation("load")
            animation_manager.run_animation("bootUp")
            boot_completed = True
            print("Boot sequence completed! Menu is now available.")
        
        # After initial animations, run the blink animation in a loop
        print("Starting blink animation loop")
        while True:
            animation_manager.run_animation("blink")
    
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
                                animation_thread.join(timeout=0)
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

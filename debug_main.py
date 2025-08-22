#!/usr/bin/env python3
"""
Minimal ToasterOS for debugging Alpine Linux issues
This version removes complexity to isolate window creation problems
"""

import sdl2
import sdl2.ext
import time
import os
from animations import AnimationManager

def main():
    print("=== Minimal ToasterOS Debug Version for XINIT ===")
    
    # Configure for xinit
    if 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':0'
        print("Set DISPLAY=:0 for xinit")
    
    os.environ['SDL_VIDEODRIVER'] = 'x11'
    os.environ['SDL_VIDEO_X11_WMCLASS'] = 'ToasterOS'
    os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
    print(f"Display: {os.environ.get('DISPLAY')}")
    print("Configured for xinit (no window manager)")
    
    # Initialize SDL2
    print("Initializing SDL2...")
    try:
        sdl2.ext.init()
        print("SDL2 initialized successfully")
    except Exception as e:
        print(f"SDL2 init failed: {e}")
        return
    
    # Create xinit-optimized window
    print("Creating xinit-optimized window...")
    try:
        # Create borderless window for xinit
        window = sdl2.ext.Window(
            "ToasterOS Debug", 
            size=(800, 600),
            flags=sdl2.SDL_WINDOW_BORDERLESS | sdl2.SDL_WINDOW_SHOWN
        )
        
        # Position at top-left
        sdl2.SDL_SetWindowPosition(window.window, 0, 0)
        
        window.show()
        print("Borderless window created and shown")
        
        # Try to grab focus
        try:
            sdl2.SDL_RaiseWindow(window.window)
            sdl2.SDL_SetWindowInputFocus(window.window)
            print("Input focus grabbed")
        except Exception:
            print("Could not grab input focus (normal for xinit)")
        
        # Create renderer
        renderer = sdl2.ext.Renderer(window)
        print("Renderer created")
        
        # Test basic rendering with green background
        print("Testing basic rendering...")
        renderer.clear(sdl2.ext.Color(0, 100, 0))  # Dark green
        renderer.present()
        
        # Wait a moment
        time.sleep(1)
        
        # Try to load a simple animation
        print("Testing animation system...")
        try:
            anim_manager = AnimationManager("Anims", window)
            anim_manager.load_animations()
            print(f"Animations loaded: {list(anim_manager.animations.keys())}")
            
            # Test a simple animation
            if 'blink' in anim_manager.animations:
                print("Testing blink animation...")
                # Run just a few cycles for testing
                anim_manager.run_animation('blink', loop=False)
            else:
                print("No blink animation found")
                
        except Exception as e:
            print(f"Animation system error: {e}")
            import traceback
            traceback.print_exc()
        
        # Keep window open
        print("Window should be visible. Press ESC to exit.")
        print("For xinit: Window should be borderless at top-left")
        running = True
        while running:
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    running = False
                    break
                elif event.type == sdl2.SDL_KEYDOWN:
                    if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                        print("ESC pressed - exiting")
                        running = False
                        break
                    elif event.key.keysym.sym == sdl2.SDLK_SPACE:
                        print("Space pressed - testing renderer")
                        renderer.clear(sdl2.ext.Color(100, 0, 100))  # Purple
                        renderer.present()
            
            time.sleep(0.1)
        
    except Exception as e:
        print(f"Window creation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Cleanup
    print("Cleaning up...")
    sdl2.ext.quit()
    print("Done")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()

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
    print("=== Minimal ToasterOS Debug Version ===")
    
    # Force X11
    os.environ['SDL_VIDEODRIVER'] = 'x11'
    print(f"Display: {os.environ.get('DISPLAY', 'NOT SET')}")
    
    # Initialize SDL2
    print("Initializing SDL2...")
    try:
        sdl2.ext.init()
        print("SDL2 initialized successfully")
    except Exception as e:
        print(f"SDL2 init failed: {e}")
        return
    
    # Create window with basic settings
    print("Creating window...")
    try:
        # Start with simple windowed mode
        window = sdl2.ext.Window("ToasterOS Debug", size=(800, 600))
        window.show()
        print("Window created and shown")
        
        # Create renderer
        renderer = sdl2.ext.Renderer(window)
        print("Renderer created")
        
        # Test basic rendering
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
                anim_manager.run_animation('blink', loop=False)
            else:
                print("No blink animation found")
                
        except Exception as e:
            print(f"Animation system error: {e}")
            import traceback
            traceback.print_exc()
        
        # Keep window open
        print("Window should be visible. Press Ctrl+C to exit or close window.")
        running = True
        while running:
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    running = False
                    break
                elif event.type == sdl2.SDL_KEYDOWN:
                    if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                        running = False
                        break
            
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

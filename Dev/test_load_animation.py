#!/usr/bin/env python3
"""
Test the load animation specifically
"""

import os
import sdl2
import sdl2.ext
import time
from animations import AnimationManager

def test_load_animation():
    """Test the load animation that contains videos"""
    
    # Initialize SDL2
    sdl2.ext.init()
    
    try:
        # Create window
        window = sdl2.ext.Window("Load Animation Test", size=(800, 600))
        window.show()
        
        # Create animation manager
        anim_manager = AnimationManager("Anims", window)
        
        # Load animations
        anim_manager.load_animations()
        
        print("Available animations:", list(anim_manager.animations.keys()))
        
        if 'load' in anim_manager.animations:
            print("Load animation sequence:")
            for i, item in enumerate(anim_manager.animations['load']['sequence']):
                print(f"  {i}: {item}")
            
            print("\nStarting load animation...")
            print("Press ESC or close window to exit")
            
            # Run the load animation (just once, no loop)
            anim_manager.run_animation('load', loop=False)
        else:
            print("Load animation not found")
        
        print("Animation test completed")
        
    except Exception as e:
        print(f"Error during animation test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        sdl2.ext.quit()

if __name__ == "__main__":
    test_load_animation()

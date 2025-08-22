#!/usr/bin/env python3
"""
Test the frame-based animation system (no more OpenCV needed!)
"""

import sdl2
import sdl2.ext
from animations import AnimationManager

def test_frame_animation():
    """Test the frame-based load animation"""
    
    # Initialize SDL2
    sdl2.ext.init()
    
    try:
        # Create a smaller window for testing (not fullscreen)
        window = sdl2.ext.Window("Frame Animation Test", size=(800, 600))
        window.show()
        
        # Create animation manager
        anim_manager = AnimationManager("Anims", window)
        
        # Load animations
        anim_manager.load_animations()
        
        print("Available animations:", list(anim_manager.animations.keys()))
        
        if 'load' in anim_manager.animations:
            load_anim = anim_manager.animations['load']
            print(f"Load animation has {len(load_anim['sequence'])} items")
            print(f"Interval: {load_anim['interval']} seconds")
            print(f"Fill mode: {load_anim['fill']}")
            
            print("\nFirst 10 items:")
            for i, item in enumerate(load_anim['sequence'][:10]):
                print(f"  {i}: {item}")
            
            print("\nLast 5 items:")
            for i, item in enumerate(load_anim['sequence'][-5:], len(load_anim['sequence'])-5):
                print(f"  {i}: {item}")
            
            print(f"\nTesting load animation with {len(load_anim['sequence'])} frames...")
            print("This should now work without OpenCV!")
            print("Press ESC or close window to exit")
            
            # Run the load animation (just once, no loop)
            anim_manager.run_animation('load', loop=False)
        else:
            print("Load animation not found")
        
        print("Frame-based animation test completed!")
        
    except Exception as e:
        print(f"Error during animation test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        sdl2.ext.quit()

if __name__ == "__main__":
    test_frame_animation()

#!/usr/bin/env python3
"""
Simple test script to verify video playback with OpenCV and SDL2
"""

import os
import sdl2
import sdl2.ext
import time
from Libs.animations import AnimationManager

def test_video_playback():
    """Test video playback functionality"""
    
    # Initialize SDL2
    sdl2.ext.init()
    
    try:
        # Create window
        window = sdl2.ext.Window("Video Test", size=(800, 600))
        window.show()
        
        # Create animation manager
        anim_manager = AnimationManager("Anims", window)
        
        # Test video file path
        video_path = os.path.join("Anims", "load", "start.mp4")
        
        if not os.path.exists(video_path):
            print(f"Video file not found: {video_path}")
            return
        
        print(f"Testing video playback: {video_path}")
        print("Press ESC or close window to exit")
        
        # Start video playback
        anim_manager.play_video(video_path)
        
        print("Video playback completed. Window will stay open for 3 seconds...")
        
        # Keep window open for a few seconds after video ends
        start_time = time.time()
        while time.time() - start_time < 3.0:
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    return
            time.sleep(0.1)
        
        print("Video playback test completed")
        
    except Exception as e:
        print(f"Error during video test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        sdl2.ext.quit()

if __name__ == "__main__":
    test_video_playback()

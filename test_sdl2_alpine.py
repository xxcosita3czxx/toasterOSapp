#!/usr/bin/env python3
"""
SDL2 diagnostics script for Alpine Linux X server compatibility
Run this to test if SDL2 can create windows properly
"""

import sdl2
import sdl2.ext
import time
import os

def test_sdl2_alpine():
    """Test SDL2 functionality in Alpine Linux environment"""
    
    print("=== SDL2 Alpine Linux Diagnostic ===")
    print()
    
    # Check environment
    print("1. Environment Check:")
    print(f"   DISPLAY: {os.environ.get('DISPLAY', 'NOT SET')}")
    print(f"   WAYLAND_DISPLAY: {os.environ.get('WAYLAND_DISPLAY', 'NOT SET')}")
    print(f"   XDG_SESSION_TYPE: {os.environ.get('XDG_SESSION_TYPE', 'NOT SET')}")
    print()
    
    # Force X11 driver
    print("2. Setting SDL2 to use X11 driver...")
    os.environ['SDL_VIDEODRIVER'] = 'x11'
    print("   SDL_VIDEODRIVER = x11")
    print()
    
    # Initialize SDL2
    print("3. Initializing SDL2...")
    try:
        result = sdl2.ext.init()
        if result != 0:
            print(f"   ERROR: SDL2 init failed with code {result}")
            print(f"   SDL Error: {sdl2.SDL_GetError().decode()}")
            return False
        print("   SUCCESS: SDL2 initialized")
    except Exception as e:
        print(f"   ERROR: Exception during SDL2 init: {e}")
        return False
    print()
    
    # Check video drivers
    print("4. Available video drivers:")
    num_drivers = sdl2.SDL_GetNumVideoDrivers()
    for i in range(num_drivers):
        driver_name = sdl2.SDL_GetVideoDriver(i).decode()
        print(f"   {i}: {driver_name}")
    
    current_driver = sdl2.SDL_GetCurrentVideoDriver()
    if current_driver:
        print(f"   Current driver: {current_driver.decode()}")
    else:
        print("   Current driver: None (ERROR)")
    print()
    
    # Check displays
    print("5. Display information:")
    num_displays = sdl2.SDL_GetNumVideoDisplays()
    print(f"   Number of displays: {num_displays}")
    
    for i in range(num_displays):
        display_mode = sdl2.SDL_DisplayMode()
        result = sdl2.SDL_GetCurrentDisplayMode(i, display_mode)
        if result == 0:
            print(f"   Display {i}: {display_mode.w}x{display_mode.h} @ {display_mode.refresh_rate}Hz")
        else:
            print(f"   Display {i}: ERROR - {sdl2.SDL_GetError().decode()}")
    print()
    
    # Test window creation
    print("6. Testing window creation...")
    try:
        # Try simple window first
        window = sdl2.ext.Window("SDL2 Test", size=(640, 480))
        print("   SUCCESS: Window object created")
        
        window.show()
        print("   SUCCESS: Window shown")
        
        # Test renderer
        renderer = sdl2.ext.Renderer(window)
        print("   SUCCESS: Renderer created")
        
        # Clear screen to red
        renderer.clear(sdl2.ext.Color(255, 0, 0))
        renderer.present()
        print("   SUCCESS: Red screen rendered")
        
        print("   Window should be visible with red background")
        print("   Waiting 3 seconds...")
        
        # Wait and handle events
        for i in range(30):  # 3 seconds at ~10 FPS
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    print("   Window closed by user")
                    sdl2.ext.quit()
                    return True
            time.sleep(0.1)
        
        print("   Test completed successfully!")
        
    except Exception as e:
        print(f"   ERROR: Window creation failed: {e}")
        sdl2.ext.quit()
        return False
    
    # Cleanup
    sdl2.ext.quit()
    print("   SDL2 cleaned up")
    print()
    print("=== Diagnostic Complete ===")
    return True

if __name__ == "__main__":
    success = test_sdl2_alpine()
    if success:
        print("✅ SDL2 appears to be working correctly")
        print("Your ToasterOS application should work!")
    else:
        print("❌ SDL2 has issues in this environment")
        print("Check your X server setup and SDL2 installation")

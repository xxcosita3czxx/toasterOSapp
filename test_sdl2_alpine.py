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
    """Test SDL2 functionality in Alpine Linux xinit environment"""
    
    print("=== SDL2 Alpine Linux XINIT Diagnostic ===")
    print()
    
    # Check environment
    print("1. Environment Check:")
    print(f"   DISPLAY: {os.environ.get('DISPLAY', 'NOT SET')}")
    print(f"   WAYLAND_DISPLAY: {os.environ.get('WAYLAND_DISPLAY', 'NOT SET')}")
    print(f"   XDG_SESSION_TYPE: {os.environ.get('XDG_SESSION_TYPE', 'NOT SET')}")
    
    # Set up for xinit if needed
    if 'DISPLAY' not in os.environ:
        print("   Setting DISPLAY=:0 for xinit")
        os.environ['DISPLAY'] = ':0'
    
    print()
    
    # Force X11 driver and xinit-specific settings
    print("2. Setting SDL2 for xinit environment...")
    os.environ['SDL_VIDEODRIVER'] = 'x11'
    os.environ['SDL_VIDEO_X11_WMCLASS'] = 'ToasterOS'
    os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
    print("   SDL_VIDEODRIVER = x11")
    print("   SDL_VIDEO_X11_WMCLASS = ToasterOS")
    print("   SDL_VIDEO_WINDOW_POS = 0,0")
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
    
    # Test window creation for xinit
    print("6. Testing xinit-optimized window creation...")
    try:
        # Try xinit-style borderless window
        window = sdl2.ext.Window(
            "SDL2 XINIT Test", 
            size=(640, 480),
            flags=sdl2.SDL_WINDOW_BORDERLESS | sdl2.SDL_WINDOW_SHOWN
        )
        print("   SUCCESS: Borderless window created")
        
        # Position at top-left
        sdl2.SDL_SetWindowPosition(window.window, 0, 0)
        print("   SUCCESS: Window positioned at 0,0")
        
        window.show()
        print("   SUCCESS: Window shown")
        
        # Try to grab focus
        try:
            sdl2.SDL_RaiseWindow(window.window)
            sdl2.SDL_SetWindowInputFocus(window.window)
            print("   SUCCESS: Input focus grabbed")
        except Exception:
            print("   INFO: Could not grab input focus (normal for xinit)")
        
        # Test renderer
        renderer = sdl2.ext.Renderer(window)
        print("   SUCCESS: Renderer created")
        
        # Clear screen to blue (good for xinit testing)
        renderer.clear(sdl2.ext.Color(0, 0, 255))
        renderer.present()
        print("   SUCCESS: Blue screen rendered")
        
        print("   Window should be visible with blue background")
        print("   For xinit: should be borderless and positioned at top-left")
        print("   Waiting 3 seconds...")
        
        # Wait and handle events
        for i in range(30):  # 3 seconds at ~10 FPS
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    print("   Window closed by user")
                    sdl2.ext.quit()
                    return True
                elif event.type == sdl2.SDL_KEYDOWN:
                    if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                        print("   ESC pressed - closing")
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
    print("=== XINIT Diagnostic Complete ===")
    return True

if __name__ == "__main__":
    success = test_sdl2_alpine()
    if success:
        print("✅ SDL2 appears to be working correctly with xinit")
        print("Your ToasterOS application should work!")
        print()
        print("XINIT Tips:")
        print("- Make sure you run this from within xinit session") 
        print("- The window should appear borderless and fill the screen")
        print("- Use Ctrl+C or ESC to exit applications")
    else:
        print("❌ SDL2 has issues in this xinit environment")
        print("Check your X server setup and SDL2 installation")
        print()
        print("Common xinit issues:")
        print("- DISPLAY not set (should be :0)")
        print("- X server not running")
        print("- Missing SDL2 X11 support: apk add sdl2-dev")

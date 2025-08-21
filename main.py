import sdl2.ext
from animations import AnimationManager

if __name__ == "__main__":
    sdl2.ext.init()
    display_mode = sdl2.SDL_DisplayMode()
    sdl2.SDL_GetCurrentDisplayMode(0, display_mode)
    window = sdl2.ext.Window("Shared Animation Window", size=(display_mode.w, display_mode.h), flags=sdl2.SDL_WINDOW_FULLSCREEN)
    window.show()

    animation_manager = AnimationManager("Images", window, interval=0.1)  # Replace "Images" with your folder containing images
    animation_manager.load_animations()
    animation_manager.run_animation("load")  # Replace with the desired animation name
    animation_manager.run_animation("bootUp")
    animation_manager.run_animation("blink", loop=True)  # Replace with the desired animation name

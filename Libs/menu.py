import sdl2
import sdl2.ext

def draw_menu(renderer, window_w, window_h, menu_pad=50, menu_color=(136, 136, 136)):
    """
    Draws a gray menu block padded 50px from the sides onto the given renderer.
    """
    renderer.clear(sdl2.ext.Color(0, 0, 0))  # Clear with black
    color = sdl2.ext.Color(*menu_color)
    menu_rect = sdl2.SDL_Rect(menu_pad, menu_pad, window_w - 2 * menu_pad, window_h - 2 * menu_pad)
    renderer.fill(menu_rect, color)
    renderer.present()

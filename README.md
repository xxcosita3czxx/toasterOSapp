# ToasterOS Touch-Optimized App Manager

A touch-optimized honeycomb-layout application manager that runs on top of X using SDL2. Designed specifically for touchscreen devices with intuitive gesture controls and larger touch targets. The first registered application appears in the center, with subsequent apps arranged in hexagonal rings around it.

## Features

- **Touch-Optimized Design**: Large touch targets and intuitive gesture controls
- **Apple-Style Honeycomb Layout**: Apps arranged in beautiful hexagonal pattern mimicking classic Apple interface
- **Advanced Touch Gestures**: Tap, long press, swipe, and pinch-to-zoom support
- **Visual Touch Feedback**: Immediate visual response to touch interactions
- **Intelligent Navigation**: UP/DOWN moves toward center or edges, swipe gestures for ring navigation
- **Zoom Support**: Pinch-to-zoom for better accessibility and customization
- **SDL2 Graphics**: Hardware-accelerated rendering with smooth animations
- **Cross-Platform**: Works on Linux, Windows, and touch-enabled devices
- **Smart Icons**: Different visual symbols for different app types with scaling
- **Configurable**: Easy customization through config.ini

## Installation

1. Make sure you have Python 3.7+ installed
2. Install PySDL2:
   ```bash
   pip install PySDL2
   ```

## Usage

### Basic Usage
```bash
python main.py
```

### Enhanced Version with Configuration
```bash
python app_manager.py
```

### Touch Controls (Primary Interface)

- **TAP**: Select and launch an application instantly
- **LONG PRESS**: Show app information or context menu (500ms hold)
- **SWIPE LEFT/RIGHT**: Navigate clockwise/counter-clockwise within current ring
- **SWIPE UP**: Move toward center or inner rings
- **SWIPE DOWN**: Move toward outer rings or away from center
- **PINCH ZOOM**: Two-finger pinch to zoom in/out (0.5x to 2.0x)
- **TOUCH DRAG**: Pan the view (future feature)

### Keyboard Controls (Fallback)

- **UP Arrow**: Move left or to center (Apple-style navigation)
- **DOWN Arrow**: Move right or to center (Apple-style navigation)
- **LEFT/RIGHT Arrows**: Navigate clockwise/counter-clockwise within current ring
- **Enter/Space**: Launch the selected application
- **Escape**: Quit the app manager

## Configuration

Edit `config.ini` to customize the app manager:

### Adding Applications
```ini
[apps]
Terminal = gnome-terminal
File Manager = nautilus
Web Browser = firefox
Text Editor = gedit
```

For Windows:
```ini
[apps]
Terminal = cmd.exe
File Manager = explorer.exe
Web Browser = "C:\Program Files\Mozilla Firefox\firefox.exe"
Text Editor = notepad.exe
```

### Appearance Settings
```ini
[appearance]
hex_size = 80
width = 1200
height = 800
background_color = 20, 25, 40, 255
app_color = 60, 70, 90, 255
selected_color = 100, 150, 200, 255
text_color = 255, 255, 255, 255
```

## Layout Structure

The honeycomb layout organizes apps in rings:

```
        6   1   7
      5   0   2   8
        4   3   9
```

- **Ring 0**: Center (1 app) - First registered app
- **Ring 1**: Inner ring (6 apps) - Apps 2-7
- **Ring 2**: Middle ring (12 apps) - Apps 8-19
- **Ring 3**: Outer ring (18 apps) - Apps 20-37

## Architecture

- **App Class**: Represents individual applications
- **HoneycombLayout Class**: Manages positioning logic
- **AppManager Class**: Main application controller
- **SDL2 Integration**: Handles graphics and input

## Requirements

- Python 3.7+
- PySDL2
- X Window System (Linux) or Windows

## Platform-Specific Notes

### Linux
- Uses standard Linux executables (gnome-terminal, nautilus, etc.)
- Requires X Window System

### Windows
- Uses Windows executables (cmd.exe, explorer.exe, etc.)
- Native Windows support

## Troubleshooting

### SDL2 Not Found
If you get SDL2 errors, make sure PySDL2 is installed:
```bash
pip install PySDL2
```

### App Launch Failures
- Check that the executable paths in config.ini are correct
- Ensure the applications are installed on your system
- Use full paths for custom applications

### Performance Issues
- Reduce window size in config.ini
- Lower the hex_size value for tighter spacing

## Development

The code is structured for easy extension:

1. **Adding new app types**: Extend the App class
2. **Custom layouts**: Modify HoneycombLayout class
3. **New rendering**: Extend AppManager._draw_app()
4. **Configuration options**: Add to config.ini parser

## License

MIT License - Feel free to modify and distribute.

#!/usr/bin/env python3
"""
ToasterOS Touch-Optimized App Manager
Entry point for the touch-optimized honeycomb app manager
"""

import sys
from app_manager import AppManager


def main():
    """Main entry point for touch-optimized app manager"""
    print("Starting ToasterOS Touch-Optimized App Manager...")
    
    app_manager = None
    
    try:
        app_manager = AppManager()
        app_manager.run()
    
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        if app_manager:
            app_manager.cleanup()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

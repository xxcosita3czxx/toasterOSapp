import os
import subprocess
import sys

def setup_xdg_runtime_dir():
    """Ensure XDG_RUNTIME_DIR is set up with correct permissions."""
    if "XDG_RUNTIME_DIR" not in os.environ:
        os.environ["XDG_RUNTIME_DIR"] = "/tmp/runtime-dir"
    runtime_dir = os.environ["XDG_RUNTIME_DIR"]
    try:
        os.makedirs(runtime_dir, exist_ok=True)
        os.chmod(runtime_dir, 0o700)
    except Exception as e:
        print(f"Failed to set up XDG_RUNTIME_DIR: {e}")
        sys.exit(1)

def start_x_server():
    """Start the X server and capture its output."""
    try:
        setup_xdg_runtime_dir()

        print("Starting X server...")
        x_server_process = subprocess.Popen(
            ["xinit", "--", ":1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return x_server_process
    except FileNotFoundError:
        print("Error: xinit not found. Please ensure X server is installed.")
        sys.exit(1)

def run_application(app_command):
    """Run the SDL2 application in the X server environment."""
    try:
        print(f"Running application: {app_command}")
        
        # Configure environment for xinit (no window manager)
        app_env = {
            "DISPLAY": ":1", 
            "XDG_RUNTIME_DIR": os.environ["XDG_RUNTIME_DIR"],
            # SDL2 configuration for xinit environment
            "SDL_VIDEODRIVER": "x11",
            "SDL_VIDEO_X11_WMCLASS": "ToasterOS",
            "SDL_VIDEO_WINDOW_POS": "0,0"
        }
        
        print("Configured SDL2 environment for xinit")
        subprocess.run(app_command, check=True, env=app_env)
    except subprocess.CalledProcessError as e:
        print(f"Application exited with error: {e}")

def stop_x_server(x_server_process):
    """Stop the X server and display its output."""
    print("Stopping X server...")
    x_server_process.terminate()
    stdout, stderr = x_server_process.communicate()
    print("X server output:")
    print(stdout.decode())
    print(stderr.decode())

def main():
    if len(sys.argv) < 2:
        print("Usage: python x_server_runner.py <application_command>")
        sys.exit(1)

    app_command = sys.argv[1:]

    # Start X server
    x_server_process = start_x_server()

    try:
        # Run the application
        run_application(app_command)
    finally:
        # Stop X server
        stop_x_server(x_server_process)

if __name__ == "__main__":
    main()

import os
import subprocess
import sys
import time

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
        # Start X server without xterm and hide cursor
        x_server_process = subprocess.Popen(
            ["xinit", "/bin/true", "--", ":1", "-nocursor"],
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
        }
        
        print("Configured SDL2 environment for xinit")
        result = subprocess.run(app_command, check=False, env=app_env, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Application failed with exit code {result.returncode}")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
        else:
            print("Application completed successfully")
            
    except Exception as e:
        print(f"Error running application: {e}")

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
        print("Usage: python startx-toasteros.py <application_command>")
        sys.exit(1)

    app_command = sys.argv[1:]

    # Start X server
    x_server_process = start_x_server()

    try:
        # Wait for X server to be ready
        print("Waiting for X server to initialize...")
        time.sleep(2)
        
        # Run the application
        run_application(app_command)
    finally:
        # Stop X server
        stop_x_server(x_server_process)

if __name__ == "__main__":
    main()

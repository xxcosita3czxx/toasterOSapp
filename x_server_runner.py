import os
import subprocess
import sys

def start_x_server():
    """Start the X server."""
    try:
        # Ensure XDG_RUNTIME_DIR is set
        if "XDG_RUNTIME_DIR" not in os.environ:
            os.environ["XDG_RUNTIME_DIR"] = "/tmp/runtime-dir"
            os.makedirs(os.environ["XDG_RUNTIME_DIR"], exist_ok=True)

        print("Starting X server...")
        x_server_process = subprocess.Popen(["xinit", "--", ":1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return x_server_process
    except FileNotFoundError:
        print("Error: xinit not found. Please ensure X server is installed.")
        sys.exit(1)

def run_application(app_command):
    """Run the SDL2 application in the X server environment."""
    try:
        print(f"Running application: {app_command}")
        subprocess.run(app_command, check=True, env={"DISPLAY": ":1"})
    except subprocess.CalledProcessError as e:
        print(f"Application exited with error: {e}")

def stop_x_server(x_server_process):
    """Stop the X server."""
    print("Stopping X server...")
    x_server_process.terminate()
    x_server_process.wait()

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

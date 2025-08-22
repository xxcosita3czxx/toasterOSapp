# ToasterOS OpenRC Service Installation

## 1. Install the service file
```bash
# Copy the service file to OpenRC directory
sudo cp toasteros /etc/init.d/

# Make it executable
sudo chmod +x /etc/init.d/toasteros
```

## 2. Edit the service file paths
```bash
sudo nano /etc/init.d/toasteros
```

Change these lines to match your installation:
```bash
command_args="/path/to/ToasterOSapp/startx-toasteros.py python /path/to/ToasterOSapp/main.py"
```

For example, if your files are in `/home/user/ToasterOSapp/`:
```bash
command_args="/home/user/ToasterOSapp/startx-toasteros.py python /home/user/ToasterOSapp/main.py"
```

## 3. Enable and start the service
```bash
# Enable the service to start at boot
sudo rc-update add toasteros default

# Start the service now
sudo rc-service toasteros start

# Check service status
sudo rc-service toasteros status

# View logs
tail -f /var/log/messages | grep toasteros
```

## 4. Control the service
```bash
# Start
sudo rc-service toasteros start

# Stop
sudo rc-service toasteros stop

# Restart
sudo rc-service toasteros restart

# Remove from boot
sudo rc-update del toasteros default
```

## Notes
- The service runs as root by default (needed for X server access)
- Change `command_user="root"` to another user if needed
- The service will automatically start ToasterOS on boot
- X server and applications will run in the background

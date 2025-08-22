# Install systemd on Alpine Linux and use .service files

## 1. Install systemd on Alpine
```bash
# Add systemd packages
sudo apk add systemd systemd-openrc

# Switch to systemd (optional, but recommended for full systemd experience)
sudo setup-systemd
```

## 2. Install the service file
```bash
# Copy service file
sudo cp toasteros.service /etc/systemd/system/

# Edit the paths in the service file
sudo nano /etc/systemd/system/toasteros.service
```

Change these paths to match your installation:
```
WorkingDirectory=/home/user/ToasterOSapp
ExecStart=/usr/bin/python3 /home/user/ToasterOSapp/startx-toasteros.py python /home/user/ToasterOSapp/main.py
```

## 3. Enable and start the service
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start at boot
sudo systemctl enable toasteros.service

# Start the service now
sudo systemctl start toasteros.service

# Check status
sudo systemctl status toasteros.service

# View logs
sudo journalctl -u toasteros.service -f
```

## 4. Control the service
```bash
# Start
sudo systemctl start toasteros

# Stop
sudo systemctl stop toasteros

# Restart
sudo systemctl restart toasteros

# Disable from boot
sudo systemctl disable toasteros

# Check logs
sudo journalctl -u toasteros --no-pager
```

## Notes
- This installs full systemd on Alpine Linux
- The service will auto-restart if it crashes
- Logs are handled by systemd journal
- You can use standard systemctl commands

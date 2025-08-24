import os

os.system("python3 -m pip install --break -r requirements.txt")
os.system("cp /root/toasterOSapp/toasteros-tty /etc/init.d/toasteros")
os.system("chmod +x /etc/init.d/toasteros")
os.system("rc-update add toasteros default")
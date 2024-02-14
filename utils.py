import socket
import time
import random
from hashlib import sha256
from pathlib import Path
import netifaces

def get_device_ip():
    """
    return device ip
    """
    try: 
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(('8.8.8.8', 53))
                local_ip = s.getsockname()[0]
        return local_ip

    except socket.error as se:
        print("Socket error occurred, trying local way")

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: 
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect(('192.255.255.252', 1))    
            ip = s.getsockname()[0]
        return ip

    except Exception as e: 
        print("can't get the device ip: ", e)
        exit() 


def get_device_name(): 
    return socket.gethostname() 

def check_network():
    """
    return True if connected to a network else False
    """
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        if interface != "lo" and _check_interface_connected(interface):
            return True
    return False

def _check_interface_connected(interface):
    """
    check addresses of a network interface 
    """
    addresses = netifaces.ifaddresses(interface)
    if netifaces.AF_INET in addresses:
        return True
    return False

def get_unique_id():
    """
    return the unique id 
    """
    file_path = Path(__file__).parent / "uid"
    if (file_path.exists()):
        with open(file_path.resolve(), "rb") as file:
            uid = file.read()
    else:
        uid = _generate_unique_id()
        with open(file_path.resolve(), "wb") as file:
            file.write(uid)
    return uid

def _generate_unique_id():
    _temp = str(time.time()).encode() + str(random.randint(0,1000000)).encode()
    return sha256(_temp).digest()
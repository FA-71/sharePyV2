import socket
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
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        if interface != "lo" and _check_interface_connected(interface):
            return True
    return False

def _check_interface_connected(interface):
    addresses = netifaces.ifaddresses(interface)
    if netifaces.AF_INET in addresses:
        return True
    return False
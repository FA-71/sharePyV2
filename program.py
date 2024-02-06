import socket
import threading


BROADCAST_PORT = 42068


class Server: 
    def __init__ (self): 
        try: 
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: 
                print("staring ")
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.connect(('192.255.255.252', 1))    
                self.server_ip = s.getsockname()[0]
                print("ip: ",self.server_ip)
        except Exception as e: 
            print("failed", e)
            return 
    
    
    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server: 
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((socket.gethostbyname(socket.gethostname()), BROADCAST_PORT))

            print("Server started. Waiting for devices...")

            while True:
                data, addr = server.recvfrom(1024)
                print(f"Received message from {addr}: {data.decode()}")


class Client: 
    def __init__(self): 
        return 
    
    def broadcast_self(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: 
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            broadcast_addr = ('<broadcast>', BROADCAST_PORT)
            print("sending ")
            for i in range(5): 
                s.sendto("this is test".encode(), broadcast_addr)
        

def main():
    server = Server()
    server_thread = threading.Thread(target=server.start_server)
    server_thread.start()

    if (input("enter y: ") == "y"): 
        client = Client() 
        client_thread = threading.Thread(target=client.broadcast_self)
        client_thread.start()

    server_thread.join()
    client_thread.join()


if __name__ == "__main__":
    main()
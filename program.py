import socket


class Server: 
    def __init__ (self): 
        return 
    
    def start_server():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('127.0.0.1', 55555))

        print("Server started. Waiting for devices...")

        while True:
            data, addr = server_socket.recvfrom(1024)
            print(f"Received message from {addr}: {data.decode()}")
            # Optionally, you can add logic to verify if the received message is from a valid device and perform actions accordingly



def main():
    server = Server()
    server.start_server()


if __name__ == "__main__":
    main()
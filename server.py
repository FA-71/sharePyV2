import socket

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', 55555))

    print("Server started. Waiting for devices...")

    while True:
        data, addr = server_socket.recvfrom(1024)
        print(f"Received message from {addr}: {data.decode()}")
        # Optionally, you can add logic to verify if the received message is from a valid device and perform actions accordingly

if __name__ == "__main__":
    start_server()

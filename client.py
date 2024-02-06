import socket 

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: 
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    broadcast_addr = ('127.0.0.1', 55555)
    print("sending ")
    for i in range(5): 
        s.sendto("this is test".encode(), broadcast_addr)
    
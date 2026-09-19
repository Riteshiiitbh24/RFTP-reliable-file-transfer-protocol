import socket

# Define IP and port for the UDP Foundation
SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080

# Create the UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

print(f"Server is listening on port {SERVER_PORT}...")

# Wait forever for a basic datagram
while True:
    data, addr = server_socket.recvfrom(1024)
    print(f"Received message from client: {data.decode('utf-8')}")
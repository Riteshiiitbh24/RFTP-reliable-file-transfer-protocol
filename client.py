import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080

# Create the UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# The message to send
message = "Hello, this is my first UDP packet!".encode('utf-8')

# Send the basic datagram
print("Sending message to the server...")
client_socket.sendto(message, (SERVER_IP, SERVER_PORT))

client_socket.close()
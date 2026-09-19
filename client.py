import socket
import struct

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080
CHUNK_SIZE = 1024
# Header: Seq No (4B), Type (1B), Length (2B), Checksum (2B)
HEADER_FORMAT = '!IBHH'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_file(filename):
    seq_num = 0
    # Open file in binary read mode
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            
            # Type 0 = DATA packet
            header = struct.pack(HEADER_FORMAT, seq_num, 0, len(chunk), 0)
            packet = header + chunk
            
            client_socket.sendto(packet, (SERVER_IP, SERVER_PORT))
            print(f"Sent packet Seq: {seq_num}, Payload Size: {len(chunk)} bytes")
            seq_num += 1

    # Send FIN packet (Type 2) to indicate the end of the file
    fin_header = struct.pack(HEADER_FORMAT, seq_num, 2, 0, 0)
    client_socket.sendto(fin_header, (SERVER_IP, SERVER_PORT))
    print("Sent FIN packet. Transfer complete.")

if __name__ == "__main__":
    # Ensure you create a 'test.txt' file in your folder before running this
    send_file("test.txt")
    client_socket.close()
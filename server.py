import socket
import struct

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080
HEADER_FORMAT = '!IBHH'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT) # 9 bytes

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

print(f"RFTP Server listening on {SERVER_IP}:{SERVER_PORT}...")

def receive_file(output_filename):
    # Open file in binary write mode for reassembly
    with open(output_filename, 'wb') as f:
        while True:
            packet, addr = server_socket.recvfrom(1024 + HEADER_SIZE)
            
            # Extract the 9-byte header
            header = packet[:HEADER_SIZE]
            seq_num, packet_type, length, checksum = struct.unpack(HEADER_FORMAT, header)
            
            if packet_type == 2:
                print("Received FIN packet. File transfer complete.")
                break
                
            elif packet_type == 0:
                # Extract the payload and write it to the file
                data = packet[HEADER_SIZE:HEADER_SIZE+length]
                f.write(data)
                print(f"Received DATA packet Seq: {seq_num}, wrote {length} bytes.")

if __name__ == "__main__":
    receive_file("received_test.txt")
    server_socket.close()
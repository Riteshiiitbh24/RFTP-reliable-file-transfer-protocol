import socket
import struct
import random

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080
HEADER_FORMAT = '!IBHH'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
DROP_PROBABILITY = 0.3  # 30% artificial packet loss

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
print(f"Server listening with {DROP_PROBABILITY*100}% packet loss...")

def calculate_checksum(data):
    checksum = 0
    for byte in data:
        checksum = (checksum + byte) & 0xFFFF
    return checksum

def receive_file(output_filename):
    expected_seq = 0
    with open(output_filename, 'wb') as f:
        while True:
            packet, addr = server_socket.recvfrom(1024 + HEADER_SIZE)
            
            # Simulate network failure
            if random.random() < DROP_PROBABILITY:
                continue

            header = packet[:HEADER_SIZE]
            seq_num, packet_type, length, header_checksum = struct.unpack(HEADER_FORMAT, header)
            
            # Type 2 = FIN
            if packet_type == 2:
                server_socket.sendto(struct.pack(HEADER_FORMAT, seq_num, 1, 0, 0), addr)
                break
                
            # Type 0 = DATA
            elif packet_type == 0:
                data = packet[HEADER_SIZE:HEADER_SIZE+length]
                
                # Drop corrupted packets
                if calculate_checksum(data) != header_checksum:
                    continue
                
                # In-order arrival: Write to file and ACK this exact sequence
                if seq_num == expected_seq:
                    f.write(data)
                    server_socket.sendto(struct.pack(HEADER_FORMAT, expected_seq, 1, 0, 0), addr)
                    expected_seq += 1
                    
                # Out-of-order arrival: Send a cumulative ACK for the highest correct sequence so far
                else:
                    if expected_seq > 0:
                        server_socket.sendto(struct.pack(HEADER_FORMAT, expected_seq - 1, 1, 0, 0), addr)

if __name__ == "__main__":
    receive_file("received_inversion.jpeg")
    server_socket.close()
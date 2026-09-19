import socket
import struct
import random

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080
HEADER_FORMAT = '!IBHH'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
DROP_PROBABILITY = 0.3

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

print(f"RFTP Server listening on {SERVER_IP}:{SERVER_PORT}...")

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
            
            # Network simulation: random drop
            if random.random() < DROP_PROBABILITY:
                print("SIMULATED DROP: Packet lost!")
                continue

            header = packet[:HEADER_SIZE]
            seq_num, packet_type, length, header_checksum = struct.unpack(HEADER_FORMAT, header)
            
            if packet_type == 2:
                ack_header = struct.pack(HEADER_FORMAT, seq_num, 1, 0, 0)
                server_socket.sendto(ack_header, addr)
                print("FIN received. Transfer complete.")
                break
                
            elif packet_type == 0:
                data = packet[HEADER_SIZE:HEADER_SIZE+length]
                
                # Verify Data Integrity
                calculated_checksum = calculate_checksum(data)
                if calculated_checksum != header_checksum:
                    print(f"CORRUPTION DETECTED in Seq: {seq_num}! Dropping packet.")
                    continue # Drop packet without ACK to force a client timeout/resend
                
                if seq_num == expected_seq:
                    f.write(data)
                    expected_seq += 1
                
                ack_header = struct.pack(HEADER_FORMAT, seq_num, 1, 0, 0)
                server_socket.sendto(ack_header, addr)

if __name__ == "__main__":
    receive_file("received_inversion.jpeg")
    server_socket.close()
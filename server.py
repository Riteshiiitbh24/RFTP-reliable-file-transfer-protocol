import socket
import struct
import random

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080
HEADER_FORMAT = '!IBHH'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
DROP_PROBABILITY = 0.3  # 30% chance to drop a packet to simulate network loss

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

print(f"RFTP Server listening on {SERVER_IP}:{SERVER_PORT}...")
print(f"Network simulation active: {DROP_PROBABILITY * 100}% packet drop rate")

def receive_file(output_filename):
    expected_seq = 0
    with open(output_filename, 'wb') as f:
        while True:
            packet, addr = server_socket.recvfrom(1024 + HEADER_SIZE)
            
            # --- PHASE 4: SIMULATED PACKET LOSS ---
            if random.random() < DROP_PROBABILITY:
                print("SIMULATED DROP: Packet lost in transit!")
                continue  # Skips the rest of the loop. No ACK is sent.
            # --------------------------------------

            header = packet[:HEADER_SIZE]
            seq_num, packet_type, length, checksum = struct.unpack(HEADER_FORMAT, header)
            
            # Type 2 = FIN
            if packet_type == 2:
                ack_header = struct.pack(HEADER_FORMAT, seq_num, 1, 0, 0)
                server_socket.sendto(ack_header, addr)
                print("FIN received. Transfer complete.")
                break
                
            # Type 0 = DATA
            elif packet_type == 0:
                if seq_num == expected_seq:
                    data = packet[HEADER_SIZE:HEADER_SIZE+length]
                    f.write(data)
                    expected_seq += 1
                
                ack_header = struct.pack(HEADER_FORMAT, seq_num, 1, 0, 0)
                server_socket.sendto(ack_header, addr)

if __name__ == "__main__":
    receive_file("received_test.txt")
    server_socket.close()
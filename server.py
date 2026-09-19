import socket
import struct

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080
HEADER_FORMAT = '!IBHH'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

print(f"RFTP Server listening on {SERVER_IP}:{SERVER_PORT}...")

def receive_file(output_filename):
    expected_seq = 0
    with open(output_filename, 'wb') as f:
        while True:
            packet, addr = server_socket.recvfrom(1024 + HEADER_SIZE)
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
                # Only write to file if it's the exact packet we are waiting for
                if seq_num == expected_seq:
                    data = packet[HEADER_SIZE:HEADER_SIZE+length]
                    f.write(data)
                    expected_seq += 1
                
                # Send ACK (Type 1) back to the client
                ack_header = struct.pack(HEADER_FORMAT, seq_num, 1, 0, 0)
                server_socket.sendto(ack_header, addr)

if __name__ == "__main__":
    receive_file("received_test.txt")
    server_socket.close()
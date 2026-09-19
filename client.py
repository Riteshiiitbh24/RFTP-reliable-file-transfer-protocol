import socket
import struct

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080
CHUNK_SIZE = 1024
HEADER_FORMAT = '!IBHH'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
TIMEOUT = 0.5

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(TIMEOUT)

def calculate_checksum(data):
    """Calculates a simple 16-bit checksum of the data payload."""
    checksum = 0
    for byte in data:
        checksum = (checksum + byte) & 0xFFFF
    return checksum

def send_file(filename):
    seq_num = 0
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            
            # Calculate the real checksum for the data
            checksum_val = calculate_checksum(chunk)
            
            # Pack the header with the real checksum
            header = struct.pack(HEADER_FORMAT, seq_num, 0, len(chunk), checksum_val)
            packet = header + chunk
            
            while True:
                client_socket.sendto(packet, (SERVER_IP, SERVER_PORT))
                print(f"Sent DATA Seq: {seq_num} | Checksum: {checksum_val}")
                
                try:
                    ack_packet, _ = client_socket.recvfrom(HEADER_SIZE)
                    ack_seq, ack_type, _, _ = struct.unpack(HEADER_FORMAT, ack_packet)
                    
                    if ack_type == 1 and ack_seq == seq_num:
                        seq_num += 1
                        break
                except socket.timeout:
                    print(f"Timeout! Retransmitting Seq: {seq_num}...")

    fin_header = struct.pack(HEADER_FORMAT, seq_num, 2, 0, 0)
    while True:
        client_socket.sendto(fin_header, (SERVER_IP, SERVER_PORT))
        try:
            ack_packet, _ = client_socket.recvfrom(HEADER_SIZE)
            ack_seq, ack_type, _, _ = struct.unpack(HEADER_FORMAT, ack_packet)
            if ack_type == 1 and ack_seq == seq_num:
                print("Transfer complete.")
                break
        except socket.timeout:
            pass

if __name__ == "__main__":
    send_file("test.txt")
    client_socket.close()
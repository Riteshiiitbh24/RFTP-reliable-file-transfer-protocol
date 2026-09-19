import socket
import struct

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080
CHUNK_SIZE = 1024
HEADER_FORMAT = '!IBHH'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
TIMEOUT = 0.5  # Wait half a second for an ACK

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(TIMEOUT)  # Turn on the timer

def send_file(filename):
    seq_num = 0
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            
            # Type 0 = DATA
            header = struct.pack(HEADER_FORMAT, seq_num, 0, len(chunk), 0)
            packet = header + chunk
            
            # Stop-and-Wait Loop
            while True:
                client_socket.sendto(packet, (SERVER_IP, SERVER_PORT))
                print(f"Sent DATA packet Seq: {seq_num}")
                
                try:
                    # Wait for the server to reply
                    ack_packet, _ = client_socket.recvfrom(HEADER_SIZE)
                    ack_seq, ack_type, _, _ = struct.unpack(HEADER_FORMAT, ack_packet)
                    
                    # Type 1 = ACK. Check if it matches our sequence number.
                    if ack_type == 1 and ack_seq == seq_num:
                        print(f"Received ACK for Seq: {seq_num}")
                        seq_num += 1
                        break  # Break the wait loop, move to next chunk
                except socket.timeout:
                    print(f"Timeout! Retransmitting Seq: {seq_num}...")

    # Send FIN packet (Type 2)
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
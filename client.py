import socket
import struct
import os

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080
CHUNK_SIZE = 1024
HEADER_FORMAT = '!IBHH'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
TIMEOUT = 0.5

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(TIMEOUT)

def calculate_checksum(data):
    checksum = 0
    for byte in data:
        checksum = (checksum + byte) & 0xFFFF
    return checksum

def send_file(filename):
    seq_num = 0
    total_size = os.path.getsize(filename)
    bytes_sent = 0
    
    print(f"Starting transfer for '{filename}' ({total_size} bytes)...")
    
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            
            checksum_val = calculate_checksum(chunk)
            header = struct.pack(HEADER_FORMAT, seq_num, 0, len(chunk), checksum_val)
            packet = header + chunk
            
            while True:
                client_socket.sendto(packet, (SERVER_IP, SERVER_PORT))
                
                try:
                    ack_packet, _ = client_socket.recvfrom(HEADER_SIZE)
                    ack_seq, ack_type, _, _ = struct.unpack(HEADER_FORMAT, ack_packet)
                    
                    if ack_type == 1 and ack_seq == seq_num:
                        seq_num += 1
                        bytes_sent += len(chunk)
                        
                        # --- PROGRESS BAR LOGIC ---
                        percent = (bytes_sent / total_size) * 100
                        filled_length = int(40 * bytes_sent // total_size)
                        bar = '█' * filled_length + '-' * (40 - filled_length)
                        
                        # \r pushes the cursor to the beginning of the line to overwrite it
                        print(f"\rProgress: |{bar}| {percent:.1f}% ", end='', flush=True)
                        # --------------------------
                        
                        break
                except socket.timeout:
                    # Print timeout on a new line so it doesn't break the progress bar
                    print(f"\n[Warning] Timeout! Retransmitting Seq: {seq_num}...")

    fin_header = struct.pack(HEADER_FORMAT, seq_num, 2, 0, 0)
    while True:
        client_socket.sendto(fin_header, (SERVER_IP, SERVER_PORT))
        try:
            ack_packet, _ = client_socket.recvfrom(HEADER_SIZE)
            ack_seq, ack_type, _, _ = struct.unpack(HEADER_FORMAT, ack_packet)
            if ack_type == 1 and ack_seq == seq_num:
                print("\n\nTransfer completely verified and finished!")
                break
        except socket.timeout:
            pass

if __name__ == "__main__":
    send_file("inversion.jpeg")
    client_socket.close()
import socket
import struct
import os
import time

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080
CHUNK_SIZE = 1024
HEADER_FORMAT = '!IBHH'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
TIMEOUT = 0.5
WINDOW_SIZE = 5  # You can increase this to 20 later to test faster speeds

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(0.01)  # Fast timeout to constantly check for ACKs

def calculate_checksum(data):
    checksum = 0
    for byte in data:
        checksum = (checksum + byte) & 0xFFFF
    return checksum

def send_file(filename):
    with open(filename, 'rb') as f:
        file_data = f.read()

    chunks = [file_data[i:i+CHUNK_SIZE] for i in range(0, len(file_data), CHUNK_SIZE)]
    total_packets = len(chunks)
    
    base = 0      
    next_seq = 0  
    timer_start = 0
    
    print(f"Starting Go-Back-N transfer for '{filename}' (Window: {WINDOW_SIZE})...")
    
    # Start the stopwatch
    start_time = time.time()
    
    while base < total_packets:
        # Fill the window
        while next_seq < base + WINDOW_SIZE and next_seq < total_packets:
            chunk = chunks[next_seq]
            checksum_val = calculate_checksum(chunk)
            packet = struct.pack(HEADER_FORMAT, next_seq, 0, len(chunk), checksum_val) + chunk
            
            client_socket.sendto(packet, (SERVER_IP, SERVER_PORT))
            if base == next_seq:
                timer_start = time.time()  
            next_seq += 1

        # Check for ACKs
        try:
            while True:
                ack_packet, _ = client_socket.recvfrom(HEADER_SIZE)
                ack_seq, ack_type, _, _ = struct.unpack(HEADER_FORMAT, ack_packet)
                
                if ack_type == 1 and ack_seq >= base:
                    base = ack_seq + 1  # Slide the window
                    timer_start = time.time()
                    
                    percent = min((base / total_packets) * 100, 100)
                    filled = int(40 * base // total_packets)
                    bar = '█' * filled + '-' * (40 - filled)
                    print(f"\rProgress: |{bar}| {percent:.1f}% ", end='', flush=True)
        except socket.timeout:
            pass

        # Timeout: Go-Back-N
        if time.time() - timer_start > TIMEOUT:
            print(f"\n[Warning] Timeout! Go-Back-N resending from Seq: {base}...")
            next_seq = base  

    # Finish connection
    fin_header = struct.pack(HEADER_FORMAT, total_packets, 2, 0, 0)
    while True:
        client_socket.sendto(fin_header, (SERVER_IP, SERVER_PORT))
        try:
            ack_packet, _ = client_socket.recvfrom(HEADER_SIZE)
            if struct.unpack(HEADER_FORMAT, ack_packet)[1] == 1:
                
                # Stop the stopwatch and calculate speed
                end_time = time.time()
                duration = end_time - start_time
                speed_kb = (len(file_data) / 1024) / duration
                
                print(f"\n\nTransfer completely verified and finished in {duration:.2f} seconds!")
                print(f"Average Speed: {speed_kb:.2f} KB/s")
                break
        except socket.timeout:
            pass

if __name__ == "__main__":
    send_file("inversion.jpeg") 
    client_socket.close()
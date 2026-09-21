# packet.py
import struct

# Header Format: Sequence (4) | Type (1) | Length (2) | Checksum (2) | Window (2)
# Total: 11 bytes
HEADER_FORMAT = '!IBHHH'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

# Packet Types
TYPE_DATA = 0
TYPE_ACK = 1
TYPE_FIN = 2
TYPE_META = 3

def calculate_checksum(data):
    """Calculates a simple 16-bit checksum of the payload."""
    checksum = 0
    for byte in data:
        checksum = (checksum + byte) & 0xFFFF
    return checksum

def create_packet(seq_num, packet_type, data, window_size=0):
    """Packs the header and data into a binary UDP packet."""
    checksum_val = calculate_checksum(data) if data else 0
    header = struct.pack(HEADER_FORMAT, seq_num, packet_type, len(data), checksum_val, window_size)
    return header + data

def parse_packet(packet):
    """Unpacks a received UDP packet into its header fields and data payload."""
    if len(packet) < HEADER_SIZE:
        return None
        
    header = packet[:HEADER_SIZE]
    seq_num, packet_type, length, header_checksum, window_size = struct.unpack(HEADER_FORMAT, header)
    data = packet[HEADER_SIZE:HEADER_SIZE+length]
    
    return {
        'seq_num': seq_num,
        'type': packet_type,
        'length': length,
        'checksum': header_checksum,
        'window': window_size,
        'data': data
    }
# RFTP - Reliable File Transfer Protocol

A reliable file transfer system built on top of UDP using Python socket programming.

## Overview

RFTP is a client-server file transfer project that uses UDP for communication. Since UDP does not provide reliability by itself, this project builds reliability mechanisms on top of UDP: sequence numbers, checksums, cumulative ACKs, and Go-Back-N retransmission. The server also simulates artificial packet loss (30% by default) to exercise the reliability logic.

## Technologies Used

- Python
- Socket Programming
- UDP
- Computer Networks

## Usage

Start the server first, in one terminal:

```bash
python3 server.py
```

The server listens on `127.0.0.1:8080`, receives a single file transfer, saves it as `received_inversion.jpeg`, then exits.

Then, in a second terminal, send a file:

```bash
python3 client.py
```

The client sends `inversion.jpeg` (must exist in the same folder) to the server and exits once the transfer is confirmed complete.

> Note: the filenames on both sides are currently hardcoded in the `if __name__ == "__main__":` block of each script. To send/receive a different file, edit `send_file("inversion.jpeg")` in `client.py` and `receive_file("received_inversion.jpeg")` in `server.py`, then rerun.

The client prints a live progress bar, retransmits any window that times out, and reports the transfer duration and average speed once the server confirms completion.

## Project Structure

```
RFTP/
├── client.py
├── server.py
├── README.md
└── .gitignore
```

## Protocol Notes

- **Header format:** `!IBHH` — 4-byte sequence number, 1-byte packet type, 2-byte payload length, 2-byte checksum.
- **Packet types:** `0` = DATA, `1` = ACK, `2` = FIN.
- **Checksum:** sum of payload bytes, masked to 16 bits.
- **Reliability:** Go-Back-N ARQ with a sliding window (default size 5) and a 0.5s retransmission timeout.

## About

No description, website, or topics provided.
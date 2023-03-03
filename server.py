import socket
import time

UDP_IP = "127.0.0.1"  # IP address of the server
UDP_PORT = 5005      # Port number to listen on
MESSAGE_SIZE = 1024  # Size of the message buffer

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to a specific IP address and port
sock.bind((UDP_IP, UDP_PORT))

# Receive messages and measure the bitrate continuously
total_bytes = 0
start_time = time.time()
while True:
    data, addr = sock.recvfrom(MESSAGE_SIZE)
    total_bytes += len(data)
    duration = time.time() - start_time
    if duration > 0:
        bitrate = total_bytes / duration * 8
        print(f"Received {total_bytes} bytes in {duration:.2f} seconds.")
        print(f"Bitrate: {bitrate:.2f} bits per second.")

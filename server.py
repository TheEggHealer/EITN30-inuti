import socket
import time
import os

UDP_IP = "127.0.0.1"  # IP address of the server
UDP_PORT = 5005      # Port number to listen on
MESSAGE_SIZE = 1024  # Size of the message buffer

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to a specific IP address and port
sock.bind((UDP_IP, UDP_PORT))

# Receive messages and measure the bitrate, latency, and delay continuously
total_bytes = 0
start_time = time.time()
last_received_time = start_time
while True:
    data, addr = sock.recvfrom(MESSAGE_SIZE)
    total_bytes += len(data)
    duration = time.time() - start_time
    if duration > 0:
        bitrate = total_bytes / duration * 8
        latency = time.time() - last_received_time - INTERVAL
        delay = duration - total_bytes / bitrate
        last_received_time = time.time()

        os.system('clear')
        print(f"Received {total_bytes} bytes in {duration:.2f} seconds.")
        print(f"Bitrate: {bitrate:.2f} bits per second.")
        print(f"Latency: {latency:.2f} seconds.")
        print(f"Delay: {delay:.2f} seconds.")
import socket
import time
import os


UDP_IP = "192.168.69.2"  # IP address of the server
UDP_PORT = 5005      # Port number to send to
MESSAGE_SIZE = 2200  # Size of the message buffer
INTERVAL = 0.1      # Delay between messages in seconds

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send messages continuously with a small delay between each message
total_bytes = 0
start_time = time.time()
last_sent_time = start_time
message = b"x" * MESSAGE_SIZE
while True:
    sock.sendto(message, (UDP_IP, UDP_PORT))
    total_bytes += len(message)
    duration = time.time() - start_time
    if duration > 0:
        bitrate = total_bytes / duration * 8
        latency = time.time() - last_sent_time - INTERVAL
        delay = duration - total_bytes / bitrate
        last_sent_time = time.time()
        os.system('clear')
        print(f"Sent {total_bytes} bytes in {duration:.2f} seconds.")
        print(f"Bitrate: {bitrate:.2f} bits per second.")
        print(f"Latency: {latency:.2f} seconds.")
        print(f"Delay: {delay:.2f} seconds.")
    time.sleep(INTERVAL)

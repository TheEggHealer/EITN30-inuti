import socket
import time

UDP_IP = "127.0.0.1"  # IP address of the server
UDP_PORT = 5005      # Port number to send to
MESSAGE_SIZE = 1024  # Size of the message buffer
INTERVAL = 0.01      # Delay between messages in seconds

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send messages continuously with a small delay between each message
message = b"x" * MESSAGE_SIZE
while True:
    sock.sendto(message, (UDP_IP, UDP_PORT))
    time.sleep(INTERVAL)

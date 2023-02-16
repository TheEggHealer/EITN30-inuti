import struct
from circuitpython_nrf24l01.rf24 import RF24
from tuntap import TunTap

def rx_thread(rx: RF24, tun: TunTap):

	segments = [b''] * 256

	while True:
			
		if rx.available():
			buffer = rx.read()
			
			if (buffer == bytes(0b1001)): 
				# Entire ip package received
				packet = b''.join(segments)
				tun.write(packet)
				packet = [b''] * 256
			else:
				segment_idx = struct.unpack('>B', buffer[0])
				segment = buffer[1:]
				segments[segment_idx] = segment
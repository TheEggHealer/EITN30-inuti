import struct
from circuitpython_nrf24l01.rf24 import RF24
from tuntap import TunTap

def rx_thread(rx: RF24, interface: TunTap):

	segments = [b''] * 256

	while True:
			
		if rx.available():
			buffer = rx.read()

			if (buffer == bytes(0b1001)): 
				# Entire ip package received
				packet = b''.join(segments)
				interface.write(packet)
				print('Wrote to tun')
				packet = [b''] * 256
			else:
				segment = buffer[1:]
				segments[buffer[0]] = segment
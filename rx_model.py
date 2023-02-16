import struct
from circuitpython_nrf24l01.rf24 import RF24
import threading
from tuntap import TunTap

def rx_thread(event: threading.Event, rx: RF24, interface: TunTap):

    segments = [b''] * 256

    while True:
        if event.is_set:
            break

        if rx.available():
            buffer = rx.read()
            
            if (buffer == bytes(0b1001)): 
                # Entire ip package received
                packet = b''.join(segments)
                interface.write(packet)
                packet = [b''] * 256
            else:
                segment_idx = struct.unpack('>B', buffer[0])
                segment = buffer[1:]
                segments[segment_idx] = segment

            
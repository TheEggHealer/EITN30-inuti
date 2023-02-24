import struct
from circuitpython_nrf24l01.rf24 import RF24
from tuntap import TunTap

def rx_thread(rx: RF24, interface: TunTap, buffer_monitor):

  segments = [b''] * 2185

  while True:
      
    if rx.available():
      buffer = rx.read()

      if (buffer == bytes(0b1001)): 
        # Entire ip package received
        packet = b''.join(segments)
        interface.write(packet)
        segments = [b''] * 2185
        buffer_monitor.update_stats(rec_ip=1)
      else:
        segment = buffer[2:]
        identifier = int(struct.unpack('<H', buffer[:2])[0])
        segments[identifier] = segment
        buffer_monitor.update_stats(rec=1, rec_bytes=len(segment))
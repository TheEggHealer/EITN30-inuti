import struct
from circuitpython_nrf24l01.rf24 import RF24
from tuntap import TunTap

def rx_thread(rx: RF24, interface: TunTap, buffer_monitor):

  segments = [b''] * 256

  while True:
      
    if rx.available():
      buffer = rx.read()
      buffer_monitor.set_splitting(True)

      if (buffer == bytes(0b1001)): 
        # Entire ip package received
        packet = b''.join(segments)
        interface.write(packet)
        packet = [b''] * 256
        buffer_monitor.update_stats(rec_ip=1)
        buffer_monitor.set_splitting(False)
      else:
        segment = buffer[2:]
        indentifier = struct.unpack('<H', buffer[:2])
        segments[indentifier] = segment
        buffer_monitor.update_stats(rec=1, rec_bytes=len(segment))
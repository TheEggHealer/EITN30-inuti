from buffer_monitor import BufferMonitor
import struct
from circuitpython_nrf24l01.rf24 import RF24
from tuntap import TunTap
from multiprocessing import Value

def tx_thread(tx: RF24, buffer_monitor: Value):
  while True:
    # Wait for packet to send
    packet = buffer_monitor.value.pop(1)
    if packet == None: continue
    
    segments = split(packet)
    for segment in segments:
      respons = tx.send(segment)
      print(respons)

def interface_reader_thread(tun: TunTap, buffer_monitor: Value):
  while True:
    packet = tun.read()
    buffer_monitor.value.put(packet)

def split(packet):
  identifier = 0
  segments = []

  for i in range(int(len(packet) / 31)):
    identifier = struct.pack('<B', i)
    segments.append(identifier + packet[i*31 : (i+1)*31])
  
  if len(packet) % 31 != 0:
    identifier = struct.pack('<B', len(segments))
    segments.append(identifier + packet[len(segments)*31:])
  
  segments.append(bytes(0b1001))


  return segments

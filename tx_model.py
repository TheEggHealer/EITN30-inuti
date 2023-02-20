import struct
from circuitpython_nrf24l01.rf24 import RF24
from tuntap import TunTap


def tx_thread(tx: RF24, buffer_monitor):
  while True:
    # Wait for packet to send
    packet = buffer_monitor.pop(1)
    if packet == None: continue
    
    segments = split(packet)
    for segment in segments:
      respons = tx.send(segment, ask_no_ack=True)
      buffer_monitor.inc(sent=1, sent_bytes=len(segment), fail=0 if respons else 1)
    buffer_monitor.inc(sent_ip=1)

def interface_reader_thread(tun: TunTap, buffer_monitor):
  inititalized = False

  while True:
    packet = tun.read()
    if inititalized:
      buffer_monitor.put(packet)
    else:
      inititalized = True

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

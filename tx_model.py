import struct
from circuitpython_nrf24l01.rf24 import RF24
from tuntap import TunTap


def tx_thread(tx: RF24, buffer_monitor):
  while True:
    # Wait for packet to send
    packet = buffer_monitor.pop(1, queue_type='fifo')
    if packet == None: continue
    
    buffer_monitor.set_sending(True)
    segments = split(packet)
    for segment in segments:

      respons = tx.send(segment, ask_no_ack=False, force_retry=1000)
      
      buffer_monitor.update_bitrate(direction='up', byte_count=len(segment))
      buffer_monitor.update_stats(sent=1, sent_bytes=len(segment), fail=0 if respons else 1)

    # Removing one sent package (END OF IP-PACKET)
    buffer_monitor.set_sending(False)
    buffer_monitor.update_stats(sent=-1, sent_ip=1)

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
  
  # 2 Byte
  # for i in range(int(len(packet) / 30)):
  #   identifier = struct.pack('<H', i)
  #   segments.append(identifier + packet[i*30 : (i+1)*30])
  
  # if len(packet) % 30 != 0:
  #   identifier = struct.pack('<H', len(segments))
  #   segments.append(identifier + packet[len(segments)*30:])
  
  for i in range(int(len(packet) / 31)):
    identifier = struct.pack('<B', i)
    segments.append(identifier + packet[i*31 : (i+1)*31])
  
  if len(packet) % 31 != 0:
    identifier = struct.pack('<B', len(segments))
    segments.append(identifier + packet[len(segments)*31:])
  
  segments.append(bytes(0b1001))


  return segments

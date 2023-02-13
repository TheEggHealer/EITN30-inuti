import threading

class BufferMonitor:

  def __init__(self):
    self.lock = threading.Lock()

    self.packet_buffer = []
  
  def put(self, packet):
    self.lock.acquire()
    self.packet.append(packet)
    self.lock.release()
  
  def pop(self):
    self.lock.acquire()
    packet = self.buffer[0]
    self.buffer = self.buffer[1:]
    self.lock.release()
    return packet
  
  
  
  

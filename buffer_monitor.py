import multiprocessing
from multiprocessing import Lock
from multiprocessing import Condition

class BufferMonitor:

  def __init__(self):
    self.lock = Lock()
    self.condition = Condition(self.lock)
    self.count_sent = 0
    self.count_rec = 0

    self.packet_buffer = []
  
  def put(self, packet):
    self.lock.acquire()
    self.packet_buffer.append(packet)
    self.condition.notify_all()
    self.lock.release()
  
  def size(self):
    self.lock.acquire()
    size = len(self.packet_buffer)
    self.lock.release()
    return size
  
  def status(self):
    return self.lock.locked()

  def pop(self, timeout):
    self.lock.acquire()

    if len(self.packet_buffer) == 0:
      self.condition.wait(timeout)
    
    if len(self.packet_buffer) == 0:
      self.lock.release()
      return None

    packet = self.packet_buffer[0]
    self.packet_buffer = self.packet_buffer[1:]
    self.lock.release()
    return packet

  def add_sent(self):
    self.lock.acquire()
    self.count_sent += 1
    self.lock.release()

  def add_rec(self):
    self.lock.acquire()
    self.count_rec += 1
    self.lock.release()

  def get_sent(self):
    self.lock.acquire()
    sent = self.count_sent
    self.lock.release()
    return sent

  def get_rec(self):
    self.lock.acquire()
    rec = self.count_rec
    self.lock.release()
    return rec
  
  
  
  

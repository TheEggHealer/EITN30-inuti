import multiprocessing
from multiprocessing import Lock
from multiprocessing import Condition

class BufferMonitor:

  def __init__(self):
    self.lock = Lock()
    self.condition = Condition(self.lock)
    self.count_sent = 0
    self.count_rec = 0
    self.count_sent_ip = 0
    self.count_rec_ip = 0
    self.count_sent_bytes = 0
    self.count_rec_bytes = 0
    self.count_fail = 0
    self.splitting = False

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

  def update_stats(self, sent=0, rec=0, sent_ip=0, rec_ip=0, sent_bytes=0, rec_bytes=0, fail=0):
    self.lock.acquire()
    self.count_sent += sent
    self.count_rec += rec
    self.count_sent_ip += sent_ip
    self.count_rec_ip += rec_ip
    self.count_sent_bytes += sent_bytes
    self.count_rec_bytes += rec_bytes
    self.count_fail += fail
    self.lock.release()

  def set_splitting(self, splitting):
    self.lock.acquire()
    self.splitting = splitting
    self.lock.release()

  def get_splitting(self):
    self.lock.acquire()
    splitting = self.splitting
    self.lock.release()
    return splitting

  def get_stats(self):
    self.lock.acquire()
    sent = self.count_sent
    rec = self.count_rec
    sent_ip = self.count_sent_ip
    rec_ip = self.count_rec_ip
    sent_bytes = self.count_sent_bytes
    rec_bytes = self.count_rec_bytes
    fail = self.count_fail
    self.lock.release()
    return sent, rec, sent_ip, rec_ip, sent_bytes, rec_bytes, fail
  
  def clear_stats(self):
    self.lock.acquire()
    self.count_sent = 0
    self.count_rec = 0
    self.count_sent_ip = 0
    self.count_rec_ip = 0
    self.count_sent_bytes = 0
    self.count_rec_bytes = 0
    self.count_fail = 0
    self.lock.release()
  
  

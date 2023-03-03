import multiprocessing
from multiprocessing import Lock
from multiprocessing import Condition
from datetime import datetime

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
    self.sending = False
    self.largest_packet = 0

    self.bitrate_up = 0
    self.bitrate_down = 0
    self.bitrate_up_list = []
    self.bitrate_down_list = []

    self.packet_buffer = []
  
  def put(self, packet):
    self.lock.acquire()
    if len(packet) > self.largest_packet: self.largest_packet = len(packet)
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

  def pop(self, timeout, queue_type='fifo'):
    self.lock.acquire()

    if len(self.packet_buffer) == 0:
      self.condition.wait(timeout)
    
    if len(self.packet_buffer) == 0:
      self.lock.release()
      return None

    if queue_type == 'fifo':
      # FIFO
      packet = self.packet_buffer[0]
      self.packet_buffer = self.packet_buffer[1:]
    else:
      #LIFO
      packet = self.packet_buffer[-1]
      self.packet_buffer = self.packet_buffer[:-1]

    self.lock.release()
    return packet

  def update_bitrate(self, direction, byte_count):
    timestamp = datetime.now()
    if direction == 'up':
      self.bitrate_up_list.append((timestamp, byte_count * 8))
    

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

  def set_sending(self, sending):
    self.lock.acquire()
    self.sending = sending
    self.lock.release()

  def get_sending(self):
    self.lock.acquire()
    sending = self.sending
    self.lock.release()
    return sending

  def get_stats(self):
    self.lock.acquire()
    timestamp = datetime.now()
    self.bitrate_up_list = [item for item in self.bitrate_up_list if (timestamp - item[0]).seconds <= 10]
    bitrate_up = sum([item[1] for item in self.bitrate_up_list]) / 10


    sent = self.count_sent
    rec = self.count_rec
    sent_ip = self.count_sent_ip
    rec_ip = self.count_rec_ip
    sent_bytes = self.count_sent_bytes
    rec_bytes = self.count_rec_bytes
    fail = self.count_fail
    largest_packet = self.largest_packet
    self.lock.release()
    return sent, rec, sent_ip, rec_ip, sent_bytes, rec_bytes, fail, largest_packet, bitrate_up
  
  def clear_stats(self):
    self.lock.acquire()
    self.count_sent = 0
    self.count_rec = 0
    self.count_sent_ip = 0
    self.count_rec_ip = 0
    self.count_sent_bytes = 0
    self.count_rec_bytes = 0
    self.count_fail = 0
    self.largest_packet = 0
    self.lock.release()
  
  def clear_queue(self):
    self.lock.acquire()
    self.packet_buffer = []
    self.lock.release()
  
  

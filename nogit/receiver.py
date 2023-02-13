import spidev
import time
import struct
import board
from digitalio import DigitalInOut
from circuitpython_nrf24l01.rf24 import RF24

class Receiver:
  RUNNING = True

  def run(self):

    try:
      while self.RUNNING:
        response = input('\nWhat would you like to do?\n> ')
        self.parse(response)
    except:
      print('Something went wrong, closing safely')
      self.nrf.power = False

    self.nrf.power = False
    print('Program has finished.')

  def parse(self, command):
    command = command.lower().strip()
    args = command.split()
    command = args[0]
    args = args[1:]

    if command in self.command_quit_in:
      return self.command_quit()
    elif command in self.command_sum_in:
      return self.command_sum(args)
    elif command in self.command_setup_in:
      return self.command_setup(args)
    elif command in self.command_listen_in:
      return self.command_listen(args)
    else:
      return self.command_not_found()


  ############################################## COMMANDS

  command_listen_in = ['listen']
  def command_listen(self, args):
    if args[0] == 'on':
      print('Listening...')
      self.nrf.listen = True
      while True:
        if self.nrf.available():
          payload_size = self.nrf.any()
          
          buffer = self.nrf.read() 
          print(f"Received {payload_size} bytes: {str(buffer)}")

  command_setup_in = ['setup']
  def command_setup(self, args):
    other_address = bytes(args[0], encoding='utf-8')

    self.address = b'1Node'
    self.SPI_BUS = spidev.SpiDev()  # for a faster interface on linux
    self.CSN_PIN = 10  # use CE0 on default bus (even faster than using any pin)
    self.CE_PIN = DigitalInOut(board.D27)  # using pin gpio22 (BCM numbering)
    self.nrf = RF24(self.SPI_BUS, self.CSN_PIN, self.CE_PIN)
    self.nrf.pa_level = -18

    self.nrf.open_tx_pipe(b'2Node')
    self.nrf.open_rx_pipe(1, self.address) 

  command_quit_in = ['q', 'quit', 'exit', 'stop']
  def command_quit(self):
    self.RUNNING = False
    print('Quitting...')
    return True

  command_sum_in = ['sum']
  def command_sum(self, args):
    args = [int(x) for x in args]
    print(f'Sum is {sum(args)}')
    return False

  def command_not_found(self): 
    print('Please enter another command.')
    return False

r = Receiver()
r.run()
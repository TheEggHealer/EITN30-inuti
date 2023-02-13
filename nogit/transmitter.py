import time
import struct
import board
from digitalio import DigitalInOut
from digitalio import Pin
from circuitpython_nrf24l01.rf24 import RF24
import spidev

class Transmitter:

  def __init__(self, radio):
    self.radio = radio

    self.SPI_BUS = spidev.SpiDev() 
    self.CSN_PIN = 10 if radio else 0
    self.CE_PIN = DigitalInOut(board.D27) if radio else DigitalInOut(board.D17) 
    
    self.nrf = RF24(self.SPI_BUS, self.CSN_PIN, self.CE_PIN)
    self.nrf.pa_level = -12
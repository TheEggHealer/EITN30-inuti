from tuntap import TunTap, Packet
import sys, os, time, subprocess
import spidev
import board
from digitalio import DigitalInOut
from circuitpython_nrf24l01.rf24 import RF24
from tx_model import tx_thread, interface_reader_thread
from rx_model import rx_thread
import multiprocessing
from buffer_monitor import BufferMonitor

BASE_ADDR = b'1Node'
MOBILE_ADDR = b'2Node'

def OpenTunnel( device_name,   ip ,  net_mask):
    try:
        tun = TunTap(nic_type="Tun",nic_name= device_name )
        tun.config(ip = ip,mask=net_mask )
        os.system(f'sudo ifconfig {device_name} mtu 576')
    except KeyboardInterrupt:
        print('Interface is busy')
        sys.exit(0)
    
    return tun

def start():
  i = 5
  while i > 0:
      bytes = tun.read()
      print(len(bytes))
      source = bytes[12:16]
      dest = bytes[16:20]
      icmp_type = bytes[20]
      print(f"Source: {int(source[0])}.{int(source[1])}.{int(source[2])}.{int(source[3])}") 
      print(f"Destination: {int(dest[0])}.{int(dest[1])}.{int(dest[2])}.{int(dest[3])}") 
      print(f"icmp type: {int(icmp_type)}")
      i -= 1
      time.sleep(1)

  tun.close()

def setup_base(interface):
  print('Setup starting')
  # Setup forwarding and masquerading
  subprocess.check_call(f'sudo iptables -t nat -A POSTROUTING -o {interface} -j MASQUERADE', shell=True)
  subprocess.check_call(f'sudo iptables -A FORWARD -i eth0 -o {interface} -m state --state RELATED,ESTABLISHED -j ACCEPT', shell=True)
  subprocess.check_call(f'sudo iptables -A FORWARD -i {interface} -o eth0 -j ACCEPT', shell=True)

  # Setup radio
  RX_SPI_BUS = spidev.SpiDev()
  RX_CSN_PIN = 10
  RX_CE_PIN = DigitalInOut(board.D27)
  rx = RF24(RX_SPI_BUS, RX_CSN_PIN, RX_CE_PIN)
  rx.pa_level = 0
  rx.open_tx_pipe(BASE_ADDR)
  rx.open_rx_pipe(1, MOBILE_ADDR) 
  rx.listen = True

  TX_SPI_BUS = spidev.SpiDev()
  TX_CSN_PIN = 0
  TX_CE_PIN = DigitalInOut(board.D17)
  tx = RF24(TX_SPI_BUS, TX_CSN_PIN, TX_CE_PIN)
  tx.pa_level = 0
  tx.open_tx_pipe(BASE_ADDR)
  tx.open_rx_pipe(1, MOBILE_ADDR)
  tx.listen = False
  print('Setup done')
  return rx, tx

def setup_mobile(interface):
  print('Setup starting')

  # subprocess.check_call(f'sudo ip route add default via 192.168.69.1 dev {interface}', shell=True)

  # Setup radio
  RX_SPI_BUS = spidev.SpiDev()
  RX_CSN_PIN = 10
  RX_CE_PIN = DigitalInOut(board.D27)
  rx = RF24(RX_SPI_BUS, RX_CSN_PIN, RX_CE_PIN)
  rx.pa_level = 0
  rx.open_tx_pipe(MOBILE_ADDR)
  rx.open_rx_pipe(1, BASE_ADDR) 
  rx.listen = True

  TX_SPI_BUS = spidev.SpiDev()
  TX_CSN_PIN = 0
  TX_CE_PIN = DigitalInOut(board.D17)
  tx = RF24(TX_SPI_BUS, TX_CSN_PIN, TX_CE_PIN)
  tx.pa_level = 0
  tx.open_tx_pipe(MOBILE_ADDR)
  tx.open_rx_pipe(1, BASE_ADDR)
  tx.listen = False
  print('Setup done')
  return rx, tx

def teardown_base(interface, rx, tx):
  subprocess.check_call(f'sudo iptables -t nat -D POSTROUTING -o {interface} -j MASQUERADE', shell=True)
  subprocess.check_call(f'sudo iptables -D FORWARD -i eth0 -o {interface} -m state --state RELATED,ESTABLISHED -j ACCEPT', shell=True)
  subprocess.check_call(f'sudo iptables -D FORWARD -i {interface} -o eth0 -j ACCEPT', shell=True)

  rx.power = False
  tx.power = False
  rx.listen = False
  print('Teardown done')

def teardown_mobile(interface, rx, tx):
  # subprocess.check_call(f'sudo ip route add default via 192.168.10.1 dev eth0', shell=True)

  rx.power = False
  tx.power = False
  rx.listen = False
  print('Teardown done')

if __name__ == "__main__":
  device = int(input('Base (0) or Mobile (1) > '))
  interface_name = 'longge'

  buffer_monitor = BufferMonitor()
  # buffer_monitor.put('Test message 1'.encode(encoding='utf-8'))
  # buffer_monitor.put('Test message 2'.encode(encoding='utf-8'))
  # buffer_monitor.put('Test message 3'.encode(encoding='utf-8'))
  # buffer_monitor.put('Test message 4'.encode(encoding='utf-8'))
  # buffer_monitor.put('Test message 5'.encode(encoding='utf-8'))
  # buffer_monitor.put('Test message 6'.encode(encoding='utf-8'))

  if device == 0:
    tunnel_ip = '192.168.69.1'
    mask = '255.255.255.0'
    tun = OpenTunnel(interface_name, tunnel_ip, mask)
    rx, tx = setup_base(interface_name)

    tx_thread = multiprocessing.Process(target=tx_thread, args=(tx, buffer_monitor))
    tx_thread.start()

    rx_thread = multiprocessing.Process(target=rx_thread, args=(rx, tun))
    rx_thread.start()

    interface_reader_thread = multiprocessing.Process(target=interface_reader_thread, args=(tun, buffer_monitor))
    interface_reader_thread.start()

    while True:
      c = input('Enter command: ')

      if c == 'exit':
        tx_thread.terminate()
        rx_thread.terminate()
        interface_reader_thread.terminate()
        break
    
    teardown_base(interface_name, rx, tx)
    tun.close()
  else:
    tunnel_ip = '192.168.69.2'
    mask = '255.255.255.0'
    tun = OpenTunnel(interface_name, tunnel_ip, mask)
    rx, tx = setup_mobile(interface_name)
    
    tx_thread = multiprocessing.Process(target=tx_thread, args=(tx, buffer_monitor))
    tx_thread.start()

    rx_thread = multiprocessing.Process(target=rx_thread, args=(rx, tun))
    rx_thread.start()

    interface_reader_thread = multiprocessing.Process(target=interface_reader_thread, args=(tun, buffer_monitor))
    interface_reader_thread.start()

    while True:
      c = input('Enter command: ')

      if c == 'exit':
        tx_thread.terminate()
        rx_thread.terminate()
        interface_reader_thread.terminate()
        break

    teardown_mobile(interface_name, rx, tx)
    tun.close()
from tuntap import TunTap, Packet
import sys, os, time, subprocess
import spidev
import board
from digitalio import DigitalInOut
from circuitpython_nrf24l01.rf24 import RF24
from tx_model import tx_thread, interface_reader_thread
from rx_model import rx_thread
import multiprocessing
from multiprocessing.managers import BaseManager
from buffer_monitor import BufferMonitor

BASE_ADDR = b'1Node'
MOBILE_ADDR = b'2Node'

def OpenTunnel( device_name,   ip ,  net_mask):
    try:
        tun = TunTap(nic_type="Tun",nic_name= device_name )
        tun.config(ip = ip,mask=net_mask )
        os.system(f'sudo ifconfig {device_name} mtu 7936')
    except KeyboardInterrupt:
        print('Interface is busy')
        sys.exit(0)
    
    return tun

def setup_base(interface):
  print('Setup starting')
  # Setup forwarding and masquerading
  subprocess.check_call(f'sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE', shell=True)
  subprocess.check_call(f'sudo iptables -A FORWARD -i eth0 -o {interface} -m state --state RELATED,ESTABLISHED -j TCPMSS --set-mss 7896 -p tcp --tcp-flags SYN,RST SYN -m tcpmss --mss 7896:7926 ', shell=True)
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

  subprocess.check_call(f'sudo ip route add 192.168.10.162 dev eth0', shell=True)
  subprocess.check_call(f'sudo ip route del 192.168.10.0/24 dev eth0', shell=True)
  subprocess.check_call(f'sudo ip route del default via 192.168.10.1', shell=True)
  subprocess.check_call(f'sudo ip route add default via 192.168.69.1', shell=True)

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
  subprocess.check_call(f'sudo iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE', shell=True)
  subprocess.check_call(f'sudo iptables -D FORWARD -i eth0 -o {interface} -m state --state RELATED,ESTABLISHED -j TCPMSS --set-mss 7896 -p tcp --tcp-flags SYN,RST SYN -m tcpmss --mss 7896:7926 ', shell=True)
  # subprocess.check_call(f'sudo iptables -D FORWARD -i eth0 -o {interface} -m state --state RELATED,ESTABLISHED -j ACCEPT', shell=True)
  subprocess.check_call(f'sudo iptables -D FORWARD -i {interface} -o eth0 -j ACCEPT', shell=True)

  rx.power = False
  tx.power = False
  rx.listen = False
  print('Teardown done')

def teardown_mobile(interface, rx, tx):
  subprocess.check_call(f'sudo ip route add 192.168.10.0/24 dev eth0', shell=True)
  subprocess.check_call(f'sudo ip route del 192.168.10.162 dev eth0', shell=True)
  subprocess.check_call(f'sudo ip route del default via 192.168.69.1', shell=True)
  subprocess.check_call(f'sudo ip route add default via 192.168.10.1', shell=True)

  rx.power = False
  tx.power = False
  rx.listen = False
  print('Teardown done')

def show_title():
	os.system('clear')
	# print('\u001b[0;0H')
	print("*********************************************")
	print("***               SnakeData               ***")
	print("*** - Get your data where your snake is - ***")
	print("*********************************************")

def print_screen(status):
	DOUBLE_LEFT_TOP = u'\u2554'
	DOUBLE_VERTI_PIPE = u'\u2551'
	DOUBLE_LEFT_BOTTOM = u'\u255a'
	DOUBLE_RIGHT_TOP = u'\u2557'
	DOUBLE_RIGHT_BOTTOM = u'\u255d'
	DOUBLE_HORIZ_PIPE = u'\u2550'
	SINGLE_LEFT_TOP = u'\u250c'
	SINGLE_VERTI_PIPE = u'\u2502'
	SINGLE_LEFT_BOTTOM = u'\u2514'
	SINGLE_RIGHT_TOP = u'\u2510'
	SINGLE_RIGHT_BOTTOM = u'\u2518'
	SINGLE_HORIZ_PIPE = u'\u2500'

	line = SINGLE_HORIZ_PIPE * 29

	print('\n')
	print(SINGLE_LEFT_TOP + SINGLE_HORIZ_PIPE * 44)

	print(SINGLE_VERTI_PIPE + ' \u001b[7mSTATUS:\u001b[0m (Press enter to update)')
	for title, value in status.items():
		print(SINGLE_VERTI_PIPE + f' * {title}:\t{value}')

	print(SINGLE_LEFT_BOTTOM + SINGLE_HORIZ_PIPE * 44)
	print('\n')

if __name__ == "__main__":
  device = int(input('Base (0) or Mobile (1) > '))
  interface_name = 'longge'

  BaseManager.register('BufferMonitor', BufferMonitor)
  manager = BaseManager()
  manager.start()
  buffer_monitor = manager.BufferMonitor()

  if device == 0:
    tunnel_ip = '192.168.69.1'
    mask = '255.255.255.0'
    tun = OpenTunnel(interface_name, tunnel_ip, mask)
    rx, tx = setup_base(interface_name)

    tx_thread = multiprocessing.Process(target=tx_thread, args=(tx, buffer_monitor))
    tx_thread.start()

    rx_thread = multiprocessing.Process(target=rx_thread, args=(rx, tun, buffer_monitor))
    rx_thread.start()

    interface_reader_thread = multiprocessing.Process(target=interface_reader_thread, args=(tun, buffer_monitor))
    interface_reader_thread.start()

    while True:
      show_title()
      sent, received, sent_ip, received_ip, sent_bytes, received_bytes, fails = buffer_monitor.get_stats()
      print_screen({
				'sent': f'{sent} ({sent_ip} ip, {sent_bytes} bytes)',
				'received': f'{received} ({received_ip} ip, {received_bytes} bytes)',
        'failed': f'{fails}',
			})

      c = input('Enter command: ')

      if c == 'exit':
        tx_thread.terminate()
        rx_thread.terminate()
        interface_reader_thread.terminate()
        break
      elif c == 'clear':
        buffer_monitor.clear_stats()
    
    teardown_base(interface_name, rx, tx)
    tun.close()
  else:
    tunnel_ip = '192.168.69.2'
    mask = '255.255.255.0'
    tun = OpenTunnel(interface_name, tunnel_ip, mask)
    rx, tx = setup_mobile(interface_name)
    
    tx_thread = multiprocessing.Process(target=tx_thread, args=(tx, buffer_monitor))
    tx_thread.start()

    rx_thread = multiprocessing.Process(target=rx_thread, args=(rx, tun, buffer_monitor))
    rx_thread.start()

    interface_reader_thread = multiprocessing.Process(target=interface_reader_thread, args=(tun, buffer_monitor))
    interface_reader_thread.start()

    while True:
      show_title()
      sent, received, sent_ip, received_ip, sent_bytes, received_bytes, fails = buffer_monitor.get_stats()
      print_screen({
				'sent': f'{sent} ({sent_ip} ip, {sent_bytes} bytes)',
				'received': f'{received} ({received_ip} ip, {received_bytes} bytes)',
        'failed': f'{fails}',
			})

      c = input('Enter command: ')

      if c == 'exit':
        tx_thread.terminate()
        rx_thread.terminate()
        interface_reader_thread.terminate()
        break
      elif c == 'clear':
        buffer_monitor.clear_stats()

    teardown_mobile(interface_name, rx, tx)
    tun.close()
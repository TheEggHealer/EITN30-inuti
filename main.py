from tuntap import TunTap, Packet
import sys, os, time, subprocess
import spidev
import board
from digitalio import DigitalInOut
from circuitpython_nrf24l01.rf24 import RF24
import tx_model
import rx_model
import multiprocessing
from multiprocessing.managers import BaseManager
from buffer_monitor import BufferMonitor

BASE_ADDR = b'1Node'
MOBILE_ADDR = b'2Node'
BASE_2_ADDR = b'3Node'
MOBILE_2_ADDR = b'4Node'

def OpenTunnel(interface_name, ip, net_mask):
    try:
        tun = TunTap(nic_type="Tun",nic_name=interface_name)
        tun.config(ip=ip, mask=net_mask)
        # os.system(f'sudo ifconfig {interface_name} mtu 7936')
    except KeyboardInterrupt:
        print('Interface is busy')
        sys.exit(0)
    
    return tun

def setup_radio(tra_addr, rec_addr, csn_pin, ce_pin, listening):
  RX_SPI_BUS = spidev.SpiDev()
  radio = RF24(RX_SPI_BUS, csn_pin, ce_pin)
  radio.pa_level = 0
  radio.open_tx_pipe(tra_addr)
  radio.open_rx_pipe(1, rec_addr) 
  radio.listen = listening
  return radio

def setup_base(interface_name):
  print('Setup starting')
  # Setup forwarding and masquerading
  subprocess.check_call(f'sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE', shell=True)
  # subprocess.check_call(f'sudo iptables -A FORWARD -i eth0 -o {interface_name} -m state --state RELATED,ESTABLISHED -j TCPMSS --set-mss 7896 -p tcp --tcp-flags SYN,RST SYN -m tcpmss --mss 7896:7926 ', shell=True)
  subprocess.check_call(f'sudo iptables -A FORWARD -i eth0 -o {interface_name} -m state --state RELATED,ESTABLISHED -j ACCEPT', shell=True)
  subprocess.check_call(f'sudo iptables -A FORWARD -i {interface_name} -o eth0 -j ACCEPT', shell=True)

  # Setup radio
  rx = setup_radio(BASE_ADDR, MOBILE_ADDR, 10, DigitalInOut(board.D27), True)
  tx = setup_radio(BASE_2_ADDR, MOBILE_2_ADDR, 0, DigitalInOut(board.D17), False)

  print('Setup done')
  return rx, tx

def teardown_radios(rx, tx):
  rx.power = False
  tx.power = False
  rx.listen = False

def setup_mobile(interface):
  print('Setup starting')
  # Setup forwarding and masquerading
  subprocess.check_call(f'sudo ip route add 192.168.10.163 dev eth0', shell=True)
  subprocess.check_call(f'sudo ip route del 192.168.10.0/24 dev eth0', shell=True)
  subprocess.check_call(f'sudo ip route del default via 192.168.10.1', shell=True)
  subprocess.check_call(f'sudo ip route add default via 192.168.69.1', shell=True)

  # Setup radio
  rx = setup_radio(MOBILE_2_ADDR, BASE_2_ADDR, 10, DigitalInOut(board.D27), True)
  tx = setup_radio(MOBILE_ADDR, BASE_ADDR, 0, DigitalInOut(board.D17), False)

  print('Setup done')
  return rx, tx

def teardown_base(interface_name, rx, tx):
  subprocess.check_call(f'sudo iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE', shell=True)
  # subprocess.check_call(f'sudo iptables -D FORWARD -i eth0 -o {interface_name} -m state --state RELATED,ESTABLISHED -j TCPMSS --set-mss 7896 -p tcp --tcp-flags SYN,RST SYN -m tcpmss --mss 7896:7926 ', shell=True)
  subprocess.check_call(f'sudo iptables -D FORWARD -i eth0 -o {interface_name} -m state --state RELATED,ESTABLISHED -j ACCEPT', shell=True)
  subprocess.check_call(f'sudo iptables -D FORWARD -i {interface_name} -o eth0 -j ACCEPT', shell=True)

  teardown_radios(rx, tx)
  print('Teardown done')

def teardown_mobile(rx, tx):
  subprocess.check_call(f'sudo ip route add 192.168.10.0/24 dev eth0', shell=True)
  subprocess.check_call(f'sudo ip route del 192.168.10.163 dev eth0', shell=True)
  subprocess.check_call(f'sudo ip route del default via 192.168.69.1', shell=True)
  subprocess.check_call(f'sudo ip route add default via 192.168.10.1', shell=True)

  teardown_radios(rx, tx)
  print('Teardown done')

def show_title():
	os.system('clear')
	# print('\u001b[0;0H')
	print("***********************************************")
	print("***                \u001b[38;2;255;168;0mSnake\u001b[38;2;226;109;0mData\u001b[0m                ***")
	print("*** - Get your data where your snake is \u001b[38;2;255;168;0m@\u001b[0m - ***")
	print("***********************************************")

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
	print(SINGLE_LEFT_TOP + SINGLE_HORIZ_PIPE * 46)

	print(SINGLE_VERTI_PIPE + ' \u001b[7mSTATUS:\u001b[0m (Press enter to update)')
	for title, value in status.items():
		print(SINGLE_VERTI_PIPE + f' * {title}:\t{value}')

	print(SINGLE_LEFT_BOTTOM + SINGLE_HORIZ_PIPE * 46)
	print('\n')
  
def run_program(buffer_monitor, rx_thread, tx_thread, interface_reader_thread): 
  while True:
    show_title()
    sent, received, sent_ip, received_ip, sent_bytes, received_bytes, fails, largest_packet = buffer_monitor.get_stats()
    print_screen({
      'sent': f'{sent:,} ({sent_ip:,} ip, {sent_bytes:,} bytes)',
      'received': f'{received:,} ({received_ip:,} ip, {received_bytes:,} bytes)',
      'failed': f'{fails:,}',
      'bfr_size': f'{buffer_monitor.size()}',
      'splitting': f'{buffer_monitor.get_splitting()}',
      'largest': f'{largest_packet:,}'
    })

    c = input('Enter command: ').lower().strip()

    if c == 'exit' or c == 'q' or c == 'quit':
      rx_thread.terminate()
      tx_thread.terminate()
      interface_reader_thread.terminate()
      break
    elif c == 'clear':
      buffer_monitor.clear_stats()

def setup(device, interface_name='longge'):
  mask = '255.255.255.0'
  tunnel_ip = '192.168.69.1' if device == 'b' else '192.168.69.2'
  tun = OpenTunnel(interface_name, tunnel_ip, mask)
  rx, tx = setup_base(interface_name) if device == 'b' else setup_mobile(interface_name)
  return rx, tx, tun

def teardown(device, rx, tx, tun, interface_name='longge'):
  if device == 'b': teardown_base(interface_name, rx, tx)
  else: teardown_mobile(rx, tx)
  
  tun.close()

if __name__ == "__main__":
  device = input('Base (b) or Mobile (m) > ')
  while device != 'b' and device != 'm':
    device = input('Invalid input. Base (b) or Mobile (m) > ')

  BaseManager.register('BufferMonitor', BufferMonitor)
  manager = BaseManager()
  manager.start()
  buffer_monitor = manager.BufferMonitor()
  
  rx, tx, tun = setup(device)

  rx_thread = multiprocessing.Process(target=rx_model.rx_thread, args=(rx, tun, buffer_monitor))
  rx_thread.start()

  tx_thread = multiprocessing.Process(target=tx_model.tx_thread, args=(tx, buffer_monitor))
  tx_thread.start()

  interface_reader_thread = multiprocessing.Process(target=tx_model.interface_reader_thread, args=(tun, buffer_monitor))
  interface_reader_thread.start()

  run_program(buffer_monitor, rx_thread, tx_thread, interface_reader_thread)

  teardown(device, rx, tx, tun)
from tuntap import TunTap, Packet
import sys, os, time, subprocess

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
  subprocess.check_call(f'sudo iptables -t nat -A POSTROUTING -o {interface} -j MASQUERADE', shell=True)
  subprocess.check_call(f'sudo iptables -A FORWARD -i eth0 -o {interface} -m state --state RELATED,ESTABLISHED -j ACCEPT', shell=True)
  subprocess.check_call(f'sudo iptables -A FORWARD -i {interface} -o eth0 -j ACCEPT', shell=True)
  print('Setup done')

def setup_mobile(interface):
  ...

def teardown_base(interface):
  subprocess.check_call(f'sudo iptables -t nat -D POSTROUTING -o {interface} -j MASQUERADE', shell=True)
  subprocess.check_call(f'sudo iptables -D FORWARD -i eth0 -o {interface} -m state --state RELATED,ESTABLISHED -j ACCEPT', shell=True)
  subprocess.check_call(f'sudo iptables -D FORWARD -i {interface} -o eth0 -j ACCEPT', shell=True)
  print('Teardown done')

def teardown_mobile(interface):
  ...

if __name__ == "__main__":
  device = int(input('Base (0) or Mobile (1) > '))
  interface = 'longge'
  print(device)

  if device == 0:
    tunnel_ip = '192.168.69.1'
    mask = '255.255.255.0'
    tun = OpenTunnel(interface, tunnel_ip, mask)
    setup_base(interface)
    start()
    teardown_base(interface)
  else:
    tunnel_ip = '192.168.69.2'
    mask = '255.255.255.0'
    tun = OpenTunnel(interface, tunnel_ip, mask)
    setup_base(interface)
    start()
    teardown_base(interface)
from tuntap import TunTap, Packet
import sys, os, time

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
  i = 10
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

if __name__ == "__main__":
  device = int(input('Base (0) or Mobile (1) > '))
  print(device)

  if device == 0:
    tunnel_ip = '192.168.69.1'
    mask = '255.255.255.0'
    tun = OpenTunnel('tun0', tunnel_ip, mask)
  else:
    tunnel_ip = '192.168.69.2'
    mask = '255.255.255.0'
    tun = OpenTunnel('tun0', tunnel_ip, mask)

  start()
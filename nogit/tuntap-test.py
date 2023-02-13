from tuntap import TunTap, Packet
from _thread import start_new_thread

# tun = TunTap(nic_type="Tun",nic_name="tun0")

# tun.config(ip="192.168.2.1",mask="255.255.255.0", gateway="192.168.10.1")

# print(tun.read())


# tun.close()

##################################################

# def readtest(tap):
#     while not tap.quitting:
#         p = tap.read()
#         if not p:
#             continue
#         if tap.nic_type == "Tap":
#             packet = Packet(frame=p)
#         else:
#             packet = Packet(data=p)
#         if not packet.get_version()==4:
#             continue
#         print(''.join('{:02x} '.format(x) for x in packet.data))
#         if tap.nic_type == "Tun":
#             pingback = p[:12]+p[16:20]+p[12:16]+p[20:]
#             tap.write(pingback)


# def main():
#     try:
#         tuntap = TunTap(nic_type="Tun",nic_name="tun0")
#         tuntap.config(ip="192.168.2.2",mask="255.255.255.0", gateway="192.168.2.1")
#         #, opt.tmtu, opt.laddr,opt.lport, opt.raddr, opt.rport)
#     except Exception as e:
#         print('EROROROR')
#         return 1
#     start_new_thread(readtest,(tuntap,))
#     input("press return key to quit!")
#     tuntap.close()
#     return 0

# main()


##################################################

# from tuntap import TunTap, Packet

tun = TunTap(nic_type="Tun",nic_name="tun0")

tun.config(ip="192.168.2.1",mask="255.255.255.0",gateway="192.168.10.1")

data = tun.read()

packet = Packet(data=data)

print(f"Packet version: {packet.get_version()}")

print(f"Tun name: {tun.name}, Tun ip: {tun.ip}, Tun mask: {tun.mask}, Gateway: {tun.gateway}")

tun.close()

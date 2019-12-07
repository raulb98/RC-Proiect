import os
import socket
from Concat_dict import *
import logging
#import netifaces
logging.basicConfig(filename='app.log', filemode='w')
#ip = netifaces.ifaddresses(netifaces.interfaces()[len(netifaces.interfaces())-1])[]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
sock.bind(('0.0.0.0',67))

dhcp_discover = {
    'op' : b'01',
    'htype' : b'01',
    'hlen' : b'06',
    'hops' : b'00',
    'xid' : b'aabbccdd',
    'secs' : b'0300',
    'flags' : b'0001',
    'ciaddr' : b'00000000',
    'yiaddr' : b'00000000',
    'siaddr' : b'00000000',
    'giaddr' : b'00000000',
    'chaddr' : b'7c7635e2fd3d00000000000000000000',
    'sname' : b'416e6472656920202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020',
    'file' : b'67656e6572696320202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020',
    'options' : b'0104FFFFFFA4FF0308C0A86446C0A864A3FF0604C0A86445FF15085461746142616369FF2804C0A864C7FF530101FF5404C0A864B6FF580400011940FF'
}

message_discover = concat_dict(dhcp_discover)
import time

print(len(message_discover))

sock.connect_ex(('192.168.43.151',5000))

try:
     sock.send(message_discover)
     time.sleep(0.001)
except Exception as e:
      logging.warning(e)

dhcp_discover = {
    'op' : b'01',
    'htype' : b'01',
    'hlen' : b'06',
    'hops' : b'00',
    'xid' : b'ffffffff',
    'secs' : b'0000',
    'flags' : b'0001',
    'ciaddr' : b'00000000',
    'yiaddr' : b'00000000',
    'siaddr' : b'00000000',
    'giaddr' : b'00000000',
    'chaddr' : b'00000000',
    'DHCP_option' : b'350101',
    'DHCP_param_req_list' : b'370401030f06',
    'end_mark' : b'ff'
}
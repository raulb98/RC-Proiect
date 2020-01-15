import time
import logging
import socket

DHCP_DATA = {
            'offer' : {
                'op': 0,
                'xid': 0,
                'hlen': 0,
                'yiaddr': 0,
                'options' : {}
            },
            'request' : {
                'op': 0,
                'xid': 0,
                'hlen': 0,
                'yiaddr': 0,
                'options' : {}
            },
            'ack' : {
                'op': 0,
                'xid': 0,
                'hlen': 0,
                'yiaddr': 0,
                'options' : {}
            }
        }

DHCP_MSGS = {
            'Discover' : None,
            'Offer' : None,
            'Request' : None,
            'Ack' : None
        }

class Communication_Level():
    def __init__(self,socket):
        self.socket = socket
        self.level = [False for i in range(0,4)]
        self.lease_time = 0
        self.data_on_each_level = DHCP_DATA
        self.messages = DHCP_MSGS
        self.my_ip_bytes = []
        self.my_ip = []
        self.requested_ip = None
        
        logging.warning("Communcation established")


    def transform_to_ip(self,text):

        def bytes_to_int(bytes):
            result = 0
            idx = 1
            for b in bytes:
                if b >= 97 and b <= 102:
                    b -= 87
                elif b >= 48 :
                    b -= 48
                #print(b)

                result = result + pow(16,idx)*b
                idx -= 1
            return result

        rez = ''
        index1 = 0
        index2 = 2

        for i in range(0,4):
            ip_part = bytes_to_int(text[index1:index2])
            rez += str(ip_part) + '.'
            index1+=2
            index2+=2
        return rez[0:len(rez)-1]

    def decode_message(self,message):
        if b'63825363' in message:
            message_aux = str(message)
            splited_message = message_aux.split('63825363')
            message_tp = splited_message[1][4:6]

        def unpack_options(msg_options):
           list_rez = [None,None]
           dict_result = {
                      '35' : ['DHCP Msg Type',None],
                      '32' : ['Address Request',None],
                      '3d' : ['Client Id',None],
                      '0c' : ['Hostname',None],
                      '3c' : ['Class Id',None],
                      '37' : ['Parameter List',None],
                      '33' : ['Address Time',None],
                      '00' : ['Pad',None],
                      '36' : ['DHCP Server ID',None],
                      'a8' : ['Unassigned',None],
                      '3a' : ['Renewal Time',None]
           }
           list_options = {'00' : 4,
                           '35' : 4,
                           '32' : 10,
                           '3d' : 16,
                           '0c' : 20,
                           '3c' : 18,
                           '37' : 26,
                           '33' : 4,
                           '36' : 4,
                           'a8' : 4,
                           '3a' : 4,
                           'ff' : None}

           o1 = 0
           o2 = 2

           while msg_options[o1:o2] != 'ff' and msg_options[o1:o2] != 'FF':
               #print(o1,o2)
               if msg_options[o1:o2] in list_options:
                   offset = list_options[msg_options[o1:o2]]
                  # print(msg_options[o1:o2])
                   if msg_options[o1:o2] == '33':
                       list_rez[1] = msg_options[o2:(o2+offset)]
                   dict_result[msg_options[o1:o2]][1] = msg_options[o2:(o2+offset)]
                   aux1 = o1 + offset + 2
                   aux2 = o2 + offset + 2

                   o1 = aux1
                   o2 = aux2
                   
           list_rez[0] = dict_result
          # print(list_rez)
           return list_rez
        
        def write(self,message,type):
            if type == '01':
                self.messages['Discover'] = message
                infos = unpack_options(splited_message[1])
                self.level[0] = True
                logging.warning(r'DHCP_Discover Message is about to be Broadcasted')
                time.sleep(1)

            elif type == '02':
                logging.warning('DHCP_Offer Messages has been received')
                time.sleep(1)
                self.messages['Offer'] = message
                self.data_on_each_level['offer']['op'] = message[0:2]
                self.data_on_each_level['offer']['xid'] = message[9:17]
                self.data_on_each_level['offer']['hlen'] = message[4:6]
                self.data_on_each_level['offer']['yiaddr'] = message[32:40]
                self.my_ip.append(self.transform_to_ip(self.data_on_each_level['offer']['yiaddr']))
                self.my_ip_bytes.append(self.data_on_each_level['offer']['yiaddr'])
                logging.warning('IP received {}'.format(self.my_ip[-1]))
                infos = unpack_options(splited_message[1])

                if infos[1] is not None:
                    self.lease_time = infos[1]
                    
                self.level[1] = True

            elif type == '03':
                logging.warning('DHCP_Request is about to be sent')
                time.sleep(1)
                self.messages['Request'] = message
                self.data_on_each_level['request']['op'] = message[0:2]
                self.data_on_each_level['request']['xid'] = message[9:17]
                self.data_on_each_level['request']['hlen'] = message[4:6]
                self.data_on_each_level['request']['yiaddr'] = message[32:40]
                infos = unpack_options(splited_message[1])
                self.level[2] = True

            elif type == '05':
                logging.warning('DHCP_Ack has been received')
                self.messages['Ack'] = message
                self.data_on_each_level['ack']['op'] = message[0:2]
                self.data_on_each_level['ack']['xid'] = message[9:17]
                self.data_on_each_level['ack']['hlen'] = message[4:6]
                self.data_on_each_level['ack']['yiaddr'] = message[32:40]
                print(self.data_on_each_level['ack'])
                infos = unpack_options(splited_message[1])
                self.level[3] = True

        if message_tp == '01':
            write(self,message,'01')
            return 'discover'
        elif message_tp == '02':
            write(self,message,'02')
            return 'offer'
        elif message_tp == '03':
            write(self,message,'03')
            return 'request'
        elif message_tp == '05':
            write(self,message,'05')
            return 'ack'

    def send(self,type):
        if type == 'discover':
            message = self.messages['Discover']
            sender = SendMessage(message,self.socket)
            sender.sendTo()
        elif type == 'request':
            message = self.messages['Request']
            sender = SendMessage(message,self.socket)
            sender.sendTo()

    def receive(self,type):
        message = RecvMessage(self.socket)
        try:
            message_data = message.get_data()
        except Exception as e:
            print(e)
        return message_data

class SendMessage():
    def __init__(self,message,my_socket):
        self.message = message
        self.mysocket = my_socket
        self.nr_bytes = len(self.message)

    def sendTo(self):
          if self.nr_bytes is not 0:
                try:
                    self.mysocket.sendto(self.message,('255.255.255.255',67))
                    logging.warning('Trying to send data')
                    time.sleep(1)
                except Exception as e:
                    logging.warning(e)
          else:
              logging.warning('Message has length 0')

class RecvMessage():
    def __init__(self,socket):
        self.data = None
        self.sock = socket

    def get_data(self):
        while True:
            data,addr = self.sock.recvfrom(1024)
            self.data = data
            logging.warning('Received message from {}'.format(addr))
            if len(self.data) is not 0:
                break
        return self.data

def assign_ip(message,xid):
    message['xid'] = xid
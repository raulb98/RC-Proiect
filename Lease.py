import time
import datetime
import MessageType
import Messages
import Concat_dict
import logging

class lease():
    def __init__(self,time_to_reconfigure,socket,req):
        self.date_time = datetime.datetime.now().time()
        self.start_time = 0
        self.time_to_reconfigure = time_to_reconfigure
        self.half_time = time_to_reconfigure / 2
        self.rebind_time = 7 * time_to_reconfigure / 8
        self.release_time = time_to_reconfigure
        self.socket = socket
        self.request = req
        self.end_process = False

    def reconfigure(self):
        self.start_time = 0
        self.half_time = self.time_to_reconfigure / 2
        self.time_to_finish = self.time_to_reconfigure
        
    def run(self):
        logging.warning('Lease Time is ' + str(self.time_to_reconfigure))
        logging.warning('Lease time started')
        while not self.end_process:
            logging.warning('')
            time.sleep(1)
            self.start_time += 1
            print('Lease time remaining: ' + str(self.start_time))
            
            if self.start_time >= self.half_time and self.start_time < self.rebind_time:
                my_sender = MessageType.SendMessage(self.request,self.socket)
                my_sender.sendTo()
                msg_rcv = MessageType.RecvMessage(self.socket)
                if len(msg_rcv) > 0:
                    self.reconfigure()
                    logging.warning('Lease time renewed')
            
            if self.start_time >= self.release_time:
                self.end_process = True
                logging.warning('Lease time released')

            if self.start_time >= self.rebind_time:
                assign_ciaddr(Messages.dhcp_request_renew,self.com_level.my_ip_bytes[-1])
                my_sender = MessageType.SendMessage(Concat_dict.concat_dict(Messages.dhcp_request_renew))
                my_sender.sendTo()
                msg_rcv = MessageType.RecvMessage(self.socket)
                if len(msg_rcv) > 0:
                    self.reconfigure()
                    logging.warning('Lease time renewed')

            
import threading
import os
import socket
from Concat_dict import *
from Messages import *
from MessageType import *
import logging
import Lease
import tkinter as tk
import tkinter.scrolledtext as ScrolledText
import datetime
import struct
import math

logging.basicConfig(filename='app.log', filemode='w')

#sock.connect_ex(('192.168.43.151',5000))


class TextHandler(logging.Handler):

    def __init__(self, text):
        logging.Handler.__init__(self)
        self.text = text

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            self.text.insert(tk.END, msg + '\n')
            self.text.configure(state='disabled')
            self.text.yview(tk.END)
        self.text.after(0, append)

class GUI(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(('0.0.0.0', 68))
        self.com_level = Communication_Level(self.sock)
        self.thread_comm = threading.Thread(target=self.run_comm)
        self.thread_release = threading.Thread(target=self.release_comm)
        self.lease_entry = tk.Entry(self)
        self.build_gui()

    def run(self):
        t1 = threading.Thread(target=self.run_comm)
        t1.start()

    def run_comm(self):
        now1 = datetime.datetime.now()
        self.com_level.decode_message(concat_dict(dhcp_discover))
        self.com_level.send('discover')
        
        message_recv = self.com_level.receive('offer')
        self.com_level.decode_message(message_recv)

        #self.com_level.decode_message(concat_dict(dhcp_decline))
        #self.com_level.send('decline')

        assign_ip(dhcp_requestsel, self.com_level.my_ip_bytes[-1])
        now2 = datetime.datetime.now()
        delta = now2 - now1

        delta_bytes = math.floor(delta.total_seconds())
        assign_seconds(dhcp_requestsel,hex(delta_bytes))
        self.com_level.decode_message(concat_dict(dhcp_requestsel))
        self.com_level.send('request')

        message_recv = self.com_level.receive('ack')
        self.com_level.decode_message(message_recv)

        lease_time = int(self.com_level.lease_time, base=16)
        dhcp_lease = Lease.lease(lease_time, self.sock, concat_dict(dhcp_request_renew))
        dhcp_lease.reconfigure()
        dhcp_lease.run()
        self.release_comm()

    def stop_execution(self):
        self.thread_comm.join()

    def release_comm(self):
        my_sender = SendMessage(concat_dict(dhcp_release),self.sock)
        my_sender.sendTo()
        self.com_level.data_on_each_level = DHCP_DATA
        self.com_level.messages = DHCP_MSGS
        self.com_level.my_ip_bytes = []
        self.com_level.my_ip = []
        self.lease_time = 0
        logging.warning('Sending DHCP_Release')

    def build_gui(self):
        self.root.title('DHCP Client')
        self.root.option_add('*tearOff', 'FALSE')


        RunButton = tk.Button(self, text="Start Communication", fg="black",command=self.run)
        RunButton.grid(row=2, column=0)
        
        ReleaseButton = tk.Button(self, text="Release Communication", fg="black", command=self.thread_release.start)
        ReleaseButton.grid(row=3, column=0)

        self.lease_entry.insert(0, 'Waiting')
        self.lease_entry.grid(row=3, column=1)

        #ReleaseButton = tk.Button(self, text="Release IP" , fg="black" ,command=)

        self.grid(column=0, row=0, sticky='ew')
        self.grid_columnconfigure(0, weight=1, uniform='a')
        self.grid_columnconfigure(1, weight=1, uniform='a')
        self.grid_columnconfigure(2, weight=1, uniform='a')
        self.grid_columnconfigure(3, weight=1, uniform='a')

        st = ScrolledText.ScrolledText(self, state='disabled')
        st.configure(font='TkFixedFont')
        st.grid(column=0, row=1, sticky='w', columnspan=4)

        text_handler = TextHandler(st)

        logging.basicConfig(filename='test.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s')

        logger = logging.getLogger()
        logger.addHandler(text_handler)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("500x500+450+150")
    app = GUI(root)
    root.mainloop()
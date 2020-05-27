###############################################################################
# NAME:             udp.py
#
# AUTHOR:           Ethan D. Twardy <edtwardy@mtu.edu>
#
# DESCRIPTION:      Implements a standard UDP server/client interface.
#
# CREATED:          05/19/2020
#
# LAST EDITED:      05/27/2020
###

import socket

class Server:
    def __init__(self, handler, address):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(address)
        self.handler = handler

    def __enter__(self):
        return self

    def __exit__(self, exType, exValue, traceback):
        self.socket.close()

    def start(self):
        while True:
            message, address = self.socket.recvfrom(64)
            response = self.handler(message.decode('utf-8'), address)
            if response:
                self.socket.sendto(str.encode(response), address)

class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __enter__(self):
        return self

    def __exit__(self, exType, exValue, traceback):
        self.socket.close()

    def send(self, message, address, waitForResponse=True,
             responseBufferSize=64):
        bytesSent = self.socket.sendto(str.encode(message), address)
        if waitForResponse:
            message, address = self.socket.recvfrom(responseBufferSize)
            return message.decode('utf-8')
        return bytesSent

    def recvfrom(self, bufferSize=64):
        message, address = self.socket.recvfrom(bufferSize)
        return message.decode('utf-8'), address

###############################################################################

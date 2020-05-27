###############################################################################
# NAME:             CretanDaemon.py
#
# AUTHOR:           Ethan D. Twardy <edtwardy@mtu.edu>
#
# DESCRIPTION:      The daemon that is responsible for listening for/sending
#                   messages.
#
# CREATED:          05/26/2020
#
# LAST EDITED:      05/27/2020
###

from threading import Thread
from queue import Queue
from configparser import ConfigParser
import json
import argparse
import sys

import Service
from protocol import Udp

###############################################################################
# Class MessageDispatcher
###

class MessageDispatcher:

    def __init__(self, streams, queue):
        self.streams = streams
        self.queue = queue

    def validateMessage(self, message):
        if message['stream'] not in self.streams:
            print(('{} attempted to send a message to stream {}, but no'
                   ' such stream exists.').format(message['source'],
                                                  message['stream']),
                  file=sys.stderr)

    def start(self):
        print('Listening for messages...')
        while True:
            message = self.queue.get()
            if not self.validateMessage(message):
                continue
            self.streams[message['stream']].writeMessage(message['message'])

###############################################################################
# Class Stream
###

class Stream:

    def __init__(self, dictionary):
        self.name = dictionary['name']
        self.handler = Service.STREAMS[dictionary['mechanism'].upper()]()

    def getName(self):
        return self.name

    def writeMessage(self, message):
        self.handler.write(message)

###############################################################################
# Class UDPListener
###

class UDPListener(Thread):

    def __init__(self, queue, address):
        super().__init__()
        self.queue = queue
        self.address = address

    def handleMessage(self, payload, address):
        print('Received message: "{}"'.format(payload))
        message = {}
        components = payload.split('\n')
        if len(components) < 3:
            return '-Formatting error'
        message['source'] = components[0]
        message['stream'] = components[1]
        message['message'] = '\n'.join(components[2:])
        self.queue.put(message)
        return "+Ok"

    def run(self):
        with Udp.Server(self.handleMessage, self.address) as server:
            print('Starting server...')
            server.start()

###############################################################################
# Main
###

def getUdpListener(config, queue):
    if 'udp' not in config:
        raise RuntimeError('No listeners defined in configuration file.')
    address = (config['udp']['address'], int(config['udp']['port']))
    return UDPListener(queue, address)

def getConfiguration(confFile):
    config = ConfigParser()
    try:
        with open(confFile, 'r') as inFile:
            config.read(confFile)
            return config
    except FileNotFoundError:
        with open(confFile, 'w') as outFile:
            config['daemon'] = {}
            config['udp'] = {'port': '13001', 'address': '127.0.0.1'}
            config.write(outFile)
            return config

def getStreams(streamFile):
    streams = []
    try:
        with open(streamFile, 'r') as inFile:
            for stream in json.load(inFile):
                streams.append(Stream(stream))
    except FileNotFoundError:
        with open(streamFile, 'w') as outFile:
            json.dump([], outFile)
    return streams

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf', help=('The configuration file'),
                        default='conf.ini')
    parser.add_argument('-s', '--streams', help=('The streams file'),
                        default='streams.json')
    return parser.parse_args()

def main():

    arguments = vars(parseArgs())
    config = getConfiguration(arguments['conf'])
    streams = getStreams(arguments['streams'])

    messageQueue = Queue()

    # Create the listening thread
    listener = getUdpListener(config, messageQueue)
    listener.start()

    # Begin dispatching messages
    dispatcher = MessageDispatcher(streams, messageQueue)
    dispatcher.start()

if __name__ == '__main__':
    main()

###############################################################################

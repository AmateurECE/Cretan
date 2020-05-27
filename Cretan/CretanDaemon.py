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

import service
from protocol import udp

###############################################################################
# Class Stream
###

class Stream:

    def __init__(self, dictionary):
        self.name = dictionary['name']
        self.handler = service.streamMapping[dictionary['mechanism'].upper()]()

    def getName(self):
        return self.name

    def writeMessage(self, message):
        self.handler.write(message)

###############################################################################
# Main
###

def getConfiguration(confFile):
    config = ConfigParser()
    try:
        with open(confFile, 'r') as inFile:
            config.read(inFile)
            return config
    except FileNotFoundError as e:
        with open(confFile, 'w') as outFile:
            config['daemon'] = {'ipc': 'udp'}
            config.write(outFile)
            return config

def getStreams(streamFile):
    streams = []
    try:
        with open(streamFile, 'r') as inFile:
            for stream in json.parse(streamsFile):
                streams.append(Stream(stream))
    except FileNotFoundError as e:
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

    print(arguments)
    print(config)
    print(streams)
    # messageQueue = Queue()

if __name__ == '__main__':
    main()

###############################################################################

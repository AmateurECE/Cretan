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
# LAST EDITED:      05/28/2020
###

import asyncio
from configparser import ConfigParser
import json
import argparse

import Service

###############################################################################
# Class MessageDispatcher
###

class MessageDispatcher:

    def __init__(self, streams):
        self.streams = streams

    def isValidStream(self, stream):
        return stream in self.streams

    async def dispatch(self, message, transport):
        theStream = self.streams[message['stream']]
        response = await theStream.writeMessage(message['message'])
        if message['responseRequested']:
            transport.sendto(response.encode('utf-8'), message['address'])

###############################################################################
# Class Stream
###

class Stream:

    def __init__(self, name, dictionary):
        self.name = name
        self.handler = Service.STREAMS[dictionary['mechanism'].upper()]()

    def getName(self):
        return self.name

    async def writeMessage(self, message):
        return await self.handler.write(message)

###############################################################################
# Class CretanUdpProtocol
###

class CretanUdpProtocol:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def connection_made(self, transport):
        self.transport = transport

    def validateMessage(self, message):
        if not self.dispatcher.isValidStream(message['stream']):
            return False, "-No such stream"
        if message['responseRequested'] != 'False' \
           and message['responseRequested'] != 'True':
            return False, "-Incorrect value (field: responseRequested)"
        return True, "+Ok"

    def datagram_received(self, data, address):
        components = data.decode().split('\n')
        if len(components) < 4:
            error = '-Format error'
            self.transport.sendto(error.encode('utf-8'), address)
            return
        message = {
            'source': components[0],
            'address': address,
            'stream': components[1],
            'responseRequested': components[2],
            'message': components[3],
        }
        isValid, error = self.validateMessage(message)
        if not isValid:
            if message['responseRequested'] == 'True':
                self.transport.sendto(error.encode('utf-8'), address)
            return
        asyncio.create_task(self.dispatcher.dispatch(message, self.transport))

###############################################################################
# Class UdpBroker
###

class UdpBroker:

    def __init__(self, address):
        self.address = address

    async def start(self, dispatcher):
        loop = asyncio.get_running_loop()

        # This null future allows us to put this task to sleep eternally.
        onConnectionLost = loop.create_future()

        transport, protocol = await loop.create_datagram_endpoint(
            lambda: CretanUdpProtocol(dispatcher),
            local_addr=self.address)

        try:
            await onConnectionLost
        finally:
            transport.close()

###############################################################################
# Main
###

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
    streams = {}
    try:
        with open(streamFile, 'r') as inFile:
            streamsFromFile = json.load(inFile)
            for streamName in streamsFromFile:
                streams[streamName] = Stream(
                    streamName, streamsFromFile[streamName])
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

async def main():
    arguments = vars(parseArgs())
    config = getConfiguration(arguments['conf'])
    streams = getStreams(arguments['streams'])

    broker = UdpBroker((config['udp']['address'], config['udp']['port']))
    dispatcher = MessageDispatcher(streams)
    await broker.start(dispatcher)

if __name__ == '__main__':
    asyncio.run(main())

###############################################################################

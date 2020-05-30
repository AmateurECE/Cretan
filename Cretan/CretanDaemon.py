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
# LAST EDITED:      05/30/2020
###

# TODO: Rename this file to just 'Daemon'

import asyncio
from configparser import ConfigParser
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
        # TODO: Make message a class
        response = await theStream.writeMessage(message)
        if message['responseRequested']:
            transport.sendto(response.encode('utf-8'), message['address'])

###############################################################################
# Class Stream
###

class Stream:

    def __init__(self, service, name, mechanism, config):
        self.name = name
        self.handler = Service.STREAM_HANDLERS[mechanism.upper()](
            service, config)

    def getName(self):
        return self.name

    async def writeMessage(self, message):
        return await self.handler.write(message)

    async def start(self, loop):
        return await self.handler.start(loop)

###############################################################################
# Class CretanUdpProtocol
###

class CretanUdpProtocol:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def validateMessage(self, message):
        if not self.dispatcher.isValidStream(message['stream']):
            return False, "-No such stream"
        if message['responseRequested'] != 'False' \
           and message['responseRequested'] != 'True':
            return False, "-Incorrect value (field: responseRequested)"
        return True, "+Ok"

    # TODO: Add some print statements for logging
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
            'message': '\n'.join(components[3:]),
        }
        isValid, error = self.validateMessage(message)
        if not isValid:
            if message['responseRequested'] != 'False':
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
        if not config.read(confFile):
            raise FileNotFoundError(confFile)
        return config
    except FileNotFoundError:
        with open(confFile, 'w') as outFile:
            config['daemon'] = {}
            config['udp'] = {'port': '13001', 'address': '127.0.0.1'}
            config.write(outFile)
            return config

def getServices(config):
    recognizedServices = Service.getRecognizedServices()
    services = {}
    for name in config:
        if name.upper() in recognizedServices:
            services[name] = Service.SERVICES[name.upper()](config[name])
    return services

def getStreams(streamFile, services):
    streams = {}
    try:
        streamConfig = ConfigParser()
        if not streamConfig.read(streamFile):
            raise FileNotFoundError(streamFile)
        for entry in streamConfig:
            if entry == 'DEFAULT':
                continue
            name, mechanism = entry.split(':')
            streams[name] = Stream(services[mechanism], name, mechanism,
                                   streamConfig[entry])
    except FileNotFoundError:
        newStreamFile = open(streamFile, 'w')
        newStreamFile.close()
    return streams

def parseArgs():
    # TODO: Change default values for conf files
    # TODO: Allow naming of services
    #   Currently, clients cannot connect to a service on a separate host if
    #   there is a daemon running on the current host that has exposed the same
    #   service. Allow users to name services, to distinguish them from their
    #   mechanism.
    # TODO: Create service configuration in config file
    #   The discord service requires an API token, which must currently be
    #   placed in every stream declaration in streams.ini. Create a more robust
    #   system that declares configuration for services like so:
    #
    #   conf.ini:
    #     [discord]
    #     token = MyToken
    #
    #   streams.ini:
    #     [mystream:discord]
    #     (...)
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf', help=('The configuration file'),
                        default='conf.ini')
    parser.add_argument('-s', '--streams', help=('The streams file'),
                        default='streams.ini')
    return parser.parse_args()

async def main():
    arguments = vars(parseArgs())
    config = getConfiguration(arguments['conf'])
    services = getServices(config)

    # initialize services
    for key in services:
        await services[key].start()

    broker = UdpBroker((config['udp']['address'], config['udp']['port']))
    streams = getStreams(arguments['streams'], services)
    dispatcher = MessageDispatcher(streams)
    await broker.start(dispatcher)

if __name__ == '__main__':
    asyncio.run(main())

###############################################################################

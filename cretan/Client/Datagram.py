###############################################################################
# NAME:             Datagram.py
#
# AUTHOR:           Ethan D. Twardy <edtwardy@mtu.edu>
#
# DESCRIPTION:      UDP framework for the client API.
#
# CREATED:          05/29/2020
#
# LAST EDITED:      05/30/2020
###

import asyncio

from .ClientCommon import getSenderString

class CretanDatagramProtocol:

    def __init__(self, message, stream, onConnectionLost):
        self.message = message
        self.stream = stream
        self.onConnectionLost = onConnectionLost
        self.transport = None

    # TODO: Put message parsing/creating logic into one place.
    def prepareMessage(self):
        gram = (
            f'{getSenderString(self.message.getSender())}\n'
            f'{self.stream}\n'
            f'{self.message.getResponseRequested()}\n'
            f'{self.message.getMessageContent()}')
        return gram.encode()

    def connection_made(self, transport):
        self.transport = transport
        self.transport.sendto(self.prepareMessage())
        if not self.message.getResponseRequested():
            self.transport.close()

    def datagram_received(self, data, address):
        if address != self.transport.get_extra_info('peername'):
            return # Ignore grams from strange addresses
        if not self.onConnectionLost.done():
            self.onConnectionLost.set_result(
                {'hasResult': True, 'result': data.decode()})
        self.transport.close()

    def error_received(self, exc):
        self.onConnectionLost.set_result(
            {'hasResult': True, 'result': str(exc)})
        raise exc

    def connection_lost(self, exc):
        if exc is None and not self.onConnectionLost.done():
            self.onConnectionLost.set_result({'hasResult': False})

class Datagram:

    def __init__(self, address, port):
        self.address = address
        self.port = port

    async def handleResponse(self, responseRequested, onConnectionLost):
        if responseRequested:
            # If we ask for a response and we don't get one within 1
            # second, throw asyncio.TimeoutError
            await asyncio.wait([onConnectionLost], timeout=1)
        else:
            await onConnectionLost

        if not onConnectionLost.done():
            raise TimeoutError('Did not receive response from server.')

        if responseRequested and onConnectionLost.result()['hasResult']:
            if onConnectionLost.result()['result'][0] == '+':
                return True # Asked for result, got one and it's good
            raise RuntimeError(onConnectionLost.result()['result'])
        elif not responseRequested and onConnectionLost.result()['hasResult']:
            if onConnectionLost.result()['result'][0] == '-':
                # Should only happen in the case of a formatting error
                raise RuntimeError(onConnectionLost.result()['result'])
        # Did not ask for a result, did not get one.
        return True

    async def send(self, message, stream):
        loop = asyncio.get_running_loop()
        onConnectionLost = loop.create_future()

        transport = (await loop.create_datagram_endpoint(
            lambda: CretanDatagramProtocol(message, stream, onConnectionLost),
            remote_addr=((self.address, self.port))))[0]

        try:
            return await self.handleResponse(
                message.getResponseRequested(), onConnectionLost)
        finally:
            transport.close()

###############################################################################

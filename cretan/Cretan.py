###############################################################################
# NAME:             Cretan.py
#
# AUTHOR:           Ethan D. Twardy <edtwardy@mtu.edu>
#
# DESCRIPTION:      This is the Python API for interacting with the server.
#
# CREATED:          05/29/2020
#
# LAST EDITED:      05/30/2020
###

import configparser

from . import Client

# TODO: Change the default value for conf file path
def getService(serviceName, confFile="conf.ini"):
    """A Service is used to send messages to the server.
    serviceName: The name of the configured listener on the server-side
        (e.g. udp);
    confFile: The path of the confFile that the server is configured from.
    """
    conf = configparser.ConfigParser()
    if not conf.read(confFile):
        raise FileNotFoundError(confFile)
    if serviceName not in conf:
        raise ValueError(f'No such service {serviceName} in {confFile}')
    return Client.CLIENTS[serviceName](conf[serviceName])

class Message:

    def __init__(self, messageContent, sender="", responseRequested=True):
        self.messageContent = messageContent
        self.sender = sender
        self.responseRequested = responseRequested

    def getResponseRequested(self):
        return self.responseRequested

    def getMessageContent(self):
        return self.messageContent

    def getSender(self):
        return self.sender

###############################################################################

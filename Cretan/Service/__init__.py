###############################################################################
# NAME:             __init__.py
#
# AUTHOR:           Ethan D. Twardy <edtwardy@mtu.edu>
#
# DESCRIPTION:      Service module stream mapping.
#
# CREATED:          05/27/2020
#
# LAST EDITED:      05/30/2020
###

from .DiscordService import DiscordService, DiscordStreamHandler

SERVICES = {
    'DISCORD': lambda config: DiscordService(config['token'])
}

STREAM_HANDLERS = {
    'DISCORD': lambda service, config: DiscordStreamHandler(
        service, config['guild'], config['channel'])
}

RECOGNIZED_SERVICES = [
    'DISCORD',
]

def getRecognizedServices():
    return RECOGNIZED_SERVICES

###############################################################################

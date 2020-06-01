###############################################################################
# NAME:             __init__.py
#
# AUTHOR:           Ethan D. Twardy <edtwardy@mtu.edu>
#
# DESCRIPTION:      Global namespace for the client module.
#
# CREATED:          05/29/2020
#
# LAST EDITED:      05/30/2020
###

from .Datagram import Datagram

CLIENTS = {
    'udp': lambda config: Datagram(config['address'], config['port']),
}

###############################################################################

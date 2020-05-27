###############################################################################
# NAME:             __init__.py
#
# AUTHOR:           Ethan D. Twardy <edtwardy@mtu.edu>
#
# DESCRIPTION:      Service module stream mapping.
#
# CREATED:          05/27/2020
#
# LAST EDITED:      05/27/2020
###

from . import Discord

streamMapping = {
    'DISCORD': Discord.DiscordFactory,
}

###############################################################################

###############################################################################
# NAME:             ServiceCommon.py
#
# AUTHOR:           Ethan D. Twardy <edtwardy@mtu.edu>
#
# DESCRIPTION:      Functionality utilized by all Services.
#
# CREATED:          05/29/2020
#
# LAST EDITED:      05/30/2020
###

import os
import psutil

def getSenderString(sender):
    proc = psutil.Process()
    if not sender:
        return f'{os.path.basename(proc.exe())},pid={proc.pid}'
    return f'{os.path.basename(proc.exe())},pid={proc.pid} ({sender})'

###############################################################################

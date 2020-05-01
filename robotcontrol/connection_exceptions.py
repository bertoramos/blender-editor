
class NotReceivedPacket(Exception):
    def __init__(self, package_type):
        Exception.__init__(self, "{0} type package has not been received".format(package_type))
        self.args = {package_type}

class InModeAlready(Exception):
    def __init__(self, mode):
        Exception.__init__(self, "it was already in {0} mode".format(mode))
        self.args = {mode}

class ModeNotSwitched(Exception):
    def __init__(self, frommode, tomode):
        Exception.__init__(self, "could not be switched from mode {0} to mode {1}".format(frommode, tomode))
        self.args = {frommode, tomode}

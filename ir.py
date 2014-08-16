import threading
import lirc

class IREventListener():

    def __init__(self, prog, lircConfig=''):

        self._thread      = None
        self._sockid      = None
        self._isListening = False

        self._commands = {}

        if lircConfig == '':
            self._sockid = lirc.init(prog)
        else:
            self._sockid = lirc.init(prog,lircConfig)

        lirc.set_blocking(False, self._sockid)

    def _wait_and_dispatch_code(self):
        while self._isListening :
            s = lirc.nextcode()
            if (s):
                try:
                    handler = self._commands[s[0]]
                    handler(self)
                except KeyError, e:
                    print "Error - no handler defined for command %s" % s[0]

    def stopListening(self):
        self._isListening = False

    def startListening(self):
        self._isListening = True
        self._thread = threading.Thread(target=self._wait_and_dispatch_code)
        self._thread.start()

    def addListener(self, command, handler):
        self._commands[command] = handler

    def removeListener(self, command):
        del self._commands[command]
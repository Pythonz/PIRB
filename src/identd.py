from pirb import c
from twisted.internet import protocol,reactor
from twisted.protocols import ident
import thread

def load(): pass

class IdentProtocol(ident.IdentServer):
	def lookup(self, serverAddress, clientAddress):
		return c.get("BOT", "username")

class IdentFactory(protocol.ServerFactory):
	protocol = IdentProtocol

if c.get("BOT", "identd") == "builtin":
	reactor.listenTCP(113, IdentFactory())
	thread.start_new_thread(reactor.run, ())

import pirb

#!/usr/bin/env python
from run import bind,put,putf,c
import thread,socket,ConfigParser

class Telnet:
	def __init__(self):
		self.ip = c.get("TELNET", "ip")
		self.port = c.get("TELNET", "port")

	def run(self):
		try:
			rc = socket.socket()
			if self.ip != "" and self.port != "":
				rc.bind((self.ip, int(self.port)))

			rc.listen(100)
			print "bound to %s:%s" % (self.ip, self.port)
			while 1:
				(client, address) = rc.accept()
				thread.start_new_thread(self.client,(client,))

			rc.close()
		except Exception,e: print(e)

	def send(self,sock,text):
		sock.send("%s\n" % text)

	def client(self,sock):
		try:
			self.send(sock,"Hello. I am %s." % c.get("BOT","username"))
			self.send(sock,"Welcome to the Telnet interface of PIRB.")
			self.send(sock,"Please enter the administrators password to unlock!")
			if str(sock.recv(100)).rstrip() == c.get("ADMIN", "password"):
				self.send(sock,"Access granted.")
			else:
				self.send(sock,"Access denied.")
				sock.close()
			while 1:
				raw = sock.recv(1024)
				data = raw.rstrip()
				if data != "":
					cmd = data.split()[0]
					if cmd == "say":
						self.send(sock,"%s" % data[4:])
					if cmd == "put":
						putf(data[4:])
						self.send(sock,"Sent: %s" % data[4:])
					elif cmd == "quit":
						self.send(sock,"Bye :(")
						sock.close()
					else:
						self.send(sock,"unknown command '%s'. try 'help'" % cmd)

		except Exception,e: print(e)

thread.start_new_thread(Telnet().run,())

import run

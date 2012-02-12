#!/usr/bin/env python
from pirb import bind,put,putf,c,printe,printa,printc,shell
import thread,socket,ConfigParser,hashlib,os,urllib2

def load(): pass

class Telnet:
	def __init__(self):
		self.ip = c.get("TELNET", "ip")
		self.port = c.get("TELNET", "port")

	def pirb(self):
		try:
			rc = socket.socket()
			if self.ip != "" and self.port != "":
				rc.bind((self.ip, int(self.port)))

			rc.listen(100)
			while 1:
				(client, address) = rc.accept()
				thread.start_new_thread(self.client,(client,))

			rc.close()
		except Exception,e:
			printe(e)
			self.pirb()

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
					cmd = data.split()[0].lower()
					if cmd == "crypt":
						sha = hashlib.sha1()
						sha.update(data[6:])
						self.send(sock,"Hash: %s" % str(sha.hexdigest()))
					elif cmd == "put":
						putf(data[4:])
						self.send(sock,"Sent: %s" % data[4:])
					elif cmd == "restart":
						if os.access("pirb.pid", os.F_OK):
							self.send(sock,"Restarting ...")
							shell("sh pirb restart")
						else: self.send(sock,"Cannot restart when debug is running")
					elif cmd == "update":
						_file = open("version", "r")
						_old = _file.read()
						_file.close()
						_web = urllib2.urlopen("https://raw.github.com/Pythonz/PIRB/master/version")
						_new = _web.read()
						_web.close()
						if _old != _new:
							self.send(sock, "{0} -> {1}".format(_old, _new))
							__cache = 0
							for doc in os.listdir("database/updates/cache"):
								__cache += 1
							__chan = 0
							for doc in os.listdir("database/updates/chan"):
								__chan += 1
							__user = 0
							for doc in os.listdir("database/updates/user"):
								__user += 1
							shell("git add .")
							shell("git rm --cached database/*.db")
							shell("git commit -m 'Save'")
							shell("git pull")
							___cache = 0
							for doc in os.listdir("database/updates/cache"):
								___cache += 1
								if __cache < ___cache:
									self.send(sock, " - Insert 'cache/{0}'".format(doc))
									shell("sqlite3 database/cache.db < database/updates/cache/{0}".format(doc))
							___chan = 0
							for doc in os.listdir("database/updates/chan"):
								___chan += 1
								if __chan < ___chan:
									self.send(sock, " - Insert 'chan/{0}'".format(doc))
									shell("sqlite3 database/chan.db < database/updates/chan/{0}".format(doc))
							___user = 0
							for doc in os.listdir("database/updates/user"):
								___user += 1
								if __user < ___user:
									self.send(sock, " - Insert 'user/{0}'".format(doc))
									shell("sqlite3 database/user.db < database/updates/user/{0}".format(doc))
							put("QUIT :Updating...")
							sock.close()
							shell("sh pirb restart")
						else: self.send(sock, "No update available.")
					elif cmd == "version":
						file = open("version", "r")
						self.send(sock, "PIRB "+file.read())
						file.close()
					elif cmd == "quit":
						self.send(sock,"Bye :(")
						sock.close()
					elif cmd == "die":
						if os.access("pirb.pid", os.F_OK):
							shell("sh pirb stop")
						else: sys.exit(2)
					elif cmd == "help":
						tbl = list()
						tbl.append("help")
						tbl.append("crypt")
						tbl.append("put")
						tbl.append("restart")
						tbl.append("update")
						tbl.append("version")
						tbl.append("die")
						tbl.append("quit")
						for command in tbl:
							self.send(sock, command.upper())
					else:
						self.send(sock,"unknown command '%s'. try 'HELP'" % cmd.upper())

		except Exception,e: printe(e)

thread.start_new_thread(Telnet().pirb,())

import pirb

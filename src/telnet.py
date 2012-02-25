#!/usr/bin/env python
from pirb import bind,put,putf,c,printe,printa,printc,shell
import thread,socket,ConfigParser,hashlib,os,urllib2,sys,sqlite3

def load(): pass

class Telnet:
	def __init__(self):
		self.ip = c.get("TELNET", "ip")
		self.port = c.get("TELNET", "port")

	def pirb(self):
		try:
			if c.getboolean("SERVER", "ipv6"):
				rc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			else:
				rc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			rc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			if self.ip != "" and self.port != "":
				rc.bind((self.ip, int(self.port)))

			rc.listen(100)
			while 1:
				(client, address) = rc.accept()
				thread.start_new_thread(self.client,(client,address[0],rc))

			rc.close()
		except Exception,e:
			printe(e)

	def send(self,sock,text):
		sock.send("%s\n" % text)


	def client(self,sock,addr,servsock):
		try:
			printc("!! conntected with "+addr+" !!")
			self.send(sock,"Hello. I am %s." % c.get("BOT","username"))
			self.send(sock,"Welcome to the remote interface of PIRB.")
			self.send(sock,"Please enter the administrators password to unlock!")
			if str(sock.recv(100)).rstrip() == c.get("ADMIN", "password"):
				self.send(sock,"Access granted.")
				printc("!! "+addr+" logged in !!")
			else:
				self.send(sock,"Access denied.")
				printc("!! "+addr+" failed login !!")
				sock.close()
			while 1:
				raw = sock.recv(1024)
				data = raw.rstrip()
				if not data:
					printc("!! losed connection with "+addr+ " !!")
					sock.close()
				if data:
					cmd = data.split()[0].lower()
					if cmd == "crypt":
						sha = hashlib.sha1()
						sha.update(data[6:])
						self.send(sock,"Hash: %s" % str(sha.hexdigest()))
					elif cmd == "put":
						put(data[4:])
						self.send(sock,"Sent: %s" % data[4:])
					elif cmd == "restart":
						if os.access("pirb.pid", os.F_OK):
							self.send(sock,"Restarting ...")
							servsock.close()
							sock.close()
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
							__cache = len(os.listdir("database/updates/cache"))
							__chan = len(os.listdir("database/updates/chan"))
							__user = len(os.listdir("database/updates/user"))
							shell("git add .")
							shell("git rm --cached database/*.db")
							shell("git commit -m 'Save'")
							shell("git pull")
							___cache = os.listdir("database/updates/cache")
							if __cache < len(___chache):
								while __cache != len(___cache):
									__cache += 1
									for sql in ___cache:
										if sql.startswith(str(__cache)+"_"):
											self.send(sock, " - Insert 'cache/{0}'".format(sql))
											shell("sqlite3 database/cache.db < database/updates/cache/{0}".format(sql))
							___chan == os.listdir("database/updates/chan")
							if __chan < len(___chan):
								while __chan != len(___chan):
									__chan += 1
									for sql in ___chan:
										if sql.startswith(str(__chan)+"_"):
											self.send(sock, " - Insert 'chan/{0}'".format(sql))
											shell("sqlite3 database/chan.db < database/updates/chan/{0}".format(sql))
							___user == os.listdir("database/updates/user")
							if __user < len(___user):
								while __user != len(___user):
									__user += 1
									for sql in ___user:
										if sql.startswith(str(__user)+"_"):
											self.send(sock, " - Insert 'user/{0}'".format(sql))
											shell("sqlite3 database/user.db < database/updates/user/{0}".format(sql))
							put("QUIT :Updating...")
							servsock.close()
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
						servsock.close()
						sock.close()
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

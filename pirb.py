#!/usr/bin/env python

import sys
import socket
import string
import os
import sqlite3
import thread
import ConfigParser
import urllib2
import subprocess
import __builtin__
import time
import traceback
import ssl
import inspect

__app__ = "PIRB"

sys.path.append(".")
sys.path.append("modules")
sys.path.append("src")

def printa(text):
	if text:
		print "\033[1m\033[34m[" + time.strftime("%H:%M", time.localtime()) + "] " + str(text) + "\033[0m"

def printc(text):
	if text:
		print "\033[1m\033[32m[" + time.strftime("%H:%M", time.localtime()) + "] " + str(text) + "\033[0m"

def printe(text):
	if c.getboolean("BOT", "debug"):
		print "\033[1m\033[31m[" + time.strftime("%H:%M", time.localtime()) + "] " + str(text) + "\033[0m"

c = ConfigParser.RawConfigParser()
c.read("configs/main.conf")

_ip = 0
lasterror = None

def shell(text):
	subprocess.Popen(text+" >> /dev/null", shell=True).wait()

def fclean(name):
	f = open(name, "wb")
	f.write("")
	f.close()

def fwrite(name,text):
	f = open(name, "ab")
	f.write(text+"\n")
	f.close()

def bind(function,event,command=""):
	frame = inspect.stack()[1]
	module = inspect.getmodule(frame[0])
	_cache.execute("insert into binds values ('%s','%s','%s','%s')" % (function,module.__name__,event,command))

def put(arg):
	try:
		_cache.execute("insert into put_query values (NULL, '%s')" % arg.replace("\'", "\\'"))
	except Exception,e: printe(e)
	except KeyboardInterrupt: printe("\nAborting ... CTRL + C")

def putf(arg):
	try:
		s.send(arg.rstrip()+"\n")
		printa(arg.rstrip())
	except Exception,e: printe(e)
	except KeyboardInterrupt: printe("\nAborting ... CTRL + C")

def whois(nick):
	if c.get("SERVER", "address").lower().endswith(".quakenet.org"):
		putf("WHO %s %snat,111" % (nick, "%"))
	else:
		putf("WHOIS %s" % nick)

def whochan(channel):
	if c.get("SERVER", "address").lower().endswith(".quakenet.org"):
		putf("WHO %s %snat,111" % (channel, "%"))
		putf("WHO %s" % channel)
	else:
		putf("WHO %s" % channel)

def keepnick():
	try:
		time.sleep(60)
		_here = sqlite3.connect("database/cache.db")
		_here.isolation_level = None
		for data in _here.execute("select name from botnick"):
			if _botnick != str(data[0]):
				_here.execute("update botnick set name='%s'" % _botnick)
				put("NICK %s" % _botnick)
		_here.close()
		thread.start_new_thread(keepnick, ())
	except Exception,e: printe(e)
	except KeyboardInterrupt:
		printe("\nAborting ... CTRL + C")
		sys.exit(2)

def disconnect():
	try:
		s.close()
		_userdb.close()
		_chandb.close()
		_cache.close()
		printa("connection closed")
		printa("reconnecting in "+c.get("SERVER", "reconnect")+" seconds")
		time.sleep(int(c.get("SERVER", "reconnect")))
		main()
	except Exception,e: printe(e)
	except socket.error: pass
	except KeyboardInterrupt:
		printe("\nAborting ... CTRL + C")
		sys.exit(2)

def put_query():
	try:
		_db = sqlite3.connect("database/cache.db")
		_db.isolation_level = None
		_db.execute("delete from put_query")
		while 1:
			for data in _db.execute("select id,message from put_query"):
				putf(data[1])
				_db.execute("delete from put_query where id = '%s'" % data[0])
				time.sleep(1)
		_db.close()
	except Exception,e: printe(e)
	except socket.error: pass
	except KeyboardInterrupt:
		printe("\nAborting ... CTRL + C")
		sys.exit(2)

def main():
	c.read("configs/main.conf")
	global _ip
	global lasterror
	__builtin__._botnick = c.get("BOT", "nick")
	__builtin__._cache = sqlite3.connect("database/cache.db")
	_cache.isolation_level = None
	_cache.execute("delete from src")
	_cache.execute("delete from modules")
	_cache.execute("delete from binds")
	_cache.execute("delete from botnick")
	_cache.execute("insert into botnick values ('%s')" % _botnick)
	__builtin__._userdb = sqlite3.connect("database/user.db")
	_userdb.isolation_level = None
	_userdb.execute("delete from auth")
	__builtin__._chandb = sqlite3.connect("database/chan.db")
	_chandb.isolation_level = None
	if c.getboolean("SERVER", "ipv6") and socket.has_ipv6:
		if c.getboolean("SERVER", "ssl"):
			__builtin__.s = ssl.wrap_socket(socket.socket(socket.AF_INET6, socket.SOCK_STREAM))
		else:
			__builtin__.s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
	else:
		if c.getboolean("SERVER", "ssl"):
			__builtin__.s = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
		else:
			__builtin__.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		for source in os.listdir("src"):
			if source != "__init__.py" and source.endswith(".py"):
				exec("import src.%s" % source.split(".py")[0])
				exec("src.%s.load()" % source.split(".py")[0])
				_cache.execute("insert into src values ('%s')" % source.split(".py")[0])
				printa("src %s loaded" % source.split(".py")[0])
		for mod in os.listdir("modules"):
			if mod != "__init__.py" and mod.endswith(".py"):
				exec("import modules.%s" % mod.split(".py")[0])
				exec("modules.%s.load()" % mod.split(".py")[0])
				_cache.execute("insert into modules values ('%s')" % mod.split(".py")[0])
				printa("module %s loaded" % mod.split(".py")[0])
		if c.get("SERVER", "bind") != "":
			s.bind((c.get("SERVER", "bind").split()[_ip], 0))
			printa("binding to ip '{0}'".format(c.get("SERVER", "bind").split()[_ip]))
			_ip += 1
			if len(c.get("SERVER", "bind").split()) == _ip:
				_ip = 0
		if c.get("BOT", "identd") == "oidentd":
			identfile = os.environ['HOME']+"/.oidentd.conf"
			file = open(identfile, "r")
			content = file.read()
			file.close()
			file = open(identfile, "w")
			file.write('global { reply "%s" }' % c.get("BOT", "username"))
			file.close()
		s.connect((c.get("SERVER", "address"), int(c.get("SERVER", "port"))))
		putf('NICK '+_botnick)
		putf('USER '+c.get("BOT", "username")+' '+socket.getfqdn(c.get("SERVER", "address"))+' MechiSoft :'+c.get("BOT", "realname"))
		thread.start_new_thread(keepnick, ())
		thread.start_new_thread(put_query, ())
	except Exception:
		et, ev, tb = sys.exc_info()
		e = "{0} {1} (Line #{2})".format(et, ev, traceback.tb_lineno(tb))
		if e != lasterror:
			lasterror = e
			printe(e)
	except KeyboardInterrupt:
		printe("\nAborting ... CTRL + C")
		sys.exit(2)
	while 1:
		try:
			line=s.recv(8096)
			if not line:
				disconnect()
				return 0
			for line in line.splitlines():
				reg = line.rstrip()
				printc(line.rstrip())
				if line.split()[1] == "001":
					if c.get("BOT", "identd") == "oidentd":
						file = open(identfile, "w")
						file.write(content)
						file.close()
				if line.split()[1] == ":Closing":
					disconnect()
					return 0
				if line.split()[0]=='PING':
					putf('PONG '+line[5:])
				line = line.rstrip()[1:]
				if line.split()[1].lower() == "privmsg":
					nick = line.split("!")[0]
					uhost = line.split("!")[1].split()[0]
					target = line.split()[2]
					arg = ' '.join(line.split()[3:])[0:][1:]
					cmd = line.split()[3][1:]
					if arg.split()[0].lower() == "reload" and line.split()[2][0] != "#":
						if src.user.getauth(nick).lower() == c.get("ADMIN", "auth").lower() or arg.split()[1] == c.get("ADMIN", "password"):
							putf("NOTICE " + nick + " :Reloading ...")
							c.read("configs/main.conf")
							_cache.execute("delete from binds")
							for loaded in _cache.execute("select name from src"):
								loaded = loaded[0]
								if not os.access("src/%s.py" % loaded, os.F_OK):
									exec("del src.%s" % loaded)
									exec("""del sys.modules["src.%s"]""" % loaded)
									_cache.execute("delete from src where name='%s'" % loaded)
									printa("src %s unloaded" % loaded)
							for source in os.listdir("src"):
								if source != "__init__.py" and source.endswith(".py"):
									name = source.split(".py")[0]
									entry = False
									for loaded in _cache.execute("select name from src where name='%s'" % name):
										entry = True
									if entry is False:
										exec("import src.%s" % name)
										exec("src.%s.load()" % name)
										_cache.execute("insert into src values ('%s')" % name)
										printa("src %s loaded" % name)
									else:
										exec("reload(src.%s)" % name)
										exec("src.%s.load()" % name)
										printa("src %s reloaded" % name)
							for loaded in _cache.execute("select name from modules"):
								loaded = loaded[0]
								if not os.access("modules/%s.py" % loaded, os.F_OK):
									exec("del modules.%s" % loaded)
									exec("""del sys.modules["modules.%s"]""" % loaded)
									_cache.execute("delete from modules where name='%s'" % loaded)
									printa("module %s unloaded" % loaded)
							for source in os.listdir("modules"):
								if source != "__init__.py" and source.endswith(".py"):
									name = source.split(".py")[0]
									entry = False
									for loaded in _cache.execute("select name from modules where name='%s'" % name):
										entry = True
									if entry is False:
										exec("import modules.%s" % name)
										exec("modules.%s.load()" % name)
										_cache.execute("insert into modules values ('%s')" % name)
										printa("module %s loaded" % name)
									else:
										exec("reload(modules.%s)" % name)
										exec("modules.%s.load()" % name)
										printa("module %s reloaded" % name)
							putf("NOTICE " + nick + " :Done.")
					if arg.split()[0].lower() == "restart" and line.split()[2][0] != "#":
						if src.user.getauth(nick) == c.get("ADMIN", "auth") or arg.split()[1] == c.get("ADMIN", "password"):
							putf("QUIT :Restart ... I\'ll be back in %s seconds!" % c.get("SERVER", "reconnect"))
							disconnect()
							return 0
					for hookconfig in _cache.execute("select * from binds"):
						hook = str(hookconfig[0])
						module = str(hookconfig[1])
						event = str(hookconfig[2])
						command = str(hookconfig[3])
						if event == "pub" and target.startswith("#"):
 							if command != "" and cmd.lower() == command.lower():
								exec("""%s.%s("%s","%s","%s","%s")""" % (module, hook, nick, uhost, target, ' '.join(arg.split()[1:])))
							elif command == "":
								exec("""%s.%s("%s","%s","%s","%s")""" % (module, hook, nick, uhost, target, arg))
						if event == "msg" and not target.startswith("#"):
							if command != "" and cmd.lower() == command.lower():
								exec("""%s.%s("%s","%s","%s")""" % (module, hook, nick, uhost, ' '.join(arg.split()[1:])))
							elif command == "":
								exec("""%s.%s("%s","%s","%s")""" % (module, hook, nick, uhost, arg))
				elif line.split()[1].lower() == "notice" and line.split()[0].find("!") != -1 and line.split()[0].find("@") != -1:
					nick = line.split("!")[0]
					uhost = line.split("!")[1].split()[0]
					target = line.split()[2]
					arg = ' '.join(line.split()[3:])[0:][1:]
					cmd = line.split()[3][1:]
					for hookconfig in _cache.execute("select * from binds"):
						hook = str(hookconfig[0])
						module = str(hookconfig[1])
						event = str(hookconfig[2])
						command = str(hookconfig[3])
						if event == "not":
							if command != "" and cmd.lower() == command.lower():
								exec("""%s.%s("%s","%s","%s","%s")""" % (module, hook, nick, uhost, target, ' '.join(arg.split()[1:])))
							elif command == "":
								exec("""%s.%s("%s","%s","%s","%s")""" % (module, hook, nick, uhost, target, arg))
				for hookconfig in _cache.execute("select * from binds"):
					hook = str(hookconfig[0])
					module = str(hookconfig[1])
					event = str(hookconfig[2])
					command = str(hookconfig[3])
					if event == "raw":
						cmdo = line.split()[1]
						if command != "" and cmdo.lower() == command.lower():
							exec("""%s.%s("%s")""" % (module, hook, reg))
						elif command == "":
							exec("""%s.%s("%s")""" % (module, hook, reg))
		except Exception:
			et, ev, tb = sys.exc_info()
			e = "{0} {1} (Line #{2})".format(et, ev, traceback.tb_lineno(tb))
			if e != lasterror:
				lasterror = e
				printe(e)
		except socket.error:
			disconnect()
			return 0
		except KeyboardInterrupt:
			printe("\nAborting ... CTRL + C")
			sys.exit(2)

if __name__ == '__main__':
	try:
		if len(sys.argv) != 1:
			if sys.argv[1].lower() == "database":
				shell("sqlite3 database/cache.db < database/cache.sql")
				shell("sqlite3 database/chan.db < database/chan.sql")
				shell("sqlite3 database/user.db < database/user.sql")
				print("Databases created")
			if sys.argv[1].lower() == "configure":
				cadd = "\033[1m\033[34m"
				cdel = "\033[0m"
				c = ConfigParser.RawConfigParser()
				printc("Welcome to the Configuring interface! Let's make it easy to use this bot.")
				printc("Loading configuration options into cache :)")
				c.add_section("SERVER")
				c.add_section("BOT")
				c.add_section("ADMIN")
				c.add_section("SERVICES")
				c.add_section("TELNET")
				printc("So lets configure the server settings first:")
				c.set("SERVER", "address", raw_input(cadd+"Address: "+cdel))
				c.set("SERVER", "port", raw_input(cadd+"Port: "+cdel))
				c.set("SERVER", "reconnect", raw_input(cadd+"Time to wait before reconnect: "+cdel))
				c.set("SERVER", "bind", raw_input(cadd+"IP to bind to (leave it blank when you don't need it): "+cdel))
				c.set("SERVER", "ipv6", raw_input(cadd+"IPv6 (True/False): "+cdel))
				c.set("SERVER", "ssl", raw_input(cadd+"SSL (True/False): "+cdel))
				printc("So now the server settings are ready. Lets go to bot settings:")
				c.set("BOT", "nick", raw_input(cadd+"Nick: "+cdel))
				c.set("BOT", "username", raw_input(cadd+"Username (ident): "+cdel))
				c.set("BOT", "realname", raw_input(cadd+"Realname: "+cdel))
				c.set("BOT", "channels", raw_input(cadd+"Channels to join on startup (seperate with ,): "+cdel))
				c.set("BOT", "debug", raw_input(cadd+"Debug (True/False): "+cdel))
				c.set("BOT", "identd", raw_input(cadd+"Identd (None/pyidentd/oidentd): "+cdel))
				printc("So lets go to the management... The admin settings:")
				c.set("ADMIN", "password", raw_input(cadd+"Password to use admin commands: "+cdel))
				c.set("ADMIN", "auth", raw_input(cadd+"Auth (nickserv nick or quakenet auth, replaces password at some commands): "+cdel))
				printc("So now we need just two more. The services settings:")
				c.set("SERVICES", "nickserv", raw_input(cadd+"NickServ password: "+cdel))
				c.set("SERVICES", "quakenet", raw_input(cadd+"QuakeNet Auth (format: authname password): "+cdel))
				printc("At least, we have to configure the telnet connection for management:")
				c.set("TELNET", "ip", raw_input(cadd+"IP to bind (0.0.0.0 to bind to all ips): "+cdel))
				c.set("TELNET", "port", raw_input(cadd+"Port to bind: "+cdel))
				printc("That was all :)")
				printc("Writing config now...")
				with open("configs/main.conf", "wb") as configfile:
					c.write(configfile)
				printc("Config file written :)")
				printc("Run '%s' to start me :D" % sys.argv[0])
			if sys.argv[1].lower() == "-h" or sys.argv[1].lower() == "--help":
				printa(sys.argv[0]+" database		creates new databases")
				printa(sys.argv[0]+" configure		config maker")
		else:
			main()
	except Exception:
		et, ev, tb = sys.exc_info()
		e = "{0} {1} (Line #{2})".format(et, ev, traceback.tb_lineno(tb))
		printe(e)
	except KeyboardInterrupt: printe("\nAborting ... CTRL + C")
	sys.exit(2)

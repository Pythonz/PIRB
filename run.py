#!/usr/bin/env python

import sys, socket, string, os, sqlite3, thread, ConfigParser, __builtin__
from time import sleep,strftime,localtime

__app__ = "PIRB"

sys.path.append(".")
sys.path.append("modules")
sys.path.append("src")

def printa(text):
	if text:
		print "\033[1m\033[34m[" + strftime("%H:%M", localtime()) + "] " + str(text) + "\033[0m"

def printc(text):
	if text:
		print "\033[1m\033[32m[" + strftime("%H:%M", localtime()) + "] " + str(text) + "\033[0m"

def printe(text):
	if c.getboolean("BOT", "debug"):
		print "\033[1m\033[31m[" + strftime("%H:%M", localtime()) + "] " + str(text) + "\033[0m"

c = ConfigParser.RawConfigParser()
c.read("configs/main.conf")

def mail(arg):
 try:
	s.send(arg.rstrip()+"\n")
	printa(arg.rstrip())
 except: pass

def fclean(name):
	f = open(name, "wb")
	f.write("")
	f.close()

def fwrite(name,text):
	f = open(name, "ab")
	f.write(text+"\n")
	f.close()

def bind(function,module,event,command=""):
	_cache.execute("insert into binds values ('%s','%s','%s','%s')" % (function,module,event,command))

def put(arg):
	try:
		s.send(arg.rstrip()+"\n")
		printa(arg.rstrip())
		sleep(1)
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
		sleep(60)
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
		sleep(int(c.get("SERVER", "reconnect")))
		main()
	except Exception,e: printe(e)
	except socket.error: pass
	except KeyboardInterrupt:
		printe("\nAborting ... CTRL + C")
		sys.exit(2)

def main():
	global s
	global _botnick
	global _cache
	global _userdb
	global _chandb
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
	__builtin__.s = socket.socket()
	try:
		for source in os.listdir("src"):
			if source != "__init__.py" and source.endswith(".py"):
				exec("from src import %s as src_%s" % (source.split(".py")[0],source.split(".py")[0]))
				_cache.execute("insert into src values ('%s')" % source.split(".py")[0])
				printa("src %s loaded" % source.split(".py")[0])
		for mod in os.listdir("modules"):
			if mod != "__init__.py" and mod.endswith(".py"):
				exec("from modules import %s" % mod.split(".py")[0])
				_cache.execute("insert into modules values ('%s')" % mod.split(".py")[0])
				printa("module %s loaded" % mod.split(".py")[0])
		if c.get("SERVER", "bind") != "":
			s.bind((c.get("SERVER", "bind"), 0))
		s.connect((c.get("SERVER", "address"), int(c.get("SERVER", "port"))))
		mail('NICK '+_botnick)
		mail('USER '+c.get("BOT", "username")+' '+c.get("SERVER", "address")+' MechiSoft :'+c.get("BOT", "realname"))
		thread.start_new_thread(keepnick, ())
	except Exception,e: printe(e)
	except KeyboardInterrupt:
		printe("\nAborting ... CTRL + C")
		sys.exit(2)
	while 1:
		try:
			line=s.recv(8096)
			if not line:
				disconnect()
				return 0
			for line in line.rstrip().split("\n"):
				reg = line.rstrip()
				printc(line.rstrip())
				if line.split()[1] == ":Closing":
					disconnect()
					return 0
				if line.split()[0]=='PING':
					mail('PONG '+line[5:])
				line = line.rstrip()[1:]
				if line.split()[1].lower() == "privmsg":
					nick = line.split("!")[0]
					uhost = line.split("!")[1].split()[0]
					target = line.split()[2]
					arg = ' '.join(line.split()[3:])[0:][1:]
					cmd = line.split()[3][1:]
					if arg.split()[0].lower() == "binds" and line.split()[2][0] != "#":
						if src_user.getauth(nick).lower() == c.get("ADMIN", "auth").lower() or arg.split()[1] == c.get("ADMIN", "password"):
							for binds in _cache.execute("select * from binds"):
								put("NOTICE %s :[BIND] Function: %s, Module: %s, Event: %s, Command: %s" % (nick,str(binds[0]),str(binds[1]),str(binds[2]),str(binds[3])))
					if arg.split()[0].lower() == "loaded" and line.split()[2][0] != "#":
						if src_user.getauth(nick).lower() == c.get("ADMIN", "auth").lower() or arg.split()[1] == c.get("ADMIN", "password"):
							load = list()
							for loaded in _cache.execute("select name from src"):
								load.append(loaded[0])
							put("NOTICE %s :[src] %s" % (nick,', '.join(load)))
							load = list()
							for loaded in _cache.execute("select name from modules"):
								load.append(loaded[0])
							put("NOTICE %s :[module] %s" % (nick,', '.join(load)))
					if arg.split()[0].lower() == "reload" and line.split()[2][0] != "#":
						if src_user.getauth(nick).lower() == c.get("ADMIN", "auth").lower() or arg.split()[1] == c.get("ADMIN", "password"):
							c.read("configs/main.conf")
							put("NOTICE %s :[run] config reloaded" % nick)
							_cache.execute("delete from binds")
							src_load = list()
							src_reload = list()
							src_unload = list()
							mod_load = list()
							mod_reload = list()
							mod_unload = list()
							for loaded in _cache.execute("select name from src"):
								loaded = loaded[0]
								if not os.access("src/%s.py" % loaded, os.F_OK):
									src_unload.append(loaded)
									exec("del src_%s" % loaded)
									_cache.execute("delete from src where name='%s'" % loaded)
									printa("src %s unloaded" % loaded)
							put("NOTICE %s :[src] %s unloaded" % (nick,', '.join(src_unload)))
							for source in os.listdir("src"):
								if source != "__init__.py" and source.endswith(".py"):
									name = source.split(".py")[0]
									entry = False
									for loaded in _cache.execute("select name from src where name='%s'" % name):
										entry = True
									if entry is False:
										src_load.append(name)
										exec("from src import %s as src_%s" % (name,name))
										_cache.execute("insert into src values ('%s')" % name)
										printa("src %s loaded" % name)
									else:
										src_reload.append(name)
										exec("reload(src_%s)" % name)
										printa("src %s reloaded" % name)
							put("NOTICE %s :[src] %s loaded" % (nick,', '.join(src_load)))
							put("NOTICE %s :[src] %s reloaded" % (nick,', '.join(src_reload)))
							for loaded in _cache.execute("select name from modules"):
								loaded = loaded[0]
								if not os.access("modules/%s.py" % loaded, os.F_OK):
									mod_unload.append(loaded)
									exec("del %s" % loaded)
									_cache.execute("delete from modules where name='%s'" % loaded)
									printa("module %s unloaded" % loaded)
							put("NOTICE %s :[module] %s unloaded" % (nick,', '.join(mod_unload)))
							for source in os.listdir("modules"):
								if source != "__init__.py" and source.endswith(".py"):
									name = source.split(".py")[0]
									entry = False
									for loaded in _cache.execute("select name from modules where name='%s'" % name):
										entry = True
									if entry is False:
										mod_load.append(name)
										exec("from modules import %s" % name)
										_cache.execute("insert into modules values ('%s')" % name)
										printa("module %s loaded" % name)
									else:
										mod_reload.append(name)
										exec("reload(%s)" % name)
										printa("module %s reloaded" % name)
							put("NOTICE %s :[module] %s loaded" % (nick,', '.join(mod_load)))
							put("NOTICE %s :[module] %s reloaded" % (nick,', '.join(mod_reload)))
					if arg.split()[0].lower() == "restart" and line.split()[2][0] != "#":
						if src_user.getauth(nick) == c.get("ADMIN", "auth") or arg.split()[1] == c.get("ADMIN", "password"):
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
		except Exception,e: printe(e)
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
				_user = sqlite3.connect("database/user.db")
				_user.isolation_level = None
				_chan = sqlite3.connect("database/chan.db")
				_chan.isolation_level = None
				_cache = sqlite3.connect("database/cache.db")
				_cache.isolation_level = None
				print("Created user, channel and cache databases...")
				print("Now im going to create the needed tables")
				_user.execute("create table auth(nick text, auth text)")
				_chan.execute("create table list(channel text)")
				_chan.execute("create table channel(channel text, auth text, flags text)")
				_chan.execute("create table info(channel text, topic text, modes text)")
				_chan.execute("create table bans(channel text, ban text)")
				_chan.execute("create table exempts(channel text, exempt text)")
				_cache.execute("create table src(name text)")
				_cache.execute("create table modules(name text)")
				_cache.execute("create table binds(name text, module text, event text, command text)")
				_cache.execute("create table botnick(name text)")
				print("All tables in databases created ... Closing connection now")
				_user.close()
				_chan.close()
				_cache.close()
				print("Databases have been restored. You can run me now.")
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
				printc("So now the server settings are ready. Lets go to bot settings:")
				c.set("BOT", "nick", raw_input(cadd+"Nick: "+cdel))
				c.set("BOT", "username", raw_input(cadd+"Username (ident): "+cdel))
				c.set("BOT", "realname", raw_input(cadd+"Realname: "+cdel))
				c.set("BOT", "channels", raw_input(cadd+"Channels to join on startup (seperate with ,): "+cdel))
				c.set("BOT", "debug", raw_input(cadd+"Debug (True/False): "+cdel))
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
	except Exception,e: printe(e)
	except KeyboardInterrupt: printe("\nAborting ... CTRL + C")
	sys.exit(2)

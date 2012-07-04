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
import base64
import fnmatch
from apscheduler.scheduler import Scheduler

__app__ = "PIRB"

sys.path.append(".")
sys.path.append("modules")
sys.path.append("src")

def printa(text):
	if text:
		print("[" + time.strftime("%H:%M", time.localtime()) + "] \033[1m\033[34m*\033[0m " + str(text))

def printc(text):
	if text:
		print("[" + time.strftime("%H:%M", time.localtime()) + "] \033[1m\033[32m*\033[0m " + str(text))

def printe(text):
	if c.getboolean("BOT", "debug"):
		print("[" + time.strftime("%H:%M", time.localtime()) + "] \033[1m\033[31m*\033[0m " + str(text))

c = ConfigParser.RawConfigParser()
c.read("configs/main.conf")

_ip = 0
lasterror = None

def encode(text):
	return base64.encodestring(text).rstrip()

def decode(text):
	return base64.decodestring(text).rstrip()

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
		open(".put_query", "a").write(arg+"\n")
	except Exception,e:
		printe(e)
	except KeyboardInterrupt:
		printe("\nAborting ... CTRL + C")

def putf(arg):
	try:
		s.send(arg.rstrip()+"\n")
		printa(arg.rstrip())
	except Exception,e:
		printe(e)
	except KeyboardInterrupt:
		printe("\nAborting ... CTRL + C")


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

def botnick():
	for data in _cache.execute("select name from botnick"):
		return str(data[0])

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
	except Exception,e:
		printe(e)
	except KeyboardInterrupt:
		printe("\nAborting ... CTRL + C")
		sys.exit(2)

def disconnect():
	try:
		_timer.shutdown()
		s.close()
		_userdb.close()
		_chandb.close()
		_cache.close()
		printa("connection closed")
		printa("reconnecting in "+c.get("SERVER", "reconnect")+" seconds")
		time.sleep(int(c.get("SERVER", "reconnect")))
		main()
	except Exception,e:
		printe(e)
	except socket.error:
		pass
	except KeyboardInterrupt:
		printe("\nAborting ... CTRL + C")
		sys.exit(2)

def put_query():
	try:
		open(".put_query", "w").write("")
		printa("put_query data cleared.")
		data = open(".put_query", "r")
		printa("put_query worker started.")

		while 1:
			for line in data.readlines():
				putf(line.rstrip())
				time.sleep(c.getint("BOT", "query_time"))

			time.sleep(1)

		data.close()
		printa("put_query worker has been interrupted.")
		thread.start_new_thread(put_query, ())
		printa("Started new put_query-thread.")
	except Exception,e:
		printe(str(e))
		thread.start_new_thread(put_query, ())
		printa("Started put_query-thread.")
	except socket.error,e:
		print(str(e))
		thread.start_new_thread(put_query, ())
		printa("Started put_query-thread.")
	except KeyboardInterrupt:
		printe("\nAborting ... CTRL + C")
		sys.exit(2)

def scheduler_action():
	printa("Executing cron tasks.")

def scheduler_thread(event):
	try:
#		_cache = sqlite3.connect("database/cache.db")
#		_cache.isolation_level = None
#		_userdb = sqlite3.connect("database/user.db")
#		_userdb.isolation_level = None
#		_chandb = sqlite3.connect("database/chan.db")
#		_chandb.isolation_level = None
		time_minute = time.strftime("%M", time.localtime())
		time_hour = time.strftime("%H", time.localtime())
		time_day = time.strftime("%d", time.localtime())
		time_month = time.strftime("%m", time.localtime())
		time_year = time.strftime("%y", time.localtime())

		for hookconfig in _cache.execute("select name,module,command from binds where event == 'time'"):
			hook = str(hookconfig[0])
			module = str(hookconfig[1])
			command = str(hookconfig[2])

			if command != "":
				times = command.split()

				if len(times) == 1:
					if fnmatch.fnmatch(time_minute, command):
						exec("""%s.%s("%s", "%s", "%s", "%s", "%s")""" % (module, hook, time_minute, time_hour, time_day, time_month, time_year))
				elif len(times) == 2:
					if fnmatch.fnmatch(time_minute + " " + time_hour, command):
						exec("""%s.%s("%s", "%s", "%s", "%s", "%s")""" % (module, hook, time_minute, time_hour, time_day, time_month, time_year))
				elif len(times) == 3:
					if fnmatch.fnmatch(time_minute + " " + time_hour + " " + time_day, command):
						exec("""%s.%s("%s", "%s", "%s", "%s", "%s")""" % (module, hook, time_minute, time_hour, time_day, time_month, time_year))
				elif len(times) == 4:
					if fnmatch.fnmatch(time_minute + " " + time_hour + " " + time_day + " " + time_month, command):
						exec("""%s.%s("%s", "%s", "%s", "%s", "%s")""" % (module, hook, time_minute, time_hour, time_day, time_month, time_year))
				elif len(times) == 5:
					if fnmatch.fnmatch(time_minute + " " + time_hour + " " + time_day + " " + time_month + " " + time_year, command):
						exec("""%s.%s("%s", "%s", "%s", "%s", "%s")""" % (module, hook, time_minute, time_hour, time_day, time_month, time_year))
#
#		_cache.close()
#		_userdb.close()
#		_chandb.close()
	except Exception,e:
		printe(str(e))
	except socket.error,e:
		print(str(e))
	except KeyboardInterrupt:
		printe("\nAborting ... CTRL + C")
		sys.exit(2)

def main():
	c.read("configs/main.conf")
	global _ip
	global lasterror
	global _timer
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
	_timer = Scheduler()
	_timer.add_cron_job(scheduler_action, second=0)
	_timer.add_listener(scheduler_thread)
	_timer.start()

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
		src_counter = 0

		for source in os.listdir("src"):
			if source != "__init__.py" and source.endswith(".py"):
				exec("import src.%s" % source.split(".py")[0])
				exec("src.%s.load()" % source.split(".py")[0])
				_cache.execute("insert into src values ('%s')" % source.split(".py")[0])
				src_counter += 1
				printa("src %s loaded" % source.split(".py")[0])

		printa("Loaded {0} sources.".format(src_counter))
		mod_counter = 0

		for mod in os.listdir("modules"):
			if mod != "__init__.py" and mod.endswith(".py"):
				exec("import modules.%s" % mod.split(".py")[0])
				exec("modules.%s.load()" % mod.split(".py")[0])
				_cache.execute("insert into modules values ('%s')" % mod.split(".py")[0])
				mod_counter += 1
				printa("module %s loaded" % mod.split(".py")[0])

		printa("Loaded {0} modules.".format(mod_counter))

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
	except Exception:
		et, ev, tb = sys.exc_info()
		e = "{0} {1} (Line #{2})".format(et, ev, traceback.tb_lineno(tb))

		if e != lasterror:
			lasterror = e
			printe(e)
	except KeyboardInterrupt:
		printe("\nAborting ... CTRL + C")
		sys.exit(2)

	while True:
		try:
			line=s.recv(102400)

			if not line:
				disconnect()
				return 0

			for line in line.splitlines():
				if len(line.split()) > 1:
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

					if line.split()[0] == 'PING':
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
								put("NOTICE " + nick + " :Reloading ...")
								c.read("configs/main.conf")
								__builtin__._botnick = c.get("BOT", "nick")
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

								put("NOTICE " + nick + " :Done.")
						elif arg.split()[0].lower() == "restart" and line.split()[2][0] != "#":
							if src.user.getauth(nick) == c.get("ADMIN", "auth") or arg.split()[1] == c.get("ADMIN", "password"):
								putf("QUIT :Restart ... I\'ll be back in %s seconds!" % c.get("SERVER", "reconnect"))
								disconnect()
								return 0
						elif arg.split()[0].lower() == "jobs" and line.split()[2][0] != "#":
							if src.user.getauth(nick).lower() == c.get("ADMIN", "auth").lower() or arg.split()[1] == c.get("ADMIN", "password"):
								put("NOTICE " + nick + " :[JOBS] " + _timer.print_jobs())

						if target.startswith("#"):
							for hookconfig in _cache.execute("select name,module,command from binds where event == 'pub'"):
								hook = str(hookconfig[0])
								module = str(hookconfig[1])
								command = str(hookconfig[2])

	 							if command != "" and cmd.lower() == command.lower():
									exec("""%s.%s("%s","%s","%s","%s")""" % (module, hook, nick, uhost, target, ' '.join(arg.split()[1:])))
								elif command == "":
									exec("""%s.%s("%s","%s","%s","%s")""" % (module, hook, nick, uhost, target, arg))
						else:
							for hookconfig in _cache.execute("select name,module,command from binds where event == 'msg'"):
								hook = str(hookconfig[0])
								module = str(hookconfig[1])
								command = str(hookconfig[2])

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

						for hookconfig in _cache.execute("select name,module,command from binds where event == 'not'"):
							hook = str(hookconfig[0])
							module = str(hookconfig[1])
							command = str(hookconfig[2])

							if command != "" and cmd.lower() == command.lower():
								exec("""%s.%s("%s","%s","%s","%s")""" % (module, hook, nick, uhost, target, ' '.join(arg.split()[1:])))
							elif command == "":
								exec("""%s.%s("%s","%s","%s","%s")""" % (module, hook, nick, uhost, target, arg))
					elif line.split()[1].lower() == "topic" and line.split()[0].find("!") != -1 and line.split()[0].find("@") != -1:
						nick = line.split("!")[0]
						uhost = line.split("!")[1].split()[0]
						target = line.split()[2]

						if len(line.split()) > 3:
							arg = ' '.join(line.split()[3:])[0:][1:]
						else:
							arg = ""

						for hookconfig in _cache.execute("select name,module from binds where event == 'topic'"):
							hook = str(hookconfig[0])
							module = str(hookconfig[1])
							exec("""%s.%s("%s", "%s", "%s", "%s")""" % (module, hook, nick, uhost, target, arg))
					elif line.split()[1].lower() == "mode" and line.split()[0].find("!") != -1 and line.split()[0].find("@") != -1 and line.split()[2][0] == "#":
						nick = line.split("!")[0]
						uhost = line.split("!")[1].split()[0]
						target = line.split()[2]

						if len(line.split()) > 3:
							arg = ' '.join(line.split()[3:])[0:][1:]
						else:
							arg = ""

						for hookconfig in _cache.execute("select name,module from binds where event == 'mode'"):
							hook = str(hookconfig[0])
							module = str(hookconfig[1])
							exec("""%s.%s("%s", "%s", "%s", "%s")""" % (module, hook, nick, uhost, target, arg))
					elif line.split()[1].lower() == "join" and line.split()[0].find("!") != -1 and line.split()[0].find("@") != -1:
						nick = line.split("!")[0]
						uhost = line.split("!")[1].split()[0]
						target = line.split()[2]

						for hookconfig in _cache.execute("select name,module from binds where event == 'join'"):
							hook = str(hookconfig[0])
							module = str(hookconfig[1])
							exec("""%s.%s("%s", "%s", "%s")""" % (module, hook, nick, uhost, target))
					elif line.split()[1].lower() == "part" and line.split()[0].find("!") != -1 and line.split()[0].find("@") != -1:
						nick = line.split("!")[0]
						uhost = line.split("!")[1].split()[0]
						target = line.split()[2]

						if len(line.split()) > 3:
							arg = ' '.join(line.split()[3:])[0:][1:]
						else:
							arg = ""

						for hookconfig in _cache.execute("select name,module from binds where event == 'part'"):
							hook = str(hookconfig[0])
							module = str(hookconfig[1])
							exec("""%s.%s("%s", "%s", "%s", "%s")""" % (module, hook, nick, uhost, target, arg))
					elif line.split()[1].lower() == "quit" and line.split()[0].find("!") != -1 and line.split()[0].find("@") != -1:
						nick = line.split("!")[0]
						uhost = line.split("!")[1].split()[0]

						if len(line.split()) > 2:
							arg = ' '.join(line.split()[2:])[0:][1:]
						else:
							arg = ""

						for hookconfig in _cache.execute("select name,module from binds where event == 'quit'"):
							hook = str(hookconfig[0])
							module = str(hookconfig[1])
							exec("""%s.%s("%s", "%s", "%s")""" % (module, hook, nick, uhost, arg))
					elif line.split()[1].lower() == "nick" and line.split()[0].find("!") != -1 and line.split()[0].find("@") != -1:
						nick = line.split("!")[0]
						uhost = line.split("!")[1].split()[0]
						target = line.split()[2]

						if target.startswith(":"):
							target = target[1:]

						for hookconfig in _cache.execute("select name,module from binds where event == 'nick'"):
							hook = str(hookconfig[0])
							module = str(hookconfig[1])
							exec("""%s.%s("%s", "%s", "%s")""" % (module, hook, nick, uhost, target))
					elif line.split()[1].lower() == "kick" and line.split()[0].find("!") != -1 and line.split()[0].find("@") != -1:
						nick = line.split("!")[0]
						uhost = line.split("!")[1].split()[0]
						chan = line.split()[2]
						target = line.split()[3]

						if len(line.split()) > 4:
							arg = ' '.join(line.split()[4:])[0:][1:]
						else:
							arg = ""

						for hookconfig in _cache.execute("select name,module from binds where event == 'kick'"):
							hook = str(hookconfig[0])
							module = str(hookconfig[1])
							exec("""%s.%s("%s", "%s", "%s", "%s", "%s")""" % (module, hook, nick, uhost, chan, target, arg))
					elif line.split()[1].lower() == "invite" and line.split()[0].find("!") != -1 and line.split()[0].find("@") != -1:
						nick = line.split("!")[0]
						uhost = line.split("!")[1].split()[0]
						target = line.split()[2]
						chan = line.split()[3]

						if chan.startswith(":"):
							chan = chan[1:]

						for hookconfig in _cache.execute("select name,module from binds where event == 'invite'"):
							hook = str(hookconfig[0])
							module = str(hookconfig[1])
							exec("""%s.%s("%s", "%s", "%s", "%s")""" % (module, hook, nick, uhost, chan, target))


					for hookconfig in _cache.execute("select name,module,command from binds where event == 'raw'"):
						hook = str(hookconfig[0])
						module = str(hookconfig[1])
						command = str(hookconfig[2])
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

			elif sys.argv[1].lower() == "configure":
				c = ConfigParser.RawConfigParser()
				print("Welcome to the Configuring interface! Let's make it easy to use this bot.")
				print("Loading configuration options into cache :)")
				sections = ['SERVER', 'BOT', 'ADMIN', 'SERVICES', 'TELNET']

				for section in sections:
					c.add_section(section)

				options = list()
				options.append(['SERVER', 'address', 'str', 'Server address'])
				options.append(['SERVER', 'port', 'int', 'Server port', '6667'])
				options.append(['SERVER', 'reconnect', 'int', 'Time between reconnects', '30'])
				options.append(['SERVER', 'bind', 'str', 'IP to bind to', ''])
				options.append(['SERVER', 'ipv6', 'bool', '', 'N'])
				options.append(['SERVER', 'ssl', 'bool', '', 'N'])
				options.append(['BOT', 'nick', 'str', ''])
				options.append(['BOT', 'username', 'str', ''])
				options.append(['BOT', 'realname', 'str', ''])
				options.append(['BOT', 'channels', 'str', 'Channels to join on startup seperated with ,'])
				options.append(['BOT', 'debug', 'bool', ''])
				options.append(['BOT', 'identd', 'str', 'Running an IdentD? You can choose between None and oidentd.', 'None'])
				options.append(['BOT', 'auth-reader', 'bool', '', 'Y'])
				options.append(['BOT', 'query_time', 'int', 'Put-Query interval', '2'])
				options.append(['ADMIN', 'password', 'str', 'needed for admin commands'])
				options.append(['ADMIN', 'auth', 'str', 'can replace password at some commands', ''])
				options.append(['SERVICES', 'nickserv', 'str', 'Nickserv password if necessary', ''])
				options.append(['SERVICES', 'quakenet', 'str', 'QuakeNet auth if necessary (format: acc pw)', ''])
				options.append(['TELNET', 'ip', 'str', '', '127.0.0.1'])
				options.append(['TELNET', 'port', 'int', '', '8898'])

				for option in options:
					if c.has_section(option[0]):
						value = ""
						text = option[0].capitalize() + "-" + option[1].capitalize()

						if len(option) == 4:
							if option[2] == "int":
								text += " (Enter a valid number)"
							elif option[2] == "bool":
								text += " (Y/N)"

							if option[3] != "":
								text += " (" + option[3] + ")"

							text += ": "

							while value == "":
								value = raw_input(text)

							if option[2] == "int":
								while not value.isdigit():
									value = raw_input(text)
							elif option[2] == "bool":
								while value != "True" and value != "False":
									if value.lower() == "y":
										value = "True"
									elif value.lower() == "n":
										value = "False"
									else:
										value = raw_input(text)
						elif len(option) == 5:
							if option[2] == "int":
								text += " (Enter a valid number)"
							elif option[2] == "bool":
								text += " (Y/N)"

							if option[3] != "":
								text += " (" + option[3] + ")"

							text += " (Default: " + option[4] + "): "
							value = raw_input(text)

							if value == "":
								value = option[4]
								
								if option[2] == "bool":
									if value == "Y":
										value = "True"
									elif value == "N":
										value = "False"
							elif option[2] == "int":
								while not value.isdigit():
									value = raw_input(text)
							elif option[2] == "bool":
								while value != "True" and value != "False":
									if value.lower() == "y":
										value = "True"
									elif value.lower() == "n":
										value = "False"
									else:
										value = raw_input(text)

						c.set(option[0], option[1], value)

				print("Writing config now...")

				with open("configs/main.conf", "wb") as configfile:
					c.write(configfile)

				print("Config file written :)")
				print("Run '%s' to start me :D" % sys.argv[0])
			elif sys.argv[1].lower() == "-h" or sys.argv[1].lower() == "--help":
				print(sys.argv[0]+" database		creates new databases")
				print(sys.argv[0]+" configure		config maker")
		else:
			thread.start_new_thread(put_query, ())
			printa("Started put_query-thread.")
			thread.start_new_thread(keepnick, ())
			printa("Started keepnick-thread.")
			main()
	except Exception:
		et, ev, tb = sys.exc_info()
		e = "{0} {1} (Line #{2})".format(et, ev, traceback.tb_lineno(tb))
		printe(e)
	except KeyboardInterrupt:
		printe("\nAborting ... CTRL + C")

	sys.exit(2)

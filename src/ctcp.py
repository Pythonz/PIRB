from pirb import bind,put

def load():
	bind("ping","src_ctcp","msg",u"\u0001PING\u0001")
	bind("version","src_ctcp","msg",u"\u0001VERSION\u0001")
	bind("userinfo","src_ctcp","msg",u"\u0001USERINFO\u0001")
	bind("finger", "src_ctcp","msg",u"\u0001FINGER\u0001")

def ctcp(target,text):
	put(u"PRIVMSG %s :\u0001%s\u0001" % (target,text))

def notice(target,text):
	put("PRIVMSG %s :%s" % (target,text))

def ping(nick,uhost,arg):
	ctcp(nick, "PONG")

def version(nick,uhost,arg):
	file = open("version", "r")
	_version = file.read()
	file.close()
	notice(nick, "PIRB "+_version)

def userinfo(nick,uhost,arg):
	file = open("version", "r")
	_version = file.read()
	file.close()
	notice(nick, "PIRB "+_version)

def finger(nick,uhost,arg):
	file = open("version", "r")
	_version = file.read()
	file.close()
	notice(nick, "PIRB "+_version)

import pirb

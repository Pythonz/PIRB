from pirb import bind,put

def load():
	bind("ping","src_ctcp","msg",u"\u0001PING\u0001")

def ctcp(target,text):
	put(u"PRIVMSG %s :\u0001%s\u0001" % (target,text))

def ping(nick,uhost,arg):
	ctcp(nick, "PING")

import pirb

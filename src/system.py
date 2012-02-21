from pirb import bind,put,putf,c
import os

def load():
	bind("uname","pub","$uname")

def uname(nick,host,chan,arg):
	sysinfo = ' '.join(os.uname())
	put("PRIVMSG %s :%s" % (chan, sysinfo))

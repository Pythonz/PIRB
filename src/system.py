from run import bind,put,putf,c
import os

bind("uname","src_system","pub","$uname")

def uname(nick,host,chan,arg):
	sysinfo = ' '.join(os.uname())
	put("PRIVMSG %s :%s" % (chan, sysinfo))

import run

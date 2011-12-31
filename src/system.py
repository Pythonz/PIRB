from run import bind,put,putf,c
import os

bind("uname","src_system","pub","$uname")

def uname(nick,host,chan,arg):
	put("PRIVMSG %s :%s" % (chan, ' '.join(os.uname)))

import run

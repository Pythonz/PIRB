from run import bind,put,putf,c
import os

bind("uname","src_system","pub","$uname")

def uname(nick,host,chan,arg):
	irc_send(chan, ' '.join(os.uname))

import run

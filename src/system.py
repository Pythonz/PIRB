from run import bind,put,putf,c
from src.irc import irc_send
import os

bind("uname","src_system","pub","$uname")

def uname(nick,host,chan,arg):
	irc_send(chan, ' '.join(os.uname))

import run

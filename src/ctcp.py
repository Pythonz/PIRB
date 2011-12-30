from run import bind,put,putf,printa,printc,printe

bind("ping","src_ctcp","msg","PING")

def ping(nick,uhost,arg):
	put("PRIVMSG %s :PONG" % nick)

import run

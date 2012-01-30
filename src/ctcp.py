from run import bind,put,putf,printa,printc,printe

bind("ping","src_ctcp","msg","PING")

def ctcp(target,text):
	put("PRIVMSG %s :%s" % (target,text))

def ping(nick,uhost,arg):
	ctcp(nick, "PING")

import run

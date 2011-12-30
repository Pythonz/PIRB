from run import put,putf,bind,c,printa,printc,printe
from time import sleep
from fnmatch import fnmatch as wmatch

bind("irc_botnick","src_irc","pub","$botnick")
bind("irc_botmode","src_irc","raw","001")
bind("irc_bans","src_irc","raw","352")
bind("irc_ping","src_irc","pub","$timeout")

def irc_botnick(nick,host,chan,arg):
	for data in _cache.execute("select name from botnick"):
		put("PRIVMSG %s :My configured nick is %s and my current nick is %s." % (chan,_botnick,str(data[0])))

def irc_botmode(text):
	for data in _cache.execute("select name from botnick"):
		putf("MODE %s +B" % str(data[0]))

def irc_send(target,message):
	if target.startswith("#"):
		s.send("PRIVMSG %s :%s\n" % (target,message))
		printa("PRIVMSG %s :%s" % (target,message))
	else:
		s.send("NOTICE %s :%s\n" % (target,message))
		printa("NOTICE %s :%s" % (target,message))
	sleep(1)

def irc_bans(text):
	chan = text.split()[3]
	host = text.split()[7]+"!"+text.split()[4]+"@"+text.split()[5]
	for data in _chandb.execute("select ban from bans where channel='%s'" % chan):
		if wmatch(host.lower(), str(data[0]).lower()):
			entry = False
			for data in _chandb.execute("select exempt from exempts where channel='%s'" % chan):
				if wmatch(host.lower(), str(data[0]).lower()):
					entry = True
			if entry == False:
				put("MODE %s +b %s" % (chan,data[0]))
				put("KICK %s %s :Banned." % (chan,text.split()[7]))

def irc_ping(nick,host,chan,arg):
	irc_send(chan,"Last ping was recieved %s minutes ago." % _timeout)

import run

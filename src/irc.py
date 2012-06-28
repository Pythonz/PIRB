from pirb import put,putf,bind,c,printa,printc,printe
from time import sleep
from fnmatch import fnmatch as wmatch

def load():
	bind("irc_botnick","pub","$botnick")
	bind("irc_botmode","raw","001")
	bind("irc_bans","raw","352")
	bind("irc_version","msg","version")

def irc_botnick(nick,host,chan,arg):
	for data in _cache.execute("select name from botnick"):
		put("PRIVMSG %s :My configured nick is %s and my current nick is %s." % (chan,_botnick,str(data[0])))

def irc_botmode(text):
	for data in _cache.execute("select name from botnick"):
		putf("MODE %s +B" % str(data[0]))

def irc_send(target,message):
	if target.startswith("#"):
		put("PRIVMSG %s :%s" % (target,message))
	else:
		put("NOTICE %s :%s" % (target,message))

def irc_bans(text):
	chan = text.split()[3]
	host = text.split()[7]+"!"+text.split()[4]+"@"+text.split()[5]

	for data in _chandb.execute("select ban from bans where channel='%s'" % chan):
		if wmatch(host.lower(), str(data[0]).lower()):
			entry = False

			for data1 in _chandb.execute("select exempt from exempts where channel='%s'" % chan):
				if wmatch(host.lower(), str(data1[0]).lower()):
					entry = True

				for botnick in _cache.execute("select name from botnick"):
					if str(text.split()[7]).lower() == str(text.split()[2]).lower():
						entry = True

			if entry == False:
				put("MODE %s +b %s" % (chan,data[0]))
				put("KICK %s %s :Banned." % (chan,text.split()[7]))

def irc_version(nick,uhost,args):
	_version = open("version", "r")
	irc_send(nick, "PIRB {0}".format(_version.read()))
	_version.close()

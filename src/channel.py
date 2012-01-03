from run import put,putf,bind,c,printa,printc,printe
from src.user import getauth
from fnmatch import fnmatch as wmatch
from src.irc import irc_send

bind("channel_join","src_channel","raw","001")
bind("channel_kick","src_channel","raw","KICK")
bind("channel_register","src_channel","msg","register")
bind("channel_drop","src_channel","msg","drop")
bind("on_join_chan","src_channel","raw","JOIN")
bind("channel_addop","src_channel","pub","$addop")
bind("channel_delop","src_channel","pub","$delop")
bind("channel_addvoice","src_channel","pub","$addvoice")
bind("channel_delvoice","src_channel","pub","$delvoice")
bind("channel_listuser","src_channel","pub","$users")
bind("channel_auth","src_channel","pub","$auth")
bind("channel_invite","src_channel","raw","INVITE")
bind("channel_modes","src_channel","pub","$mode")
bind("channel_topic","src_channel","pub","$topic")
bind("on_topic","src_channel","raw","TOPIC")
bind("on_mode","src_channel","raw","MODE")
bind("ban","src_channel","pub","$ban")
bind("exempt","src_channel","pub","$exempt")
bind("op","src_channel","pub","$op")
bind("deop","src_channel","pub","$deop")
bind("voice","src_channel","pub","$voice")
bind("devoice","src_channel","pub","$devoice")
bind("kick","src_channel","pub","$kick")
bind("invite","src_channel","pub","$invite")

def getflag(chan,auth):
	for data in _chandb.execute("select flags from channel where channel='%s' and auth='%s'" % (chan,auth)):
		return data[0]

def gethostflag(chan,host):
	for data in _chandb.execute("select auth,flags from channel where channel='%s'" % chan):
		if wmatch(host.lower(), str(data[0]).lower()):
			return str(data[1])

def kick(nick,host,chan,arg):
	auth = getauth(nick)
	flag = getflag(chan,auth)
	hostmask = nick+"!"+host
	hostflag = gethostflag(chan,hostmask)
	if flag == "n" or flag == "o" or hostflag == "o":
		if len(arg.split()) != 0:
			target = arg.split()[0]
			reason = "Requested."
			if len(arg.split()) != 1:
				reason = ' '.join(arg.split()[1:])
			put("KICK %s %s :%s" % (chan,target,reason))

def invite(nick,host,chan,arg):
	auth = getauth(nick)
	flag = getflag(chan,auth)
	hostmask = nick+"!"+host
	hostflag = gethostflag(chan,hostmask)
	if flag == "n" or flag == "o" or hostflag == "o":
		for user in arg.split():
			put("INVITE %s %s" % (user,chan))

def op(nick,host,chan,arg):
	auth = getauth(nick)
	flag = getflag(chan,auth)
	hostmask = nick+"!"+host
	hostflag = gethostflag(chan,hostmask)
	if flag == "n" or flag == "o" or hostflag == "o":
		if len(arg.split()) != 0:
			mode = "o"*len(arg.split())
			putf("MODE %s +%s %s" % (chan,mode,arg))
		else:
			putf("MODE %s +o %s" % (chan,nick))

def deop(nick,host,chan,arg):
	auth = getauth(nick)
	flag = getflag(chan,auth)
	hostmask = nick+"!"+host
	hostflag = gethostflag(chan,hostmask)
	if flag == "n" or flag == "o" or hostflag == "o":
		if len(arg.split()) != 0:
			mode = "o"*len(arg.split())
			putf("MODE %s -%s %s" % (chan,mode,arg))
		else:
			putf("MODE %s -o %s" % (chan,nick))

def voice(nick,host,chan,arg):
	auth = getauth(nick)
	flag = getflag(chan,auth)
	hostmask = nick+"!"+host
	hostflag = gethostflag(chan,hostmask)
	if flag == "n" or flag == "o" or hostflag == "o":
		if len(arg.split()) != 0:
			mode = "v"*len(arg.split())
			putf("MODE %s +%s %s" % (chan,mode,arg))
		else:
			putf("MODE %s +v %s" % (chan,nick))

def devoice(nick,host,chan,arg):
	auth = getauth(nick)
	flag = getflag(chan,auth)
	hostmask = nick+"!"+host
	hostflag = gethostflag(chan,hostmask)
	if flag == "n" or flag == "o" or hostflag == "o":
		if len(arg.split()) != 0:
			mode = "v"*len(arg.split())
			putf("MODE %s -%s %s" % (chan,mode,arg))
		else:
			putf("MODE %s -v %s" % (chan,nick))

def ban(nick,host,chan,arg):
	target = arg.split()[0][1:]
	scut = arg.split()[0]
	auth = getauth(nick)
	flag = getflag(chan,auth)
	hostmask = nick+"!"+host
	hostflag = gethostflag(chan,hostmask)
	if flag == "n" or flag == "o" or hostflag == "o":
		if wmatch(target, "*!*@*"):
			if scut.startswith("+"):
				entry = False
				for data in _chandb.execute("select ban from bans where channel='%s' and ban='%s'" % (chan,target)):
					entry = True
				if entry is False:
					_chandb.execute("insert into bans values ('%s','%s')" % (chan,target))
					put("NOTICE %s :[%s] %s has been added to the banlist" % (nick,chan,target))
					put("WHO %s" % chan)
				else:
					put("NOTICE %s :[%s] %s is already on the banlist" % (nick,chan,target))
			elif scut.startswith("-"):
				entry = False
				for data in _chandb.execute("select ban from bans where channel='%s' and ban='%s'" % (chan,target)):
					entry = True
				if entry is True:
					_chandb.execute("delete from bans where channel='%s' and ban='%s'" % (chan,target))
					put("NOTICE %s :[%s] %s has been removed from the banlist" % (nick,chan,target))
					put("MODE %s -b %s" % (chan,target))
				else:
					put("NOTICE %s :[%s] %s is not on the banlist" % (nick,chan,target))
			else:
				irc_send(nick,"$ban +/-*!*example@*.example.com")
		else:
			for data in _chandb.execute("select ban from bans where channel='%s'" % chan):
				irc_send(nick,"[%s] %s" % (chan,str(data[0])))

def exempt(nick,host,chan,arg):
	target = arg.split()[0][1:]
	scut = arg.split()[0]
	auth = getauth(nick)
	flag = getflag(chan,auth)
	hostmask = nick+"!"+host
	hostflag = gethostflag(chan,hostmask)
	if flag == "n" or flag == "o" or hostflag == "o":
		if wmatch(target, "*!*@*"):
			if scut.startswith("+"):
				entry = False
				for data in _chandb.execute("select exempt from exempts where channel='%s' and exempt='%s'" % (chan,target)):
					entry = True
				if entry is False:
					_chandb.execute("insert into exempts values ('%s','%s')" % (chan,target))
					put("NOTICE %s :[%s] %s has been added to the exemptlist" % (nick,chan,target))
					put("WHO %s" % chan)
				else:
					put("NOTICE %s :[%s] %s is already on the exemptlist" % (nick,chan,target))
			elif scut.startswith("-"):
				entry = False
				for data in _chandb.execute("select exempt from exempts where channel='%s' and exempt='%s'" % (chan,target)):
					entry = True
				if entry is True:
					_chandb.execute("delete from exempts where channel='%s' and exempt='%s'" % (chan,target))
					put("NOTICE %s :[%s] %s has been removed from the exemptlist" % (nick,chan,target))
					put("MODE %s -b %s" % (chan,target))
				else:
					put("NOTICE %s :[%s] %s is not on the exemptlist" % (nick,chan,target))
			else:
				irc_send(nick,"$exempt +/-*!*example@*.example.com")
		else:
			for data in _chandb.execute("select exempt from exempts where channel='%s'" % chan):
				irc_send(nick,"[%s] %s" % (chan,str(data[0])))

def channel_modes(nick,host,chan,arg):
	auth = getauth(nick)
	hostmask = nick+"!"+host
	flag = getflag(chan,auth)
	hostflag = gethostflag(chan,hostmask)
	if flag == "n" or flag == "o" or hostflag == "o":
		_chandb.execute("update info set modes='%s' where channel='%s'" % (arg,chan))
		put("MODE %s %s" % (chan,arg))

def channel_topic(nick,host,chan,arg):
	auth = getauth(nick)
	hostmask = nick+"!"+host
	flag = getflag(chan,auth)
	hostflag = gethostflag(chan,hostmask)
	if flag == "n" or flag == "o" or hostflag == "o":
		_chandb.execute("update info set topic='%s' where channel='%s'" % (arg,chan))
		put("TOPIC %s :%s" % (chan,arg))

def on_topic(text):
	nick = text.split()[0][1:].split("!")[0]
	for mynick in _cache.execute("select name from botnick"):
		if nick != str(mynick[0]) and nick != "Q" and nick != "ChanServ":
			for data in _chandb.execute("select topic from info where channel='%s'" % text.split()[2]):
				put("TOPIC %s :%s" % (text.split()[2],str(data[0])))

def on_mode(text):
	nick = text.split()[0][1:].split("!")[0]
	for mynick in _cache.execute("select name from botnick"):
		if nick != str(mynick[0]):
			for data in _chandb.execute("select modes from info where channel='%s'" % text.split()[2]):
				put("MODE %s %s" % (text.split()[2],str(data[0])))

def channel_invite(text):
	chan = text.split()[3]
	if chan.startswith(":"):
		for data in _chandb.execute("select channel from list where channel='%s'" % chan[1:]):
			put("JOIN %s" % chan[1:])
	else:
		for data in _chandb.execute("select channel from list where channel='%s'" % chan):
			put("JOIN %s" % chan)

def channel_addop(nick,host,chan,arg):
	auth = getauth(nick)
	flag = getflag(chan,auth)
	target = getauth(arg.split()[0])
	uatarget = arg.split()[0]
	if flag == "n":
		if auth != target:
			if wmatch(uatarget, "*!*@*"):
				entry = False
				for data in _chandb.execute("select flags from channel where channel='%s' and auth = '%s' and flags='o'" % (chan,uatarget)):
					entry = True
				if entry is False:
					_chandb.execute("insert into channel values ('%s','%s','o')" % (chan,uatarget))
					put("NOTICE %s :[%s] %s has been added to the operators list" % (nick,chan,uatarget))
				else:
					put("NOTICE %s :[%s] %s is already on the operators list" % (nick,chan,uatarget))
			else:
				entry = False
				for data in _chandb.execute("select flags from channel where channel='%s' and auth='%s' and flags='o'" % (chan,target)):
					entry = True
				if entry is False:
					_chandb.execute("insert into channel values ('%s','%s','o')" % (chan,target))
					put("NOTICE %s :[%s] %s has been added to the operators list" % (nick,chan,target))
					put("MODE %s +o %s" % (chan,arg.split()[0]))
				else:
					put("NOTICE %s :[%s] %s is already on the operators list" % (nick,chan,target))
		else:
			put("NOTICE %s :[%s] You cannot add yourself!" % (nick,chan))

def channel_delop(nick,host,chan,arg):
	auth = getauth(nick)
	flag = getflag(chan,auth)
	target = getauth(arg.split()[0])
	uatarget = arg.split()[0]
	if flag == "n":
		if auth != target:
			if wmatch(uatarget, "*!*@*"):
				entry = True
				for data in _chandb.execute("select flags from channel where channel='%s' and auth = '%s' and flags='o'" % (chan,uatarget)):
					entry = False
				if entry is False:
					_chandb.execute("delete from channel where channel='%s' and auth='%s' and flags='o'" % (chan,uatarget))
					put("NOTICE %s :[%s] %s has been removed from the operators list" % (nick,chan,uatarget))
				else:
					put("NOTICE %s :[%s] %s is not on the operators list" % (nick,chan,uatarget))
			else:
				entry = True
				for data in _chandb.execute("select flags from channel where channel='%s' and auth='%s' and flags='o'" % (chan,target)):
					entry = False
				if entry is False:
					_chandb.execute("delete from channel where channel='%s' and auth='%s' and flags='o'" % (chan,target))
					put("NOTICE %s :[%s] %s has been removed from the operators list" % (nick,chan,target))
					put("MODE %s -o %s" % (chan,arg.split()[0]))
				else:
					put("NOTICE %s :[%s] %s is not on the operators list" % (nick,chan,target))
		else:
			put("NOTICE %s :[%s] You cannot remove yourself!" % (nick,chan))

def channel_addvoice(nick,host,chan,arg):
	auth = getauth(nick)
	flag = getflag(chan,auth)
	target = getauth(arg.split()[0])
	uatarget = arg.split()[0]
	if flag == "n":
		if auth != target:
			if wmatch(uatarget, "*!*@*"):
				entry = False
				for data in _chandb.execute("select flags from channel where channel='%s' and auth = '%s' and flags='v'" % (chan,uatarget)):
					entry = True
				if entry is False:
					_chandb.execute("insert into channel values ('%s','%s','v')" % (chan,uatarget))
					put("NOTICE %s :[%s] %s has been added to the voices list" % (nick,chan,uatarget))
				else:
					put("NOTICE %s :[%s] %s is already on the voices list" % (nick,chan,uatarget))
			else:
				entry = False
				for data in _chandb.execute("select flags from channel where channel='%s' and auth='%s' and flags='v'" % (chan,target)):
					entry = True
				if entry is False:
					_chandb.execute("insert into channel values ('%s','%s','v')" % (chan,target))
					put("NOTICE %s :[%s] %s has been added to the voices list" % (nick,chan,target))
					put("MODE %s +v %s" % (chan,arg.split()[0]))
				else:
					put("NOTICE %s :[%s] %s is already on the voices list" % (nick,chan,target))
		else:
			put("NOTICE %s :[%s] You cannot add yourself!" % (nick,chan))

def channel_delvoice(nick,host,chan,arg):
	auth = getauth(nick)
	flag = getflag(chan,auth)
	target = getauth(arg.split()[0])
	uatarget = arg.split()[0]
	if flag == "n":
		if auth != target:
			if wmatch(uatarget, "*!*@*"):
				entry = True
				for data in _chandb.execute("select flags from channel where channel='%s' and auth = '%s' and flags='v'" % (chan,uatarget)):
					entry = False
				if entry is False:
					_chandb.execute("delete from channel where channel='%s' and auth='%s' and flags='v'" % (chan,uatarget))
					put("NOTICE %s :[%s] %s has been removed from the voices list" % (nick,chan,uatarget))
				else:
					put("NOTICE %s :[%s] %s is not on the voices list" % (nick,chan,uatarget))
			else:
				entry = True
				for data in _chandb.execute("select flags from channel where channel='%s' and auth='%s' and flags='v'" % (chan,target)):
					entry = False
				if entry is False:
					_chandb.execute("delete from channel where channel='%s' and auth='%s' and flags='v'" % (chan,target))
					put("NOTICE %s :[%s] %s has been removed from the voices list" % (nick,chan,target))
					put("MODE %s -v %s" % (chan,arg.split()[0]))
				else:
					put("NOTICE %s :[%s] %s is not on the voices list" % (nick,chan,target))
		else:
			put("NOTICE %s :[%s] You cannot remove yourself!" % (nick,chan))

def channel_listuser(nick,host,chan,arg):
	for owner in _chandb.execute("select auth from channel where channel='%s' and flags='n'" % chan):
		put("NOTICE %s :[%s] %s is the owner" % (nick,chan,owner[0]))
	op = _chandb.execute("select auth from channel where channel='%s' and flags='o'" % chan)
	operators = ', '.join(set(op.fetchall()))
	put("NOTICE %s :[%s] Operators: %s" % (nick,chan,operators))
	v = _chandb.execute("select auth from channel where channel='%s' and flags='v'" % chan)
	voices = ', '.join(set(v.fetchall()))
	put("NOTICE %s :[%s] %s is a voice" % (nick,chan,voices))

def channel_join(text):
	putf("JOIN %s" % c.get("BOT", "channels"))
	for data in _chandb.execute("select channel from list"):
		put("JOIN %s" % data[0])

def channel_kick(text):
	nick = text.split()[0][1:].split("!")[0]
	chan = text.split()[2]
	target = text.split()[3]
	if target.find(c.get("BOT", "nick")) != -1:
		put("JOIN %s" % chan)

def channel_register(nick,uhost,arg):
	password = arg.split()[0]
	channel = arg.split()[1]
	if password == c.get("ADMIN", "password"):
		_chandb.execute("insert into list values ('%s')" % channel)
		put("JOIN %s" % channel)
		put("NOTICE %s :%s has been added to the database ... You got owner flags" % (nick,channel))
		_chandb.execute("insert into channel values ('%s','%s','n')" % (channel,getauth(nick)))
		_chandb.execute("insert into info values ('%s','','')" % channel)

def channel_drop(nick,uhost,arg):
	password = arg.split()[0]
	channel = arg.split()[1]
	if password == c.get("ADMIN", "password"):
		_chandb.execute("delete from list where channel='%s'" % channel)
		put("PART %s" % channel)
		put("NOTICE %s :%s has been removed from the database" % (nick,channel))
		_chandb.execute("delete from channel where channel='%s'" % channel)
		_chandb.execute("delete from info where channel='%s'" % channel)

def on_join_chan(text):
	nick = text.split()[0][1:].split("!")[0]
	putf("WHO %s" % nick)
	hostmask = text.split()[0][1:]
	if text.split()[2].startswith(":"):
		chan = text.split()[2][1:]
	else:
		chan = text.split()[2]
	auth = getauth(nick)
	flag = getflag(chan,auth)
	hostflag = gethostflag(chan,hostmask)
	if flag == "n" or flag == "o" or hostflag == "o":
		putf("MODE %s +o %s" % (chan,nick))
	if flag == "v" or hostflag == "v":
		putf("MODE %s +v %s" % (chan,nick))

def channel_auth(nick,host,chan,arg):
	put("NOTICE %s :[%s] Trying to auth ..." % (nick,chan))
	auth = getauth(nick)
	hostmask = nick+"!"+host
	put("NOTICE %s :[%s] Getting flag for %s (%s)..." % (nick,chan,auth,hostmask))
	flag = getflag(chan,auth)
	hostflag = gethostflag(chan,hostmask)
	put("NOTICE %s :[%s] Flag: %s, Hostflag: %s" % (nick,chan,flag,hostflag))
	if flag == "n" or flag == "o" or hostflag == "o":
		putf("MODE %s +o %s" % (chan,nick))
	if flag == "v" or hostflag == "v":
		putf("MODE %s +v %s" % (chan,nick))

import run

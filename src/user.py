from pirb import put,putf,bind,c,printa,printc,printe,whois,whochan

def load():
	bind("nick_in_use","raw","433")
	if c.getboolean("BOT", "auth-reader"):
		bind("on_quit","quit")
		bind("whois_330","raw","330")
		bind("who_354", "raw", "354")
		bind("check_user","raw","352")
		bind("on_366","raw","366")
		bind("on_nickchange","nick")
		bind("whois_307","raw","307")

def nick_in_use(text):
	for data in _cache.execute("select name from botnick"):
		putf("NICK %s_" % str(data[0]))
		_cache.execute("update botnick set name='%s_'" % str(data[0]))

def on_quit(nick,uhost,arg):
	_userdb.execute("delete from auth where nick='%s'" % nick)

	if nick.lower() == _botnick.lower():
		_cache.execute("update botnick set name='%s'" % _botnick)
		put("NICK %s" % _botnick)

def whois_330(text):
	_userdb.execute("delete from auth where nick='%s'" % text.split()[3])
	_userdb.execute("insert into auth values ('%s','%s')" % (text.split()[3], text.split()[4]))

def whois_307(text):
	_userdb.execute("delete from auth where nick='%s'" % text.split()[3])
	_userdb.execute("insert into auth values ('%s','%s')" % (text.split()[3], text.split()[3]))

def who_354(text):
	if text.split()[3] == "111":
		_userdb.execute("delete from auth where nick='%s'" % text.split()[4])
		_userdb.execute("insert into auth values ('%s','%s')" % (text.split()[4], text.split()[5]))

def check_user(text):
	if not c.get("SERVER", "address").lower().endswith(".quakenet.org"):
		whois(text.split()[7])

def on_366(text):
	whochan(text.split()[3])

def on_nickchange(nick,uhost,newnick):
	for data in _cache.execute("select name from botnick"):
		if nick == str(data[0]):
			_cache.execute("update botnick set name='%s'" % newnick)

	if nick.lower() == _botnick.lower():
		_cache.execute("update botnick set name='%s'" % _botnick)
		put("NICK %s" % _botnick)

	_userdb.execute("delete from auth where nick='%s'" % nick)

	whois(newnick)

def getauth(nick):
	if c.getboolean("BOT", "auth-reader"):
		for data in _userdb.execute("select auth from auth where nick='%s'" % nick):
			return data[0]
	else:
		return "disabled"

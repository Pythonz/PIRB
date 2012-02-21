from pirb import put,putf,bind,c,printa,printc,printe,whois,whochan
import pirb

def load():
	bind("nick_in_use","raw","433")
	bind("on_quit","raw","QUIT")
	bind("whois_330","raw","330")
	bind("who_354", "src_user", "raw", "354")
	bind("check_user","raw","352")
	bind("on_366","raw","366")
	bind("on_nickchange","raw","NICK")
	bind("whois_307","raw","307")

def nick_in_use(text):
	for data in _cache.execute("select name from botnick"):
		putf("NICK %s_" % str(data[0]))
		_cache.execute("update botnick set name='%s_'" % str(data[0]))

def on_quit(text):
	_userdb.execute("delete from auth where nick='%s'" % text.split()[0][1:].split("!")[0])
	if text.lower().split()[0][1:].split("!")[0] == _botnick.lower():
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

def on_nickchange(text):
	for data in _cache.execute("select name from botnick"):
		if text.split()[0][1:].split("!")[0] == str(data[0]):
			_cache.execute("update botnick set name='%s'" % text.split()[2])
	if text.lower().split()[0][1:].split("!")[0] == _botnick.lower():
		_cache.execute("update botnick set name='%s'" % _botnick)
		put("NICK %s" % _botnick)
	_userdb.execute("delete from auth where nick='%s'" % text.split()[0][1:].split("!")[0])
	if text.split()[2].startswith(":"):
		whois(text.split()[2][1:])
	else:
		whois(text.split()[2])

def getauth(nick):
	for data in _userdb.execute("select auth from auth where nick='%s'" % nick):
		return data[0]

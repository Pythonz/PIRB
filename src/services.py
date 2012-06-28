from pirb import put,bind,c,putf

def load():
	bind("nick_identify","not")
	bind("quakenet_auth","raw","001")
	bind("quakenet_mode_x","not","You")

def nick_identify(nick, uhost, target, arg):
	if nick == "NickServ":
		if arg.lower().find("wenn du ihn nicht innerhalb einer minute identifizierst") != -1:
			ns_pw = c.get("SERVICES", "nickserv")
			putf("PRIVMSG NickServ :IDENTIFY %s" % ns_pw)
		elif arg.lower().find("nickname is registered") != -1:
			ns_pw = c.get("SERVICES", "nickserv")
			putf("PRIVMSG NickServ :IDENTIFY %s" % ns_pw)

def quakenet_auth(text):
	if c.get("SERVICES", "quakenet") != "" and len(c.get("SERVICES", "quakenet").split()) == 2:
		putf("AUTH %s" % c.get("SERVICES", "quakenet"))

def quakenet_mode_x(nick,host,target,arg):
	react = "are now logged in as "+c.get("SERVICES","quakenet").split()[0]+"."

	if arg == react:
		putf("MODE %s +x" % target)

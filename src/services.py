from pirb import put,bind,c,putf

def load():
	bind("nick_identify","src_services","not")
	bind("quakenet_auth","src_services","raw","376")
	bind("quakenet_mode_x","src_services","not","You")

def nick_identify(nick, uhost, target, arg):
	if nick == "NickServ":
		if arg.lower().find("wenn du ihn nicht innerhalb einer minute identifizierst") != -1:
			ns_pw = c.get("SERVICES", "nickserv")
			putf("PRIVMSG NickServ :IDENTIFY %s" % ns_pw)
		if arg.lower().find("nickname is registered") != -1:
			ns_pw = c.get("SERVICES", "nickserv")
			putf("PRIVMSG NickServ :IDENTIFY %s" % ns_pw)

def quakenet_auth(text):
	if c.get("SERVICES", "quakenet") != "" and len(c.get("SERVICES", "quakenet").split()) == 2:
		putf("PRIVMSG Q@CServe.quakenet.org :AUTH %s" % c.get("SERVICES", "quakenet"))

def quakenet_mode_x(nick,host,target,arg):
        react = "are now logged in as "+c.get("SERVICES","quakenet").split()[0]+"."
        if arg == react:
                putf("MODE %s +x" % target)

import pirb

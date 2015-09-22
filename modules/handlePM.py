def init():
    event_handler.hook('irc:on_privmsg', on_privmsg)
    event_handler.hook('irc:on_privnotice', on_privnotice)

def on_privmsg(bot, connection, event):
    print('%s messaged you, they said: %s' % (event.source.nick, event.arguments[0]))
def on_privnotice(bot, connection, event):
    try:
        if event.source.nick in ("Global", "ChanServ", "NuclearFallout.WA.US.GameSurge.net"):
            pass
        else:
            print('%s sent you a notice, they said: %s' %(event.source.nick, event.arguments[0]))
    except:
        pass
#       A question handler written by Aqua         #
#      https://github.com/Levtastic/kittenbot      #
"""
    TODO:
        [-] init modules, functions
    FINISHED:
        [✔] 
"""
import random
def init():
    #uestionHandler()
    pass
class questionHandler():

    def __init__(self):
        event_handler.hook('irc:on_pubmsg', self.on_pubmsg)
        self.workingChannels = ["#squadchat", "#puppy", "#Jasper"]
        
    def on_pubmsg(self, bot, connection, event):
        if event.target not in self.workingChannels:
            return
        if event.arguments[0].startswith(connection.get_nickname()): #someone is addressing us
            #if event.arguments[0].endswith("?"): #definitely a question
            
            if ("dont" or "don't") and "love" in event.arguments[0]:
                bot.send(connection, event.target, "%s i do! %s loves everyone" % (event.source.nick, connection.get_nickname()), event)
                
            if ("y" or "why") and not "love" in event.arguments[0]:
                bot.send(connection, event.target, "i dunno %s, sometimes there just isn't a reason..." % event.source.nick, event)

            if ("self-aware" or "self aware") in event.arguments[0]:
                bot.send(connection, event.target, "yes %s, i am working on it..." % event.source.nick, event)
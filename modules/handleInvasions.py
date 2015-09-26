#     An invasion handler for ToontownRewritten    #
#          written by Aqua for kittenbot           #
#      https://github.com/Levtastic/kittenbot      #
"""
    TODO:
        [-] display cogtypes, remaining, etc
        [-] return a message when there arent any invasions
        [-] have module interpret api data _properly_
    FINISHED:
        [✔] init functions
        [✔] call invasions api
"""
import urllib.request as r,json
def init():
    invasionHandler()

class invasionHandler():

    def __init__(self):
        event_handler.hook('irc:on_pubmsg', self.on_pubmsg)
        self.triggers = ["puppy are there any invasions?", "puppy are there any invasions"]
        
    def on_pubmsg(self, bot, connection, event):
        if event.target not in ("#squadchat", "#puppy"):
            return
    #LIST INV
        if any(trigger in event.arguments[0] for trigger in self.triggers):
            self.returnInvasions(bot, connection, event)
            
    def returnInvasions(self, bot, connection, event):
        districts = []
        invargs = []
        stats = []
        raw_json = json.loads(r.urlopen("https://www.toontownrewritten.com/api/invasions").read().decode('utf-8'))

        dist_str = ', '.join([a for a in raw_json['invasions']])
        
        # for a in invasions:
            # districts += a
            # for b in invasions[a]:
                # invargs += b
                # try:
                    # for c in invasions[a][b]:
                        # stats += c
                # except:
                    # pass
        bot.send(connection, event.target, "Hey there %s, there are currently invasions in %s!" % (event.source.nick, dist_str), event)
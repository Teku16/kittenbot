#     An invasion handler for ToontownRewritten    #
#          written by Aqua for kittenbot           #
#      https://github.com/Levtastic/kittenbot      #
"""
    TODO:
        [-] display [✔] cogtypes, [-] remaining, etc
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
        if "is ttr up?" in event.arguments[0]:
            self.serverStatus(bot, connection, event)
            
    def serverStatus(self, bot, connection, event):
        pass #TODO
            
    def returnInvasions(self, bot, connection, event):
        raw_json = json.loads(r.urlopen("https://www.toontownrewritten.com/api/invasions").read().decode('utf-8'))
        invasions = [a for a in raw_json['invasions']]
        dist_str = ', '.join([a for a in invasions])
        stuff = ([value['type'] for key, value in raw_json['invasions'].items()])
        type_str = ', '.join([a for a in stuff])                    
        
        inv_msg = ', '.join(['%s (%s)' % (key, value['type']) for key, value in raw_json['invasions'].items()])

        bot.send(connection, event.target, "Hey there %s, the current invasions are: %s!" % (event.source.nick, inv_msg), event)
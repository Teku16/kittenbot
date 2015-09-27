#     An invasion handler for ToontownRewritten    #
#          written by Aqua for kittenbot           #
#      https://github.com/Levtastic/kittenbot      #
"""
    TODO:
        [-] display [✔] cogtypes, [-] remaining, etc
        [-] have module interpret api data _properly_
        [-] variation in response strings for different replys
    FINISHED:
        [✔] init functions | call invasions api
        [✔] return a message when there arent any invasions
        [✔] can check TTR server status
"""
import urllib.request as r,json
from urllib.request import Request, urlopen
def init():
    invasionHandler()

class invasionHandler():

    def __init__(self):
        event_handler.hook('irc:on_pubmsg', self.on_pubmsg)
        self.triggers = ["puppy are there any invasions?", "puppy are there any invasions"]
        self.workingChannels = ["#squadchat", "#puppy"]
        self.p_triggers = ["status", "progress", "remaining"]

    def on_pubmsg(self, bot, connection, event):
        if event.target not in self.workingChannels:
            return
    #LIST INV
        if any(trigger in event.arguments[0] for trigger in self.triggers):
            self.returnInvasions(bot, connection, event)
    #SERVER STATUS
        if "is ttr up?" in event.arguments[0]:
            self.serverStatus(bot, connection, event)
    #PROGRESS
        try:
            if any(word in event.arguments[0].split(" ", 2)[1] for word in self.p_triggers):
                cogtype = event.arguments[0].split(" ", 2)[2]
                self.returnProgress(cogtype, bot, connection, event)
        except:
            pass
    def serverStatus(self, bot, connection, event):
            status_raw = json.loads(r.urlopen("https://www.toontownrewritten.com/api/status").read().decode('utf-8'))
            status = status_raw['open']
            if status:#                                 V green   V clear
                bot.send(connection, event.target, "%s, 03yes, the Toontown Rewritten servers are currently up and running!" % event.source.nick, event)
            else:
                bot.send(connection, event.target, "%s, 4no, the Toontown Rewritten servers are currently down :(" % event.source.nick, event)
                bot.send(connection, event.target, "However, their website says '%s'." % status_raw['banner'], event)
    def returnInvasions(self, bot, connection, event):
        raw_json = json.loads(r.urlopen("https://www.toontownrewritten.com/api/invasions").read().decode('utf-8'))
        invasions = (['%s (%s)' % (key, value['type']) for key, value in raw_json['invasions'].items()])
        if not invasions:
            bot.send(connection, event.target, "Sorry %s, there doesn't seem to be any invasions right now!" % event.source.nick, event)
        else:
            inv_msg = ', '.join(invasions[:-1])
            bot.send(connection, event.target, "Hey there %s, the current invasions are: %s!" % (event.source.nick, inv_msg + " and " + invasions[-1]), event)
        
    def returnProgress(self, requestedType, bot, connection, event):
        parsed_data = urlopen(Request("http://toonhq.org/api/v1/invasion/", headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8')
        raw_json = json.loads(parsed_data)
        cogTypes = []
        total = []
        defeated = []
        for inv in raw_json['invasions']:
            cogTypes.append(inv['cog'])
        if requestedType in cogTypes:
            print("yay!", cogTypes) #debug
            InvasionData = []
            for inv in raw_json['invasions']:
                InvasionData = {inv['district']:{'cog' : inv['cog'], 'total' : inv['total'], 'defeated' : inv['defeated']}}
                print("invasionData = ", InvasionData) #debug
                for districts in InvasionData:
                    if requestedType in InvasionData[districts]['cog']:
                        total = (InvasionData[districts]['total'])
                        print("total = ", total) #debug
                        defeated = (InvasionData[districts]['defeated'])
                        print("defeated = ", defeated) #debug
            num_remaining = total - defeated
            print("remaining = ", num_remaining) #debug
            bot.send(connection, event.target, "%s, in the %s invasion, there are %d cogs remaining!" % (event.source.nick, requestedType, num_remaining), event)
        else:
            bot.send(connection, event.target, "Sorry %s, I could not find an invasion for '%s'." % (event.source.nick, cogtype), event)
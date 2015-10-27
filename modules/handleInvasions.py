#     An invasion handler for ToontownRewritten    #
#          written by Aqua for kittenbot           #
#      https://github.com/Levtastic/kittenbot      #
"""
    TODO:
        [-] make module interpret time since start, total time etc
    FINISHED:
        [✔] init functions | call invasions api
        [✔] display [✔] cogtypes, [✔] remaining
        [✔] return a message when there arent any invasions
        [✔] can check TTR server status
        [✔] translate returnInvasions to the ToonHQ api
        [✔] variation in response strings for different replys
        [✔] store certain variables between reloads 
"""
import json, random
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
import modules.resources.format as f
from socket import timeout
def init():
    invasionHandler()

class invasionHandler():

    def __init__(self):
        self.invLoop = False
        event_handler.hook('irc:on_pubmsg', self.on_pubmsg)
        event_handler.hook('modulehandler:before_load_modules', self.before_load_modules)
        event_handler.hook('modulehandler:before_init_modules', self.before_init_modules)
        event_handler.hook('modulehandler:after_load_modules', self.restoreOldVariables)
        
        self.triggers = ["puppy are there any invasions?", "puppy are there any invasions", "!invasions"]
        self.workingChannels = ["#squadchat", "#puppy"]
        self.p_triggers = ["status", "progress", "remaining"]
        self.greeting = ["Hey there", "Yooo", "What's up", "Greetings", "Hey", "Hiya", "Hello", "Ayy"]
        
        self.Sellbots = ['Cold Caller', 'Telemarketer', 'Name Dropper', 'Glad Hander', 'Mover & Shaker', 'Two-Face', 'The Mingler', 'Mr. Hollywood']
        self.Cashbots = ['Short Change', 'Penny Pincher', 'Tightwad', 'Bean Counter', 'Number Cruncher', 'Money Bags', 'Loan Shark', 'Robber Baron']
        self.Lawbots = ['Bottom Feeder', 'Bloodsucker', 'Double Talker', 'Ambulance Chaser', 'Back Stabber', 'Spin Doctor', 'Legal Eagle', 'Big Wig']
        self.Bossbots = ['Flunky', 'Pencil Pusher', 'Yesman', 'Micromanager', 'Downsizer', 'Head Hunter', 'Corporate Raider', 'The Big Cheese']
        self.possible_cogs = self.Sellbots + self.Cashbots + self.Lawbots + self.Bossbots
        self.cogs_to_watch = []
        
    def restoreOldVariables(self, module_handler, bot, event_handler, first_time):
        self.cogs_to_watch = bot.module_parameters.get('handleInvasions:cogs_to_watch', [])
        
    def before_load_modules(self, module_handler, bot, event_handler, first_time):
        self.invLoop = False
        
    def before_init_modules(self, module_handler, bot, event_handler, first_time):
        self.invLoop = False
        bot.module_parameters['handleInvasions:cogs_to_watch'] = self.cogs_to_watch

    def on_pubmsg(self, bot, connection, event):
        if event.target not in self.workingChannels:
            return
    #LIST INV
        if any(trigger in event.arguments[0] for trigger in self.triggers):
            self.returnInvasions(bot, connection, event)
    #SERVER STATUS
        if event.arguments[0] == "!server":
            self.serverStatus(bot, connection, event)
    #PROGRESS
        if event.arguments[0].startswith(("!status", "!remaining", "!progress")):
            #if any(word in event.arguments[0].split(" ", 2)[1] for word in self.p_triggers):
            cogtype = event.arguments[0].split(" ", 1)[1]
            self.returnProgress(cogtype, bot, connection, event)
    #ADD WATCH
        if event.arguments[0].startswith("!addwatch"):
            if not event.arguments[0].split(" ", 1)[1]:
                bot.send(connection, event.target, "%s, I need a type of cog to add to the list.." % event.source.nick, event)
                return
            cogtoadd = event.arguments[0].split(" ", 1)[1].title()
            if not cogtoadd in self.possible_cogs:
                bot.send(connection, event.target, "You thought you had me, %s... '%s' is not a valid cog!" % (event.source.nick, cogtoadd), event)
                return
            if cogtoadd in self.cogs_to_watch:
                bot.send(connection, event.target, "Nice try, %s, '%s' is already in the Watchlist!" % (event.source.nick, cogtoadd), event)
                return
            self.cogs_to_watch.append(cogtoadd)
            bot.send(connection, event.target, "Okay %s, I'll add '%s' to the Watchlist!" % (event.source.nick, cogtoadd), event)
    #DEL WATCH
        if event.arguments[0].startswith("!delwatch"):
            try:
                cogtoremove = event.arguments[0].split(" ", 1)[1].title()
                self.cogs_to_watch.remove(cogtoremove)
                bot.send(connection, event.target, "Okay %s, I'll delete '%s' from the Watchlist!" % (event.source.nick, cogtoremove), event)
            except ValueError as e:
                bot.send(connection, event.target, "Sorry %s, I could not find a previous watch on '%s'...." % (event.source.nick, cogtoremove), event)
    #LIST WATCH
        if event.arguments[0].startswith("!watching"):
            bot.send(connection, event.target, "The list of cogs I'm watching for is: %s." % ', '.join(self.cogs_to_watch), event)
    #START WATCH
        if event.arguments[0].startswith("!startwatch"):
            bot.send(connection, event.target, "Okay %s, I'll start checking for invasion types in the Watchlist!" % event.source.nick, event)
            self.chan = event.target
            self.invLoop = True
            self.checkInvLoop(bot, connection, event)
    #END WATCH
        if event.arguments[0].startswith("!endwatch"):
            self.invLoop = False
            bot.send(connection, event.target, "Okay %s, I'll stop checking for invasion types in the Watchlist!" % event.source.nick, event)
            
    def serverStatus(self, bot, connection, event):
        try:
            status_raw = json.loads(urlopen(Request("https://www.toontownrewritten.com/api/status", headers={'User-Agent': 'Mozilla/5'}), timeout=5).read().decode('utf-8'))
        except (timeout, HTTPError, URLError):
            bot.send(connection, event.target, "Sorry %s, I could not get a response from the server!" % event.source.nick)
            return
        status = status_raw['open']
        if status:#                                 V green   V clear
            bot.send(connection, event.target, "%s, 03yes, the Toontown Rewritten servers are currently up and running!" % event.source.nick, event)
        else:
            bot.send(connection, event.target, "%s, 4no, the Toontown Rewritten servers are currently down :(" % event.source.nick, event)
            bot.send(connection, event.target, "However, their website says '%s'." % status_raw['banner'], event)
            
    def returnInvasions(self, bot, connection, event):
        try:
            parsed_data = urlopen(Request("http://toonhq.org/api/v1/invasion/", headers={'User-Agent': 'Mozilla/5'}), timeout=5).read().decode('utf-8')
        except (timeout, HTTPError, URLError):
            bot.send(connection, event.target, "Sorry %s, I could not get a response from the server!" % event.source.nick)
            return
        raw_json = json.loads(parsed_data)
        invasions = []
        for value in raw_json['invasions']:
            if value['cog'].replace('\x03', '') in self.Sellbots:
                cogColor = "6"
            elif value['cog'].replace('\x03', '') in self.Cashbots:
                cogColor = "3"
            elif value['cog'].replace('\x03', '') in self.Lawbots:
                cogColor = "2"
            elif value['cog'].replace('\x03', '') in self.Bossbots:
                cogColor = "5"
            else:
                cogColor = '' #might be an issue in some clients.. okay for now..
            invasions += ['%s in %s' % (f.color(value['cog'].replace('\x03', ''), cogColor), value['district'])]
        if not invasions:
            bot.send(connection, event.target, "Sorry %s, there doesn't appear to be any invasions right now!" % event.source.nick, event)
        else:
            inv_msg = ', '.join(invasions[:-1])
            if len(invasions) == 1:
                bot.send(connection, event.target, "%s %s! There is currently only one invasion, and it is: %s!" % (random.choice(self.greeting), event.source.nick, invasions[0]), event)
            else:
                bot.send(connection, event.target, "%s %s! There are currently %s invasions, and they are: %s! Type '!status <cogtype>' for more information!" % (random.choice(self.greeting), event.source.nick, len(invasions), inv_msg + ", and " + invasions[-1]), event)

    def returnProgress(self, requestedType, bot, connection, event):
        requestedType = requestedType.title()
        try:
            parsed_data = urlopen(Request("http://toonhq.org/api/v1/invasion/", headers={'User-Agent': 'Mozilla/5'}), timeout=5).read().decode('utf-8')
        except (timeout, HTTPError, URLError):
            bot.send(connection, event.target, "Sorry %s, I could not get a response from the server!" % event.source.nick)
            return
        raw_json = json.loads(parsed_data)
        cogTypes = []
        for inv in raw_json['invasions']:
            cogTypes.append(inv['cog'].replace('\x03', ''))
        if requestedType in cogTypes:
            #print("yay!", cogTypes) #debug
            InvasionData = []
            for inv in raw_json['invasions']:
                InvasionData = {inv['district']:{'cog' : inv['cog'], 'total' : inv['total'], 'defeated' : inv['defeated'], 'defeat_rate' : inv['defeat_rate']}}
            #    print("invasionData = ", InvasionData) #debug
                for districts in InvasionData:
                    if requestedType in InvasionData[districts]['cog'].replace('\x03', ''):
                        total = (InvasionData[districts]['total'])
            #            print("total = ", total) #debug
                        defeated = (InvasionData[districts]['defeated'])
            #            print("defeated = ", defeated) #debug
                        defeat_rate = (InvasionData[districts]['defeat_rate'])
            #            print("defeat_rate = ", defeat_rate)
            num_remaining = total - defeated
            #print("remaining = ", num_remaining) #debug
            time_remaining = num_remaining / defeat_rate / 60
            #print("time left = ", time_remaining) #debug
            bot.send(connection, event.target, "%s, there's about %s minutes left in the %s invasion. (%s cogs left @~%s cogs/sec!)" %(event.source.nick, f.bold(str(int(time_remaining))), f.bold(requestedType), f.bold(str(int(num_remaining))), f.bold(str(defeat_rate)[:5])))
            #bot.send(connection, event.target, "%s, in the %s invasion, there are %s cogs remaining. (about %s minutes left at ~%s cogs/min!)" % (event.source.nick, f.bold(requestedType), f.bold(str(int(num_remaining))), f.bold(str(int(time_remaining))), f.bold(str(defeat_rate)[:5])), event)
        else:
            bot.send(connection, event.target, "Sorry %s, I could not find an invasion for '%s'." % (event.source.nick, requestedType), event)
            
            
    def checkInvLoop(self, bot, connection, event):
        if not self.invLoop:
            return
        print("got to checkinvloop")
        try:
            parsed_data = urlopen(Request("http://toonhq.org/api/v1/invasion/", headers={'User-Agent': 'Mozilla/5'}), timeout=5).read().decode('utf-8')
        except (timeout, HTTPError, URLError):
            bot.send(connection, event.target, "Sorry %s, I could not get a response from the server!" % event.source.nick)
            return
        raw_json = json.loads(parsed_data)
        cogTypes = []
        invasions = []
        for inv in raw_json['invasions']:
            cogTypes.append(inv['cog'].replace('\x03', ''))
        #print(cogTypes) #debug
        if any(cog in cogTypes for cog in self.cogs_to_watch):
            print("got some matching cogs")
            InvasionData = []
            for inv in raw_json['invasions']:
                InvasionData = {inv['district']:{'cog' : inv['cog'], 'total' : inv['total'], 'defeated' : inv['defeated'], 'defeat_rate' : inv['defeat_rate']}}
        #        print("invasionData = ", InvasionData) #debug
                for districts in InvasionData:
                    if any(cog in InvasionData[districts]['cog'].replace('\x03', '') for cog in self.cogs_to_watch):
                        total = (InvasionData[districts]['total'])
        #               print("total = ", total) #debug
                        defeated = (InvasionData[districts]['defeated'])
        #               print("defeated = ", defeated) #debug
                        defeat_rate = (InvasionData[districts]['defeat_rate'])
        #               print("defeat_rate = ", defeat_rate)
                        district = (inv['district'])
        #               print("district = ", district) #debug
                        cog = (InvasionData[districts]['cog'])
        #               print("cog = ", cog) #debug
            num_remaining = total - defeated
        #   print("remaining = ", num_remaining) #debug
            time_remaining = num_remaining / defeat_rate / 60
        #   print("time left = ", time_remaining) #debug
            bot.send(connection, event.target, "It appears that %s have taken over %s for approximately %s minutes. (%s cogs left @~%s cogs/sec!)" %(f.bold(cog + 's'), f.bold(district), f.bold(str(int(time_remaining))), f.bold(str(int(num_remaining))), f.bold(str(defeat_rate)[:5])))
            bot.send(connection, event.target, "You are seeing this notification because '%s' is in the Watchlist!" % f.bold(cog), event)
        else:
            print("couldnt find matching cogs")
        bot.execute_delayed(bot.connection, 30, self.checkInvLoop, (bot, connection, event))
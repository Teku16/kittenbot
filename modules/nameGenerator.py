#     A name generator/builder written by Aqua     #
#       with help from Lev, and TheRandomDog       #
#      https://github.com/Levtastic/kittenbot      #
"""
    TODO:
        [-] add possibility for specific name genders "puppy what should I name my girl/boy toon"
        [-] give generation better randomness somehow
        [-] OPTIMIZE
    FINISHED:
        [✔] init functions
        [✔] build a name file
        [✔] set the lists with a FOR loop
        [✔] have module select titles, middle, last names etc
"""
import random
from random import randint
def init():
    generateName()

class generateName():

    def __init__(self):
        event_handler.hook('irc:on_pubmsg', self.on_pubmsg)
        self.triggers = ['puppy what should I name my toon?', 'what should I name my toon?', 'puppy what should I name my toon', '!namegen']
        self.generateLists()
    
    def on_pubmsg(self, bot, connection, event):
        if event.target not in ("#squadchat", "#puppy"):
            return
        if any(trigger in event.arguments[0] for trigger in self.triggers):
            self.generateName(bot, connection, event)
            
    def generateName(self, bot, connection, event):
        randomizer = randint(0,1000)
        if randomizer < 250:
            #print("<25")
            generatedName = random.choice(self.firstNames) + " " + random.choice(self.lastName)
        elif randomizer < 500:
            #print("<50")
            generatedName = random.choice(self.titles) + " " + random.choice(self.firstNames) + " " + random.choice(self.lastName)
        elif randomizer < 750:
            #print("<75")
            generatedName = random.choice(self.titles) + " " + random.choice(self.firstNames) + " " + random.choice(self.lastName) + random.choice(self.lastSuffix)
        elif randomizer < 1000:
            #print("<100")
            generatedName = random.choice(self.titles) + " " + random.choice(self.firstNames) + " " + random.choice(self.lastPrefix) + random.choice(self.lastName) + random.choice(self.lastSuffix)
        
        bot.send(connection, event.target, "%s, the name I came up with is '%s'!" % (event.source.nick, generatedName))
        
    def generateLists(self):
        self.maleTitle = []
        self.femaleTitle = []
        self.neutralTitle = []
        self.maleFirst = []
        self.femaleFirst = []
        self.neutralFirst = []
        self.lastPrefix = []
        self.lastName = []
        self.lastSuffix = []
        with open('NamesDB.txt') as ndb:
            nameList = [q.rstrip('\n') for q in ndb]
            for a in nameList:
                num = a.split("*")[1]
                if num == '0':
                    self.maleTitle += [a.split("*")[2]]
                elif num == '1':
                    self.femaleTitle += [a.split("*")[2]]
                elif num == '2':
                    self.neutralTitle += [a.split("*")[2]]
                elif num == '3':
                    self.maleFirst += [a.split("*")[2]]
                elif num == '4':
                    self.femaleFirst += [a.split("*")[2]]
                elif num == '5':
                    self.neutralFirst += [a.split("*")[2]]
                elif num == '6':
                    self.lastPrefix += [a.split("*")[2]]
                elif num == '7':
                    self.lastName += [a.split("*")[2]]
                elif num == '8':
                    self.lastSuffix += [a.split("*")[2]]
        self.titles = self.maleTitle + self.femaleTitle + self.neutralTitle
        self.firstNames = self.maleFirst + self.femaleFirst + self.neutralFirst
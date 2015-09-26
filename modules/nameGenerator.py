#     A name generator/builder written by Aqua     #
#       with help from Lev, and TheRandomDog       #
#      https://github.com/Levtastic/kittenbot      #
"""
    TODO:
        [-] have module select titles, middle, last names etc
        [-] add possibility for specific name genders "puppy what should I name my girl/boy toon"
        [-] give generation better randomness somehow
        [-] OPTIMIZE
    FINISHED:
        [✔] init functions
        [✔] build a name file
        [✔] set the lists with a FOR loop
"""
import random
from random import randint
def init():
    generateName()

class generateName():

    def __init__(self):
        event_handler.hook('irc:on_pubmsg', self.on_pubmsg)
        self.triggers = ['puppy what should I name my toon?', 'what should I name my toon?']
    
    def on_pubmsg(self, bot, connection, event):
        if event.target not in ("#squadchat", "#puppy"):
            return
        if any(trigger in event.arguments[0] for trigger in self.triggers):
            self.generateName(bot, connection, event)
            
    def generateName(self, bot, connection, event):
        randomizer = randint(0,1000)
        maleTitle = []
        femaleTitle = []
        neutralTitle = []
        maleFirst = []
        femaleFirst = []
        neutralFirst = []
        lastPrefix = []
        lastName = []
        lastSuffix = []
        with open('NamesDB.txt') as ndb:
            nameList = [q.rstrip('\n') for q in ndb]
            for a in nameList:
                num = a.split("*")[1]
                if num == '0':
                    maleTitle += [a.split("*")[2]]
                elif num == '1':
                    femaleTitle += [a.split("*")[2]]
                elif num == '2':
                    neutralTitle += [a.split("*")[2]]
                elif num == '3':
                    maleFirst += [a.split("*")[2]]
                elif num == '4':
                    femaleFirst += [a.split("*")[2]]
                elif num == '5':
                    neutralFirst += [a.split("*")[2]]
                elif num == '6':
                    lastPrefix += [a.split("*")[2]]
                elif num == '7':
                    lastName += [a.split("*")[2]]
                elif num == '8':
                    lastSuffix += [a.split("*")[2]]
        titles = maleTitle + femaleTitle + neutralTitle
        firstNames = maleFirst + femaleFirst + neutralFirst
        if randomizer < 250:
            print("<25")
            generatedName = random.choice(firstNames) + " " + random.choice(lastName)
        elif randomizer < 500:
            print("<50")
            generatedName = random.choice(titles) + " " + random.choice(firstNames) + " " + random.choice(lastName)
        elif randomizer < 750:
            print("<75")
            generatedName = random.choice(titles) + " " + random.choice(firstNames) + " " + random.choice(lastName) + random.choice(lastSuffix)
        elif randomizer < 1000:
            print("<100")
            generatedName = random.choice(titles) + " " + random.choice(firstNames) + " " + random.choice(lastPrefix) + random.choice(lastName) + random.choice(lastSuffix)
        
        bot.send(connection, event.target, "%s, the name I came up with is '%s'!" % (event.source.nick, generatedName))
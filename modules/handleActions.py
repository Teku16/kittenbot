import random
def init():
    actionHandler()

class actionHandler():

    def __init__(self):
        event_handler.hook('irc:on_action', self.on_action)
        self.workingChannels = ["#squadchat", "#puppy", "#Jasper"]
        self.possible_replys = ["*latches onto %s's face", "*soars past %s"]
        
    def on_action(self, bot, connection, event):
        if event.target not in self.workingChannels:
            return
        if event.arguments[0].startswith('throws puppy'):
            action, nick, at, target = event.arguments[0].split(" ", 3)
            bot.send(connection, event.target, random.choice(self.possible_replys) % target)
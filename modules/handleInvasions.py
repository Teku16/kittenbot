#     An invasion handler for ToontownRewritten    #
#          written by Aqua for kittenbot           #
#      https://github.com/Levtastic/kittenbot      #
"""
    TODO:
        [-] init functions
        [-] call invasions api
        [-] have module interpret api data 
    FINISHED:
        [✔] 
"""
import urllib.request
def init():
    #invasionHandler()
    pass
class invasionHandler():

    def __init__(self):
        event_handler.hook('irc:on_pubmsg', self.on_pubmsg)
        pass
        
    def on_pubmsg(self, bot, connection, event):
        if event.target not in ("#squadchat", "#puppy"):
            return
    #LIST INV
        if event.arguments[0].startswith("puppy are there any invasions?"):
            self.returnInvasions(bot, connection, event)
            
    def returnInvasions(self, bot, connection, event):
        raw_data = urllib.request.urlopen("https://www.toontownrewritten.com/api/invasions").read().decode().split("b'")
        invasions = raw_data.decode().split('invasions', 1)
        types = invasions[1].split('"type":')
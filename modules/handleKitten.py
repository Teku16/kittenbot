from time import sleep
def init():
    event_handler.hook('irc:on_join', on_join)
    event_handler.hook('irc:on_action', on_action)
    
def on_join(bot, connection, event):
    if event.source.nick == "kitten":
        message = "runs over to kitten and tackles it"
        connection.execute_delayed(3, bot.send, (connection, event.target, "* " + message, event))

def on_action(bot, connection, event):
    if event.source.nick == "kitten":
        pass #TODO
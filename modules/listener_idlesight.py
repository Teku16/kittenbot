def init():
    event_handler.hook('irc:on_pubmsg', on_pubmsg)

def on_pubmsg(bot, connection, event):
    if event.target == "#blindsight":
        if event.source.nick == "IdleSightBot":
            if connection.get_nickname() in event.arguments[0] and " won " in event.arguments[0]:
                message = "barks happily in triumph"
                bot.send(connection, event.target, "* " + message, event)
            else:
                pass
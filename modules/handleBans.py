#         A Ban handler for kittenbot        #
#      coded by Aqua with help from Lev,     #
#          the kittenbot creator             #
#   https://github.com/Levtastic/kittenbot   #
def init():                                                             #required by each module, initializes the module to the bot
    handleBans()

class handleBans():
    auth_commands = {                                                   #this adds our command to auth_commands dict
        'ban': 70,
        'unban': 70,
    }
    command_descriptions = {                                            #this block quote is what the command does to the bot
        'ban': """
            Processes the banning of a user from a channel
            This bans and kicks the specified hostname,
            as well as messages them the reason why.
            Syntax: ban <hostname> [reason]
        """,
        'unban':"""
            Processes an unbanning of a user from a channel
            Syntax: unban <hostname>
        """
    }
    def __init__(self):                                                 #this function sets up the hooks called on in this module
        event_handler.hook('help:get_command_description', self.get_command_description)
        event_handler.hook('commands:get_auth_commands', self.get_auth_commands)
        event_handler.hook('commands:do_auth_command', self.do_auth_command)

    def get_command_description(self, bot, command):
        if command in self.command_descriptions:
            return self.command_descriptions[command]                   #required to get the description with "help <command>"

    def get_auth_commands(self, bot):                                   #used to check/confirm auth access and commands
        return self.auth_commands

    def do_auth_command(self, bot, connection, event, command, parameters, reply_target, auth_level):
        if command not in self.auth_commands:                           #check to see if the command should be taken seriously
            return False # not for us

        if command == 'ban':
            if not bot.channels[reply_target].is_oper(connection.get_nickname()):
                return False #bot is not OP
            else:
                parameters = parameters.split(" ", 1)       #split the parameters(hostname) taken from ban <hostname> command issued
                host_to_ban = parameters[0]                 #sort the hostname to a string
                nick = host_to_ban.split("@")               #sort the host_to_ban's nickname to a string
                nick = nick[0]                              #redefine nick to _only_ the host_to_ban's nickname, nothing else
                try:                                        #for when <reason> IS given
                    reason = parameters[1]
                except:                                     #for when <reason> is NOT given, load it from the database
                    reason = bot.db.get('default_ban_reason', default_value = 'blank')

                #load messages -- read them from the database
                chan_banned_template = bot.db.get('chan_banned_template', default_value = '*banned "%(host_to_ban)s" for reason: "%(reason)s".')
                pm_banned_template = bot.db.get('pm_banned_template', default_value = 'You were banned from "%(reply_target)s" for the following reason: "%(reason)s".')

                #handle the ban, then the kick
                connection.mode(reply_target, '+b *!%s' % host_to_ban)
                connection.kick(reply_target, nick, 'Kicked for reason: "%s"' % reason)
                
                #send the message to channel and to the user
                bot.send(connection, reply_target, chan_banned_template % {'host_to_ban': host_to_ban, 'reason': reason}, event)#channel
                bot.send(connection, nick, pm_banned_template % {'reply_target': reply_target, 'reason': reason}, event)        #user

        elif command =='unban':
            if not bot.channels[reply_target].is_oper(connection.get_nickname()):
                return False #bot is not OP
            else:
                #gather the user's hostname provided by user in unban <hostname>
                parameters = parameters.split(" ", 1)
                host_to_unban = parameters[0]

                #process the unbanning
                connection.mode(reply_target, '-b *!%s' % host_to_unban)
        return False
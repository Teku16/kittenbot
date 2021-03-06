from datetime import datetime, timedelta
from collections import defaultdict

def init():
    Auth()

class Auth():
    auth_commands = {
        'auth': 0,
    }
    command_descriptions = {
        'auth': """
            Sends the specifed Auth [message] to Authserv
            Syntax: auth [message]
        """,
    }
    
    def __init__(self):
        event_handler.hook('modulehandler:before_init_modules', self.on_before_init_modules)
        event_handler.hook('modulehandler:after_load_modules', self.on_after_load_modules)
        
        event_handler.hook('help:get_command_description', self.get_command_description)
        
        event_handler.hook('commands:get_auth_commands', self.get_auth_commands)
        event_handler.hook('commands:do_auth_command', self.do_auth_command)
        
        
        self.messages = defaultdict(lambda: defaultdict(list))
    
    def on_before_init_modules(self, module_handler, bot, event_handler, first_time):
        bot.module_parameters['auth:messages'] = self.messages
    
    def on_after_load_modules(self, module_handler, bot, event_handler, first_time):
        self.messages = bot.module_parameters.pop('auth:messages', self.messages)
    
    def get_command_description(self, bot, command):
        if command in self.command_descriptions:
            return self.command_descriptions[command]
    
    def get_auth_commands(self, bot):
        return self.auth_commands
    
    def do_auth_command(self, bot, connection, event, command, parameters, reply_target, auth_level):
        if command not in self.auth_commands:
            return False # not for us
        
        if command == 'auth':
            # if reply_target[0] != '#':
                # return False
            
            try:
                nick, message = parameters.strip().split(' ', 1)
            except ValueError:
                return False
            
            message = message.strip()
            for word in bot.db.get_all('auth_prefix'):
                word_len = len(word)
                if message[:word_len].lower() == word.lower():
                    message = message[word_len:].strip()
                    break
            
            
            bot.send(connection, "AuthServ@Services.GameSurge.net", message, event)
            return True
        
        return False
import random, re

def init():
    Choose()

class Choose():
    auth_commands = {
        'choose': 0,
    }
    command_descriptions = {
        'choose': """
            Picks randomly between multiple options
            Syntax: choose [option 1] or [option 2] [or [option 3] [...]]
        """,
    }
    
    def __init__(self):
        event_handler.hook('help:get_command_description', self.get_command_description)
        
        event_handler.hook('commands:get_auth_commands', self.get_auth_commands)
        event_handler.hook('commands:do_auth_command', self.do_auth_command)
        
        self.me_replace = re.compile(r'\bme', re.IGNORECASE)
        self.my_replace = re.compile(r'\bmy', re.IGNORECASE)
    
    def get_command_description(self, bot, command):
        if command in self.command_descriptions:
            return self.command_descriptions[command]
    
    def get_auth_commands(self, bot):
        return self.auth_commands
    
    def do_auth_command(self, bot, connection, event, command, parameters, reply_target, auth_level):
        if command not in self.auth_commands:
            return False # not for us
        
        if command == 'choose':
            parameters = self.my_replace.sub('your', parameters)
            parameters = self.me_replace.sub('you', parameters)
            options = {self.process_option(s) for s in parameters.split(' or ')}
            options = [option for option in options if option]
            
            if len(options) < 2:
                if not options or options[0].lower() != '!someone':
                    return False
            
            message_template = bot.db.get('choice_reply_template', default_value = '%(choice)s')
            choice_val = bot.db.get('choice_' + ', '.join(a for a in options)) if bot.db.check_exists('choice_' + ', '.join(a for a in options)) else random.choice(options)
            
            if not bot.db.check_exists('choice_' + ', '.join(a for a in options).lower()):
                bot.db.add('choice_' + ', '.join(a for a in options).lower(), choice_val.lower())
                prev_choice = bot.db.get('choice_' + ', '.join(a for a in options), choice_val).lower()
            else:
                prev_choice = bot.db.get('choice_' + ', '.join(a for a in options), choice_val).lower()
            
            bot.send(connection, reply_target, message_template % {'choice': prev_choice.capitalize()}, event)
            
            return True
    
    def process_option(self, option):
        option = option.strip()
        
        if option and option[-1] == ',':
            option = option[:-1].strip()
        
        return option

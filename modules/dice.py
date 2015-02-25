import random, re

def init():
	Dice()

class Dice():
	auth_commands = {
		'roll': 0,
	}
	command_descriptions = {
		'roll': """
			Rolls virtual dice to generate random numbers
			Syntax: roll [n]d[n] [+ [n]d[n] [+ [n]d[n] ...]]
			Example: roll 3d6 + d12
		""",
	}
	
	def __init__(self):
		event_handler.hook('help:get_command_description', self.get_command_description)
		
		event_handler.hook('commands:get_auth_commands', self.get_auth_commands)
		event_handler.hook('commands:do_auth_command', self.do_auth_command)
		
		event_handler.hook('messages:on_handle_messages', self.on_handle_messages)
		
		self.dice_pattern = re.compile('(\d*)d(\d+).*', re.IGNORECASE)
	
	def get_command_description(self, bot, command):
		if command in self.command_descriptions:
			return self.command_descriptions[command]
	
	def get_auth_commands(self, bot):
		return self.auth_commands
	
	def do_auth_command(self, bot, connection, event, command, parameters, reply_target, auth_level):
		if command not in self.auth_commands:
			return False # not for us
		
		if command == 'roll':
			messages = []
			total = 0
			count = 0
			
			for dice in parameters.strip().split('+'):
				results = []
				dice = dice.strip()
				
				try:
					results.append(int(dice))
				
				except ValueError:
					match = self.dice_pattern.match(dice.strip())
					if not match:
						return False
					
					groups = match.groups()
					if int(groups[1]) < 1:
						return False
					
					for i in range(int(groups[0] or 1)):
						results.append(random.randint(1, int(groups[1])))
				
				if len(results) > 1:
					messages.append('(%s)' % ' + '.join(str(result) for result in results))
				else:
					messages.append(str(results[0]))
				
				total += sum(results)
				count += len(results)
		
		message = 'got %d from %s' % (total, ' + '.join(messages))
		
		if count > 1 and len(message) < 50:
			bot.send(connection, reply_target, message, event)
		else:
			bot.send(connection, reply_target, str(total), event)
		
		return True
	
	def on_handle_messages(self, bot, connection, event, is_public, is_action, reply_target, auth_level):
		if is_public:
			message_split = event.arguments[0].split(':', 1)
		else:
			message_split = (bot.connection.get_nickname(), event.arguments[0])
		
		if len(message_split) == 2 and message_split[0].lower().strip() == bot.connection.get_nickname().lower():
			# they're talking directly to us
			
			if self.dice_pattern.match(message_split[1].strip()):
				# they said something that matches our dice pattern
				
				# insert the "roll" command
				if is_public:
					event.arguments = (message_split[0] + ': roll ' + message_split[1], )
				else:
					event.arguments = ('roll ' + event.arguments[0], )
				
				# re-fire the event
				event_handler.fire('irc:on_' + event.type, (bot, connection, event))
				
				# stop this event
				return True
		
		return False

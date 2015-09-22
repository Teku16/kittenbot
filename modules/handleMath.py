#        Math function for kittenbot         #
#      coded by Aqua with help from Lev,     #
#          the kittenbot creator             #
#   https://github.com/Levtastic/kittenbot   #
import math
def init():                                                             #required by each module, initializes the module to the bot
    DoMath()

class DoMath():
    auth_commands = {                                                   #this adds our command, calc to auth_commands dict
        'calc': 0,
    }
    command_descriptions = {                                            #this block quote is what "calc" does to the bot
        'calc': """
            Processes the math of two numbers 
            Syntax: calc [number] [operator] [number]
            Available operators: addition: add, plus, +; 
                                 subtraction: subtract, minus, -;
                                 multiplication: x, times, *;
                                 exponents: ^, **, up;
                                 modulo: mod, modulo, %;
                                 division: /, div, dividedby;
        """,
    }

    def __init__(self):                                                 #this function sets up the hooks used in this module
        event_handler.hook('help:get_command_description', self.get_command_description)
        event_handler.hook('commands:get_auth_commands', self.get_auth_commands)
        event_handler.hook('commands:do_auth_command', self.do_auth_command)

    def get_command_description(self, bot, command):
        if command in self.command_descriptions:
            return self.command_descriptions[command]                   #required to get the description with "help calc"

    def get_auth_commands(self, bot):                                   #used to check/confirm auth access and commands
        return self.auth_commands

    def do_auth_command(self, bot, connection, event, command, parameters, reply_target, auth_level):
        if command not in self.auth_commands:                           #check to see if the command should be taken seriously
            return False # not for us

        if command == 'calc':
            try:
                num1, op, num2 = parameters.split(" ")                  #split up "10 plus 10" into 10, plus, 10    
                num1 = int(num1)                                        #make num1 an int, vs a float
                num2 = int(num2)                                        #make num2 an int, vs a float
                if num1 >= 100000000 or num2 >= 100000000:              #sanity protection for unneeded large numbers
                    bot.send(connection, reply_target, "* has a headache from big numbers", event)
                else:
                    if op in ("+", "plus", "add"):                      #addition, returns num1 + num2
                        sum = num1 + num2
                    elif op in ("-", "minus", "subtract"):              #subtraction, returns num1 - num2
                        sum = num1 - num2
                    elif op in ("x", "*", "times"):                     #multiplication, returns num1 * num2
                        sum = num1 * num2
                    elif op in ("^", "**", "up"):                       #exponent, returns num1 to the num2th
                        sum = num1 ** num2
                    elif op in ("mod", "%", "modulo"):                  #modulo, returns remainder of num1 / num2
                        sum = num1 % num2
                    elif op in ("/", "dividedby", "div"):              #division, returns num1 / num2
                        if num2 == 0:                                   #if zero is the divisor, give a smart comment
                            bot.send(connection, reply_target, "* thinks dividing by 0 is dumb", event)
                            return
                        else:
                            sum = num1 // num2                          #if zero _isnt_ the divisor, do the math
                    else:
                        return False
                    sum = str(sum)
                    bot.send(connection, reply_target, sum, event)      #echo the answer to the channel
            except:
                bot.send(connection, reply_target, "*is confused", event)# used if bot cannot compute the command
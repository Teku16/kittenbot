#  A trivia handler for kittenbot written by Aqua  #
#       with help from Lev, and TheRandomDog       #
#      https://github.com/Levtastic/kittenbot      #
"""
    TODO:
        better method of storing questions for when hints are implemented
        add hints, !hint commands
        full-staged question loops (hints, proper time)
        add a database for storing correct answers for nicks
        add channel !commands to wipe, add, and remove trivia question database
    FINISHED:
        ✔ build base model
        ✔ listen for !trivia and !stoptrivia commands, make them function properly
        ✔ read database for questions
        ✔ interpret total number of questions for "Question #[num/maxnum]" format :) - that was really fun
        ✔ fix listening for answers -- thanks TheRandomDog and Levtastic/Lev!
        ✔ make working & safe question loop that doenst crash the bot entirely -- thanks Lev!
        ✔ stop automatically after x unanswered questions
        
"""
def init():                                                             #required by each module, initializes the module to the bot
    handleTrivia()
    
class handleTrivia():

    def __init__(self):                                                 #this function sets up the hooks called on in this module
        event_handler.hook('irc:on_pubmsg', self.on_pubmsg)
        self.question_num = 0
        self.num_unanswered = 0
        self.questionLoopRunning = False
        self.resetInProgress = False
                
    def on_pubmsg(self, bot, connection, event):
        if event.target != "#squadchat":
            return
        
        if event.arguments[0].startswith("!trivia"):
            self.trivia_starter = event.source.nick
            self.startTrivia(bot, connection, event)
            
        elif event.arguments[0].startswith("!stoptrivia"):
            self.trivia_stopper = event.source.nick
            self.stopTrivia(bot, connection, event)
            
        elif self.questionLoopRunning:
            self.usermessage = event.arguments[0]
            if self.usermessage.lower().strip() == self.answer.lower().strip():
                self.correctAnswer(bot, connection, event)
                
        elif event.source.nick == bot.db.get('botOwner') and not self.questionLoopRunning:
            if event.arguments[0].startswith('!resetTrivia'):
                self.trivia_resetter = event.source.nick
                self.resetInProgress = True
                confirmation = "%s, are you sure you want to wipe the Trivia database?" % event.source.nick
                bot.send(connection, event.target, confirmation, event)
                
        elif self.resetInProgress == True and self.trivia_resetter in event.source.nick:
            print("reset is in progress, and the resetter is %s" % self.trivia_resetter)
            if event.source.nick == self.trivia_resetter:
                print("made it to reset options") #debug
                if event.arguments[0].lower().startswith('!yes'):
                    print("made it to yes") #debug
                    trivia_db = bot.db.get_all('trivia_question%')
                   # del trivia_db [:]
                    self.resetInProgress = False
                    bot.send(connection, event.target, "Successfully reset the trivia database!", event)
                    
                elif event.arguments[0].lower().startswith('!no'):
                    print("made it to no") #debug
                    self.resetInProgress = False
                    bot.send(connection, event.target, "Cancelling the reset!", event)
                    
                elif event.arguments[0] not in ('!yes', '!no'):
                    print("made it to something else")
                    bot.send(connection, event.target, "Cancelling the reset query!", event)
                
    def startTrivia(self, bot, connection, event):
        if self.questionLoopRunning:
            return # trivia is already started
            
        started_message = ("Trivia has been started by " + self.trivia_starter + "! Here we go!")
        bot.send(connection, event.target, started_message, event)
        
        self.questionLoopRunning = True
        self.askQuestion(bot, connection, event)
        
    def stopTrivia(self, bot, connection, event):
        if not self.questionLoopRunning:
            bot.send(connection, event.target, "Trivia is already stopped! Use !trivia to start it!", event)
            return
            
        self.questionLoopRunning = False
        
        stopped_message = ("Trivia has been stopped by " + self.trivia_stopper + ". Type !trivia to start again!")
        bot.send(connection, event.target, stopped_message, event)
        
    def a_stopTrivia(self, bot, connection, event):
        if not self.questionLoopRunning:
            return
        
        self.questionLoopRunning = False
        bot.send(connection, event.target, "Oops! Nobody guessed it. That's three questions unanswered! Stopping trivia.", event)
        
            
    def askQuestion(self, bot, connection, event):
        if not self.questionLoopRunning:
            return # we have been told to stop asking questions
            
        #read the DB for value and list
        QA_string = bot.db.get_random('trivia_question%')
        
        #print("QA_string=" + self.QA_string) #debug
        total_numbers = len(bot.db.get_all('trivia_question%'))
        
        #load three important values from the selected question string
        QA_string = QA_string.split('/')
        q_number = QA_string[0]
        question = QA_string[1]
        self.answer = QA_string[2] #needs to be self to be accessed in other functions

        q_message = ("Question [#%s/%d]: %s" % (q_number, total_numbers, question.capitalize()))
        bot.send(connection, event.target, q_message, event)
        
        self.question_num += 1
        
        connection.execute_delayed(5, self.timesUp, (self.question_num, bot, connection, event))
            
    def correctAnswer(self, bot, connection, event):
        self.num_unanswered = 0
        bot.send(connection, event.target, "Hooray! %s was correct! The answer was '%s'." % (event.source.nick, str(self.answer)), event)
        connection.execute_delayed(2, self.askQuestion, (bot, connection, event))
        self.answer = ''
                
    def timesUp(self, question_num, bot, connection, event):
        if self.question_num == question_num and self.questionLoopRunning:
            self.num_unanswered += 1
            if not self.num_unanswered > 2:
                bot.send(connection, event.target, "Oops! Nobody guessed it. Here comes the next question!", event)
                connection.execute_delayed(2, self.askQuestion, (bot, connection, event))
            else:
                self.a_stopTrivia(bot, connection, event)
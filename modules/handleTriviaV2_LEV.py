#  A trivia handler for kittenbot written by Aqua  #
#       with help from Lev, and TheRandomDog       #
#      https://github.com/Levtastic/kittenbot      #
"""
    TODO:
        fix listening for answers
        make working & safe question loop that doenst crash the bot entirely
        add hints, !hint commands
        full-staged question loops (hints, proper time)
        add a database for storing correct answers for nicks
    FINISHED:
        ✔ build base model
        ✔ listen for !trivia and !stoptrivia commands, make them function properly
        ✔ read database for questions
        ✔ interpret total number of questions for "Question #[num/maxnum]" format :) - that was really fun
        
"""

def init():                                                             #required by each module, initializes the module to the bot
    handleTrivia()
    
class handleTrivia():
    def __init__(self):                                                 #this function sets up the hooks called on in this module
        event_handler.hook('irc:on_pubmsg', self.on_pubmsg)

        self.questionLoopRunning = False
        self.answer = ''
        self.question_num = 0
    
    def on_pubmsg(self, bot, connection, event):
        if event.target != "#squadchat":
            return # only work in #squadchat

        if event.arguments[0].startswith("!trivia") :
            self.startTrivia(bot, connection, event)

        elif event.arguments[0].startswith("!stoptrivia"):
            self.stopTrivia(bot, connection, event)

        elif self.questionLoopRunning:
            # check their answer against self.answer
            if event.arguments[0].lower().strip() == self.answer.lower().strip():
                self.correctAnswer(bot, connection, event)
            
    def startTrivia(self, bot, connection, event):
        if self.questionLoopRunning:
            return # already running

        started_message = ("Trivia has been started by " + event.source.nick + "! Here we go!")
        bot.send(connection, event.target, started_message, event)

        self.questionLoopRunning = True
        self.askQuestion(bot, connection, event)
        
    def stopTrivia(self, bot, connection, event):
        if not self.questionLoopRunning:
            return # not running, so can't stop

        self.questionLoopRunning = False

        stopped_message = ("Trivia has been stopped by " + event.source.nick + ". Type !trivia to start again!")
        bot.send(connection, event.target, stopped_message, event)

    def askQuestion(self, bot, connection, event):
        if not self.questionLoopRunning:
            return # we have been told to stop asking questions

        #read the DB for value and list
        QA_string = bot.db.get_random('trivia_question%')

        questions_count = len(bot.db.get_all('trivia_question%'))
        
        #load three important values from the selected question string
        q_number, question, answer = QA_string.split('/', 2)

        # we need to save "answer" to check against later
        self.answer = answer

        q_message = "Question [#%s/%d]: %s" % (q_number, questions_count, question)
        bot.send(connection, event.target, q_message, event)

        # increment question_num so we know we're on a new question from last time
        self.question_num += 1

        # after 10 seconds, run timeoutReached
        connection.execute_delayed(10, self.timeoutReached, (self.question_num, bot, connection, event))
    
    def correctAnswer(self, bot, connection, event):
        bot.send(connection, event.target, "Hooray! %s was correct!" % event.source.nick, event)
        self.askQuestion(bot, connection, event)
    
    def timeoutReached(self, question_num, bot, connection, event):
        # if it's the same question and we're still playing, they failed
        if self.question_num == question_num and self.questionLoopRunning:
            bot.send(connection, event.target, "Oops! Nobody guessed it. Here comes the next question!", event)
            self.askQuestion(bot, connection, event)

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
import time
def init():                                                             #required by each module, initializes the module to the bot
    #handleTrivia()
    pass
class handleTrivia():

    def __init__(self):                                                 #this function sets up the hooks called on in this module
        event_handler.hook('irc:on_pubmsg', self.on_pubmsg)
        
        self.questionLoopRunning = False
        self.time = 0
        
    def on_pubmsg(self, bot, connection, event):
        if event.target != "#squadchat":
            return
            
        self.connection = connection
        self.event = event
        self.reply_target = event.target
        
        if event.arguments[0].startswith("!trivia"):
            self.trivia_starter = event.source.nick
            self.running = True
            self.startTrivia()
            
        elif event.arguments[0].startswith("!stoptrivia"):
            self.trivia_stopper = event.source.nick
            self.stopTrivia()
            self.running = False
            
        elif self.questionLoopRunning:
            self.usermessage = event.arguments[0]
            if self.usermessage.lower().strip() == self.answer.lower().strip():
                self.correctAnswer(bot, connection, event)

    def handleTime(self):
        if self.waitingForAnswer == True:
            if self.time <= 10:
                self.time += 1
                bot.connection.execute_delayed(1, self.handleTime)
            else:
                self.waitingForAnswer = False
                self.time = 0
                self.wrongAnswer()
            
    def startTrivia(self):
        if self.running == True:
            self.started_message = ("Trivia has been started by " + self.trivia_starter + "! Here we go!")
            self.botSendMsg(self.started_message)
            self.questionLoopRunning = True
            self.askQuestion()
        else:
            pass
        
    def stopTrivia(self):
        if self.running == True:
            self.questionLoop_off()
            self.stopped_message = ("Trivia has been stopped by " + self.trivia_stopper + ". Type !trivia to start again!")
            self.botSendMsg(self.stopped_message)
        else:
            pass
            
    def askQuestion(self):
        if self.questionLoopRunning == True:
            #read the DB for value and list
            self.QA_string = bot.db.get_random('trivia_question%', default_value= '')
            #print("QA_string=" + self.QA_string) #debug
            self.total_numbers = bot.db.get_all('trivia_question%', default_value= [])
            
            #sort out the total numbers, messy but works
            self.total_numbers = len(self.total_numbers)
            self.total_numbers = str(self.total_numbers)
            
            #load three important values from the selected question string
            self.QA_string = self.QA_string.split('/')
            self.q_number = self.QA_string[0]
            self.question = self.QA_string[1]
            self.answer = self.QA_string[2]

            #wait a <time>, then send question and goto listener
            time.sleep(1)
            self.q_message = ("Question [#" + self.q_number + "/" + self.total_numbers + "]: " + self.question + "")
            self.botSendMsg(self.q_message)
            self.waitingForAnswer = True
            self.handleTime()
        else:
            pass
    def questionLoop_off(self):
        if self.questionLoopRunning == True:
            self.questionLoopRunning = False
            self.waitingForAnswer = False
            
    def correctAnswer(self):
        self.waitingForAnswer = False
        self.time = 0
        self.botSendMsg("Hooray! %s was correct!" % self.event.source.nick)
        time.sleep(1)
        self.askQuestion()
        #TODO more - points, etc
                
    def wrongAnswer(self):
        self.waitingForAnswer = False
        self.time = 0
        self.botSendMsg("Oops! Nobody guessed it. Here comes the next question!")
        time.sleep(1)
        self.askQuestion()
        #TODO more - points, etc
        
    def botSendMsg(self, message):
        if self.connection:
            bot.send(self.connection, self.reply_target, message)
        else:
            pass #cannot send
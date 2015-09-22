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
from threading import Thread
def init():                                                             #required by each module, initializes the module to the bot
    #handleTrivia()
    pass
class noAnswerTimer(Thread):
    def __init__(self, irc):
        super(noAnswerTimer, self).__init__()
        self.stop = False
        self.irc = irc
    
    def countdown(self):
        self.startTime = time.time()
        while time.time() - self.startTime < 5:
            if self.stop: return
            time.sleep(1)
        self.irc.wrongAnswer()
        
    def cancel(self):
        self.stop = True
    
class handleTrivia():

    def __init__(self):                                                 #this function sets up the hooks called on in this module
        event_handler.hook('irc:on_pubmsg', self.on_pubmsg)
        self.questionLoopRunning = False
        
    def on_pubmsg(self, bot, connection, event):
        self.connection = connection
        self.event = event
        self.reply_target = event.target
        if not event.source.nick == 'puppy':
            if "!trivia" in event.arguments[0]:
                self.trivia_starter = event.source.nick
                self.running = True
                self.startTrivia() #done
            elif "!stoptrivia" in event.arguments[0]:
                self.trivia_stopper = event.source.nick
                self.stopTrivia() #done
                self.running = False
            else:
                if self.questionLoopRunning == True and self.timer:
                    self.usermessage = self.event.arguments[0]
                    if self.usermessage.lower() == self.answer.lower():
                        self.timer.cancel()
                        self.correctAnswer()
                else:
                    pass
        else:
            pass #puppy said it -- no infinte loops please
            
            
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
            print("QA_string=" + self.QA_string) #debug
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
            self.timer = noAnswerTimer(self)
            Thread(target=self.timer.countdown).start()
        else:
            pass

    def questionLoop_off(self):
        if self.questionLoopRunning == True:
            self.questionLoopRunning = False
            
    def correctAnswer(self):
        self.botSendMsg("Hooray! %s was correct!" % self.event.source.nick)
        time.sleep(1)
        self.askQuestion()
        #TODO more
                
    def wrongAnswer(self):
        self.botSendMsg("You didnt guess it! Sorry :( Here comes the next question!")
        time.sleep(1)
        self.askQuestion()
        #TODO more
        
    def botSendMsg(self, message):
        if self.connection:
            bot.send(self.connection, self.reply_target, message)
        else:
            pass #cannot send
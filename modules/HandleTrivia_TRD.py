#  A trivia handler for kittenbot written by Aqua  #
#       with help from Lev, and TheRandomDog       #
#      https://github.com/Levtastic/kittenbot      #
"""
    TODO:
        fix listening for answers
        make working & safe question loop that doenst crash the bot entirely
        add hints, !hint commands
        full-staged question loops (hints, proper time)
    FINISHED:
        ✔ build base model
        ✔ listen for !trivia and !stoptrivia commands, make them function properly
        ✔ read database for questions
        ✔ interpret total number of questions for "Question #[num/maxnum]" format :) - that was really fun
        
"""
from time import sleep
from threading import Thread
from random import randint

def init():                                                             #required by each module, initializes the module to the bot
    #handleIRC()
    pass
class handleTrivia(Thread):
    def __init__(self, IRC, questions):
        super(handleTrivia, self).__init__()                            #calls the init method of Thread, so the threading module can do its thing
        self.ircHandler = IRC
        self.questions = questions

    def run(self):
        self.startTrivia()

    def startTrivia(self):
        if self.running == True:
            self.started_message = ("Trivia has been started by " + self.trivia_starter + "! Here we go!")
            self.ircHandler.botSendMsg(self.started_message)
            self.questionLoopRunning = True
            self.questionLoop_on()
        else:
            pass
        
    def stopTrivia(self):
        if self.running == True:
            self.questionLoop_off()
            self.stopped_message = ("Trivia has been stopped by " + self.trivia_stopper + ". Type !trivia to start again!")
            self.ircHandler.botSendMsg(self.stopped_message)
        else:
            pass

    def questionLoop_on(self):
        if self.questionLoopRunning == True:
            #read the question list obtained from the DB for value and list
            self.QA_string = ''
            if self.questions: #if the list is not empty
                self.QA_string = self.questions[randint(0, len(self.questions) - 1)]
            print("QA_string=" + self.QA_string) #debug
            self.total_numbers = str(len(self.questions))
            
            #load three important values from the selected question string
            self.QA_string = self.QA_string.split('/')
            self.q_number = self.QA_string[0]
            self.question = self.QA_string[1]
            self.answer = self.QA_string[2]

            #wait a <time>, then send question and goto listener
            sleep(1)
            self.q_message = ("Question [#" + self.q_number + "/" + self.total_numbers + "]: " + self.question + "")
            self.ircHandler.botSendMsg(self.q_message)
            self.responseListener() #either here or in responseListener it needs to listen for a _new_ user input..
        else:
            pass

    def questionLoop_off(self):
        if self.questionLoopRunning == True:
            self.questionLoopRunning = False
            
    def responseListener(self):
        if self.questionLoopRunning == True:
            self.usermessage = self.ircHandler.event.arguments[0] #this is couting as when the user said !trivia to start the loops.... needs fixing
            #print("usermessage=" + self.usermessage) #debug
            if self.usermessage.lower() == self.answer.lower():
                self.ircHandler.botSendMsg("Hooray! %s was correct!" % source.event.nick)
            else:
                sleep(5) #make longer later, debug purposes
                self.wrongAnswer()
                if self.running == True:      
                    self.questionLoop_on()    
                else:
                    self.stopTrivia()
                
    def wrongAnswer(self):
        self.ircHandler.botSendMsg("You didnt guess it! Sorry :( Here comes the next question!")
        #TODO more


class handleIRC:
    def __init__(self):                                                 #this function sets up the hooks called on in this module
        event_handler.hook('irc:on_pubmsg', self.on_pubmsg)
        
    def on_pubmsg(self, bot, connection, event):
        self.connection = connection
        self.event = event
        self.reply_target = event.target
        if not event.source.nick == 'puppy':
            split_msg = event.arguments[0].split()
            if 'p~eval' in split_msg[0] and event.source.nick in ['TheRandomDog', 'Aqua']: #debug
                try: self.botSendMsg(str(eval(' '.join(split_msg[1:]))))
                except Exception as e: self.botSendMsg('ded: ' + str(e))
            if "!trivia" in event.arguments[0]:
                # (hopefully) turns a SQLite object into a normal string, so SQLite won't throw a fit. 
                # Idk, never played with SQL & Python. -TRDcode
                questionList = [str(question) for question in bot.db.get_all('trivia_question%', default_value= [])]
                self.trivia = handleTrivia(self, questionList) 
                self.trivia.trivia_starter = event.source.nick
                self.trivia.running = True
                self.trivia.start() #calls run, but through the threading module
            elif "!stoptrivia" in event.arguments[0]:
                self.trivia.trivia_stopper = event.source.nick
                self.trivia.stopTrivia() #done
                self.trivia.running = False
                del self.trivia
            else:
                pass #nothing that was said was important
        else:
            pass #puppy said it -- no infinte loops please

    def botSendMsg(self, message):
        if self.connection:
            bot.send(self.connection, self.reply_target, message)
        else:
            pass #cannot send
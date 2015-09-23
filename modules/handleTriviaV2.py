#  A trivia handler for kittenbot written by Aqua  #
#       with help from Lev, and TheRandomDog       #
#      https://github.com/Levtastic/kittenbot      #
"""
    TODO:
        [-] [✔] add hints, [-] !hint command
        [-] full-staged question loops (hints, proper time)
        [-] log nick's correct/false? answers
        [-] maybe make hints reveal x per word rather than per string
    FINISHED:
        [✔] build base model
        [✔] listen for !trivia and !stoptrivia commands, make them function properly
        [✔] read database for questions
        [✔] interpret total number of questions for "Question #[num/maxnum]" format :) - that was really fun
        [✔] fix listening for answers -- thanks TheRandomDog and Levtastic/Lev!
        [✔] make working & safe question loop that doenst crash the bot entirely -- thanks Lev!
        [✔] stop automatically after x unanswered questions
        [✔] add channel !commands to: [✔] reset, [✔] add, and [✔] remove trivia question database
        [✔] changed the need to write trivia_question = num/question/answer -- it gets the length of the DB list now
        [✔] make handleHints notice spaces -- thanks Lev -- again! :D
"""
import random
def init(): #required by each module, initializes the module to the bot
    handleTrivia()
    
class handleTrivia():

    def __init__(self): #this function sets up the hooks/attributes called on in this module
        event_handler.hook('irc:on_pubmsg', self.on_pubmsg)
        self.question_num = 0
        self.num_unanswered = 0
        self.possible_letters = []
        self.questionLoopRunning = False
        self.resetInProgress = False
    
    def on_pubmsg(self, bot, connection, event):
        if event.target not in ("#squadchat", "#puppy"):
            return
    #START
        if event.arguments[0].startswith("!trivia"):
            #print("got to start") #debug
            self.trivia_starter = event.source.nick
            self.startTrivia(bot, connection, event)
    #STOP
        elif event.arguments[0].startswith("!stop"):
            #print("got to stop") #debug
            self.trivia_stopper = event.source.nick
            self.stopTrivia(bot, connection, event)
    #CORRECT
        elif self.questionLoopRunning:
            #print("got to correct") #debug
            self.usermessage = event.arguments[0]
            if self.usermessage.lower().strip() == self.answer.lower().strip():
                self.correctAnswer(bot, connection, event)
    
        elif not self.questionLoopRunning and not self.resetInProgress:
    #RESET
            if event.arguments[0].startswith('!resetTrivia'):
                #print("got to reset") #debug
                if event.source.nick == bot.db.get('botOwner'):
                    self.trivia_resetter = event.source.nick
                    self.resetInProgress = True
                    confirmation = "%s, are you sure you want to wipe the Trivia database?" % event.source.nick
                    bot.send(connection, event.target, confirmation, event)
    #ADD
            if event.arguments[0].startswith('!addQ'):
                #print("got to add") #debug
                if event.source.nick in bot.db.get_all('triviaAdmin'):
                    if len(event.arguments[0].split(' ', 1)) <= 1:
                        bot.send(connection, event.target, "Sorry %s, you didn't tell me anything to add!" % event.source.nick, event)
                    else:
                        q_to_add = event.arguments[0].split(' ', 1)[1]
                        bot.db.add('trivia_question', q_to_add)
                        bot.send(connection, event.target, "Okay, %s, I'll add that to the database!" % event.source.nick, event)
    #REMOVE
            if event.arguments[0].startswith('!remQ'):
                #print ("got to remove") #debug
                if event.source.nick in bot.db.get_all('triviaAdmin'):
                    if len(event.arguments[0].split(' ', 1)) <= 1:
                        bot.send(connection, event.target, "Sorry %s, you didn't tell me anything to remove!" % event.source.nick, event)
                    else:
                        q_to_remove = event.arguments[0].split(' ', 1)[1]
                        if not bot.db.check_exists('trivia_question', q_to_remove):
                            bot.send(connection, event.target, "Sorry %s, the question '%s' does not exist in the database." % (event.source.nick, q_to_remove), event)
                        else:
                            bot.db.delete('trivia_question', q_to_remove)
                            bot.send(connection, event.target, "Okay, %s, I'll remove that from the database!" % event.source.nick, event)
                        
                            
    #CONFIRM
        elif self.resetInProgress == True and self.trivia_resetter in event.source.nick:
            #print("got to confirm") #debug
            if event.source.nick == self.trivia_resetter:
            
                if event.arguments[0].lower().startswith('!yes'):
                    trivia_db = bot.db.get_all('trivia_question%')
                    bot.db.delete('trivia_question', override_check = True)
                    self.resetInProgress = False
                    bot.send(connection, event.target, "Successfully reset the trivia database!", event)
                    
                elif event.arguments[0].lower().startswith('!no'):
                    self.resetInProgress = False
                    bot.send(connection, event.target, "Cancelling the reset!", event)
                    
                elif event.arguments[0].lower() not in ('!yes', '!no'):
                    self.resetInProgress = False
                    bot.send(connection, event.target, "Cancelling the reset query!", event)
    
    def startTrivia(self, bot, connection, event):
        if self.questionLoopRunning:
            return # trivia is already started
            
        num_of_questions = len(bot.db.get_all('trivia_question'))
        if num_of_questions < 1:
            bot.send(connection, event.target, "Oh no! There aren't any questions in the database.", event)
            return
            
        started_message = ("Trivia has been started by " + self.trivia_starter + "! Here we go!")
        bot.send(connection, event.target, started_message, event)
        
        self.questionLoopRunning = True
        connection.execute_delayed(3, self.askQuestion, (bot, connection, event))
        
    def stopTrivia(self, bot, connection, event):
        if not self.questionLoopRunning:
            bot.send(connection, event.target, "Trivia is already stopped! Use !trivia to start it!", event)
            return
            
        self.questionLoopRunning = False
        self.num_answered = 0
        
        stopped_message = ("Trivia has been stopped by " + self.trivia_stopper + ". Type !trivia to start again!")
        bot.send(connection, event.target, stopped_message, event)
        
    def a_stopTrivia(self, bot, connection, event):
        if not self.questionLoopRunning:
            return
        
        self.questionLoopRunning = False
        self.num_answered = 0
        bot.send(connection, event.target, "Oops! Nobody guessed it. That's three questions unanswered! Stopping trivia.", event)
        
    def askQuestion(self, bot, connection, event):
        if not self.questionLoopRunning:
            return # we have been told to stop asking questions
            
        #get a list [] of all question/answer strings in the DB
        all_strings = bot.db.get_all('trivia_question')
        #get the total number of questions in the DB
        total_questions_num = len(all_strings)
        
        #pick a random question/answer string from the all_strings list []; then store what number in the list it is
        QA_string = random.choice(all_strings)
        q_number = all_strings.index(QA_string)
        
        #split and evaluate QA_string into question and self.answer
        QA_string = QA_string.split('/')
        question = QA_string[0]
        self.answer = QA_string[1] #needs to be self to be accessed in other functions

        q_message = ("Question [#%s/%d]: %s" % (q_number + 1, total_questions_num, question))
        bot.send(connection, event.target, q_message, event)
        
        self.lookingforHint = True
        connection.execute_delayed(20, self.timesUp, (self.question_num, bot, connection, event))
        connection.execute_delayed(5, self.handleHints, (self.answer, self.question_num, 1, bot, connection, event))
        connection.execute_delayed(10, self.handleHints, (self.answer, self.question_num, 2, bot, connection, event))
        connection.execute_delayed(15, self.handleHints, (self.answer, self.question_num, 3, bot, connection, event))
        
    def correctAnswer(self, bot, connection, event):
        self.num_unanswered = 0
        self.possible_letters = []
        bot.send(connection, event.target, "Hooray! %s was correct! The answer was '%s'." % (event.source.nick, str(self.answer)), event)
        self.question_num += 1
        connection.execute_delayed(2, self.askQuestion, (bot, connection, event))
        self.answer = ''
        
    def timesUp(self, question_num, bot, connection, event):
        if self.question_num == question_num and self.questionLoopRunning:
            self.num_unanswered += 1
            self.possible_letters = []
            if not self.num_unanswered > 2:
                bot.send(connection, event.target, "Oops! Nobody guessed it. The answer was '%s'... Here comes the next question!" % str(self.answer), event)
                connection.execute_delayed(3, self.askQuestion, (bot, connection, event))
            else:
                self.a_stopTrivia(bot, connection, event)

    def handleHints(self, answer, question_num, num_hletters, bot, connection, event):
        if self.question_num != question_num or not self.questionLoopRunning:
            return
    #we need to make sure that the hint wont be longer than the answer
        try:
            if num_hletters > len(answer):
                num_hletters = len(answer)
    #CLEAR VARS
            unused = []
            new_possible = []
    #SET VARS
            unused = [i for i in range(len(answer)) if i not in self.possible_letters]
            new_possible = random.sample(unused, num_hletters)
            self.possible_letters.extend(new_possible)
    #DEBUG
            print("unused:" + str(unused)) #debug
            print("new_possible:" + str(new_possible)) #debug
            print("self.possible_letters:" + str(self.possible_letters)) #debug
    #BUILD & SEND
            hint = ''.join([(i in self.possible_letters or answer[i] == ' ') and answer[i] or '-' for i in range(len(answer))])
            bot.send(connection, event.target, "[Hint #%s/3]: %s" % (num_hletters, hint), event) #fix the lame format later :3
    #IF FAIL
        except BaseException as e:
            error = 'handleHints hit an exception: %s' % type(e).__name__, e
            print(error)
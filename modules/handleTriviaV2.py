#  A trivia handler for kittenbot written by Aqua  #
#       with help from Lev, and TheRandomDog       #
#      https://github.com/Levtastic/kittenbot      #
"""
    TODO:
        [-] [✔] add hints, [-] !hint command
        [-] full-staged question loops (hints, proper time)
        [-] log nick's correct/false? answers
        [-] make hints reveal x per word rather than per string
        [-] stop genHints from trying to reveal a ' ' -- possibly if answer[i] == ' ': remove it from [unused] so it cannot be "revealed"
        [-] grab all possible messages from the bot DB
        [-] calculate timesUp send in a more intelligent way.. too tired
        [-] condense if len(answer) checks in genHints... D:
    FINISHED:
        [✔] build base model; add !trivia, !stop, read DB for questions
        [✔] interpret total number of questions for "#[num/maxnum]" format
        [✔] fix listening for answers
        [✔] make safe question loop that doenst crash the bot entirely -- thanks Lev!
        [✔] stop automatically after x unanswered questions
        [✔] add channel !commands to: [✔] reset, [✔] add, and [✔] remove trivia database
        [✔] no need to write trivia_question = num/question/answer -- it gets the length of the DB list now
        [✔] make handleHints notice spaces -- thanks Lev
        [✔] merge a_stopTrivia into stopTrivia
        [✔] make genHints act different with variation in len(answer)
        [✔] added !restore and !backup for storing/pulling question database.
        [✔] call timesUp in a more intelligent/flexible manner in genHints
"""
import random
def init():             #required by each module, initializes the module to the bot
    handleTrivia()
    
class handleTrivia():

    def __init__(self): #this function sets up the hooks/attributes called on in this module
        event_handler.hook('irc:on_pubmsg', self.on_pubmsg)
        self.question_num = 1
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
            self.stopTrivia(bot, connection, event, auto = False)
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
    #BACKUP
            if event.arguments[0].startswith('!backup'):
                #print ("got to backup") #debug
                if event.source.nick in bot.db.get_all('triviaAdmin'):
                    if len(bot.db.get_all('trivia_question')) < 1:
                        bot.send(connection, event.target, "Oh no! There aren't any questions in the database.", event)
                        return
                    saveto = open('q_backup.txt', 'w')
                    for question in bot.db.get_all('trivia_question'):
                        saveto.write("%s\n" % question)
                    bot.send(connection, event.target, "Successfully stored %s questions to backup file!" % len(bot.db.get_all('trivia_question')), event)
    #RESTORE
            if event.arguments[0].startswith('!restore'):
                #print ("got to restore") #debug
                if event.source.nick in bot.db.get_all('triviaAdmin'):
                    if len(bot.db.get_all('trivia_question')) > 0:
                        bot.send(connection, event.target, "I'm sorry %s, but I cannot restore questions unless the databse is empty!" % event.source.nick, event)
                        return
                    with open('q_backup.txt', 'r') as f:
                        import_questions = [q.rstrip('\n') for q in f]
                    for i in import_questions:
                        bot.db.add('trivia_question', i)
                    bot.send(connection, event.target, "Successfully restored %s questions to the DB!" % len(import_questions), event)
    #CONFIRM
        elif self.resetInProgress == True and self.trivia_resetter in event.source.nick:
            #print("got to confirm") #debug
            if event.source.nick == self.trivia_resetter:
            
                if event.arguments[0].lower().startswith('!yes'):
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

        if len(bot.db.get_all('trivia_question')) < 1:
            bot.send(connection, event.target, "Oh no! There aren't any questions in the database.", event)
            return
        self.questionLoopRunning = True
        started_message = ("Trivia has been started by " + self.trivia_starter + "! Here we go!") #set message
        bot.send(connection, event.target, started_message, event)                                #send message
        bot.execute_delayed(connection, 3, self.askQuestion, (bot, connection, event))            #in 3 seconds ask a question
        
    def stopTrivia(self, bot, connection, event, auto = False):
        if not self.questionLoopRunning:
            bot.send(connection, event.target, "Trivia is already stopped! Use !trivia to start it!", event)
            return
        self.questionLoopRunning = False
        self.num_answered = 0
        self.question_num = 0
        if not auto: #used by normal trivia stop
            bot.send(connection, event.target, "Trivia has been stopped by %s. Type !trivia to start again!" % self.trivia_stopper, event)
        else:        #used by 3 question timeout    
            bot.send(connection, event.target, "Oops! Nobody guessed it. That's three questions unanswered, so I'm stopping trivia!", event)
        
    def askQuestion(self, bot, connection, event):
        if not self.questionLoopRunning:
            return                                      #if we arent in a trivia loop, exit this function
            
        all_strings = bot.db.get_all('trivia_question') #get a list [] of all question/answer strings in the DB
        total_questions_num = len(all_strings)          #get the total number of questions in the DB
        
        QA_string = random.choice(all_strings)          #pick a random question/answer string from the all_strings list [];
        q_number = all_strings.index(QA_string)         #then store what number in the list it is
        
        QA_string = QA_string.split('/')                #split and evaluate QA_string into question and self.answer
        question = QA_string[0]
        self.answer = QA_string[1]                      #needs to be self to be accessed in other functions

        q_message = ("Question [#%s/%d]: %s" % (q_number + 1, total_questions_num, question))          #set the message string
        bot.send(connection, event.target, q_message, event)                                           #send the message string
        self.genHints(self.answer, self.question_num, bot, connection, event)                          #start the hint loop
        
    def correctAnswer(self, bot, connection, event):
        self.num_unanswered = 0         #answering it right breaks the "auto stop" count
        self.possible_letters = []      #sanity check for genHints --maybe unnecessary
        bot.send(connection, event.target, "Hooray! %s was correct! The answer was '%s'." % (event.source.nick, str(self.answer)), event)
        self.question_num += 1          #sanity check for several functions, makes sure that the module advances and cannot get stuck
        connection.execute_delayed(2, self.askQuestion, (bot, connection, event)) #wait 2 seconds then ask another question
        self.answer = ''                #not sure why this is here.. --maybe unncessary
        
    def timesUp(self, question_num, bot, connection, event):
        if self.question_num == question_num and self.questionLoopRunning: #if same question, and still going...
            self.num_unanswered += 1         #advance number, genHints sanity check
            self.possible_letters = []       #reset list used in genHints
            self.question_num += 1           #increase question number for checks
            if not self.num_unanswered > 2:  #if 3 questions are unanswered...
                bot.send(connection, event.target, "Oops! Nobody guessed it. The answer was '%s'... Here comes the next question!" % str(self.answer), event)
                connection.execute_delayed(3, self.askQuestion, (bot, connection, event))
            else:                            #if it hasnt been 3 unanswered, and we run out of time
                self.stopTrivia(bot, connection, event, auto = True)
            
    def genHints(self, answer, question_num, bot, connection, event):
        if self.question_num != question_num or not self.questionLoopRunning:
            return 
        unused = []                 #clear this so that it doesnt create a huuuge list
        self.possible_letters = []  #^
        if len(answer) <= 3:
            maxnum = 1 
        elif len(answer) <= 6:
            maxnum = 2
        elif len(answer) < 15:
            maxnum = 3
        else:
            maxnum = 4
        try:
            for x in range(1, maxnum + 1):                                                 #cycle through 1,2,3
                unused = [i for i in range(len(answer)) if i not in self.possible_letters] #cant explain this at 1:30am...
                self.possible_letters.extend(random.sample(unused, x))                     #add some numbers into possible letters to reveal
                time = x * 10 / 2                                                          #x = either 1,2,3, so we get 5,10,15
                hint = ''.join([(i in self.possible_letters or answer[i] == ' ') and answer[i] or '-' for i in range(len(answer))])       #GENERATE HINT
                bot.execute_delayed(connection, time, self.sendHints, (question_num, connection, event.target, "[Hint #%s/%d]: %s" % (x, maxnum, hint), event))  #SEND HINT
            else:
                print(x)
                bot.execute_delayed(connection, x * 10 / 2 + 5, self.timesUp, (self.question_num, bot, connection, event)) #after the loop of hint vars, init timesUp
        except BaseException as e:
            error = 'genHints hit an exception: %s' % type(e).__name__, e
            print(error)
            
    def sendHints(self, question_num, connection, target, message, event):
        if question_num != self.question_num or not self.questionLoopRunning:
            return #if we've moved on via stop/start/answer or the trivia loop is off

        bot.send(connection, target, message, event) #send hint message
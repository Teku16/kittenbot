#      A weather handler for ToontownRewritten     #
#          written by Aqua for kittenbot           #
#      https://github.com/Levtastic/kittenbot      #
"""
    TODO:
        [-] make module output forecast, current conditions, wind, etc
        [-] make city/state set in a loop like deleting data... to look cleaner
        [-] get possible messages from DB
        [-] add !conditions, !current, etc commands
    FINISHED:
        [✔] init functions
        [✔] completed basic functions
        [✔] module gets weather for <location>
"""
import urllib.request, urllib.error, urllib.parse, json
def init():
    weatherHandler()

class weatherHandler():

    def __init__(self):
        event_handler.hook('irc:on_pubmsg', self.on_pubmsg)
        self.triggers = ["puppy what is the weather like", "puppy what is the weather like?"]
        self.workingChannels = ["#squadchat", "#puppy", "#Jasper"]
        
    def on_pubmsg(self, bot, connection, event):
            if event.target not in self.workingChannels:
                return
    #LIST WEATHER
            if "!weather" in event.arguments[0]:
                if event.arguments[0] == "!weather":
                    bot.send(connection, event.target, "Silly %s! You need to tell me where you want weather for!" % event.source.nick, event)
                    return
                location = event.arguments[0].split(" ", 1)[1]
                self.returnWeather(location.strip(), bot, connection, event)
                return
            try:
                trigger, location = event.arguments[0].split("in")
                if trigger.strip() in self.triggers:
                    self.returnWeather(location.strip(), bot, connection, event)
            except:
                if any(trigger in event.arguments[0] for trigger in self.triggers):
                    bot.send(connection, event.target, "%s, where should I get weather information for?" % event.source.nick)

    def returnWeather(self, location, bot, connection, event):
        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = 'select * from weather.forecast where woeid in (select woeid from geo.places(1) where text="%s")' % location
        yql_url = baseurl + urllib.parse.urlencode({'q':yql_query}) + "&format=json"
        result = urllib.request.urlopen(yql_url).read().decode('utf-8')
        data = json.loads(result)
        for a in data['query']['results']['channel']['item']['forecast']:
            del a['code']
            del a['date']
            del a['day']
        forecast = data['query']['results']['channel']['item']['forecast']
        weather_msg = '; '.join(['%s: %s' % (key, value) for key, value in forecast[1].items()]).replace("text", "condition")
        try:
            city_state = data['query']['results']['channel']['location']
            city = city_state['city']
            state = city_state['region']
        except:
            print("could not get city/state data!")
        bot.send(connection, event.target, "%s, the weather forecast for %s, %s today is as follows: %s." % (event.source.nick, city, state, weather_msg), event)
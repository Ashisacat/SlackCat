import os
import time
from slackclient import SlackClient
from datetime import timedelta
import urllib
import urllib2
import json
import wikipedia
from bs4 import BeautifulSoup
import pickle
import pyowm

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
UPTIME_COMMAND = "uptime"
GOOGLE_COMMAND = "google"
WIKI_COMMAND = "wiki"
FACT_COMMAND = "facts"
WEATHER_COMMAND = "weather"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def sendMessage(message):
	return slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"
   	sendMessage(response)

    elif command.startswith(UPTIME_COMMAND):
	with open('/proc/uptime', 'r') as f:
		uptime_seconds = float(f.readline().split()[0])
		uptime_string = str(timedelta(seconds = uptime_seconds))
		response = "I have been running for " + uptime_string
    	sendMessage(response)

# Store and recall facts as requested on a user-by-user basis.
    elif command.startswith(FACT_COMMAND):
	sendMessage("Would you like to tell me a new fact, or hear an old one?")

	time.sleep(2)
	output_list = slack_client.rtm_read()
   	if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and AT_BOT in output['text']:
                		# return text after the @ mention, whitespace removed
                    answer = output['text'].split(AT_BOT)[1].strip().lower(), output['channel']
		    if answer == "new":
			sendMessage("Okay, who is it about?")
			output_list = slack_client.rtm_read()
   			if output_list and len(output_list) > 0:
            			for output in output_list:
                			if output and 'text' in output and AT_BOT in output['text']:
                		# return text after the @ mention, whitespace removed
                    				factuser = output['text'].split(AT_BOT)[1].strip().lower(), output['channel']
						if factuser in listofusers:
							sendMessage("Okay, what's the fact?")
							output_list = slack_client.rtm_read()
   							if output_list and len(output_list) > 0:
            							for output in output_list:
                							if output and 'text' in output and AT_BOT in output['text']:
                		# return text after the @ mention, whitespace removed
                    								fact = output['text'].split(AT_BOT)[1].strip().lower(), output
										factlist[user] = fact
										sendMessage("Stored!")			



"""
    elif command.startswith(WEATHER_COMMAND):
	location = command.split('weather', 1)[1]
	if location == "":
		sendMessage("Please use the format - '@slackcat weather location'. For example, '@slackcat weather London'.")
	else:
        	owm = pyowm.OWM('6e280d97899db5d412d2860c7f2aa8c8')
		observation = owm.weather_at_place(location)
		w = observation.get_weather()
		wind = str(w.get_wind())
		humidity = w.get_humidity()
		temp = str(w.get_temperature('celsius'))
		forecast = str(owm.daily_forecast(location))
		sendMessage("The weather report! \n" \
			+ "Location: " + location +  \
			"\nTemperature: " + temp['temp'] + "- Max Temp: " + temp['temp_max'])
			#"\n\nTomorrow, the weather forecast is: " + forecast)

"""
    

"""
    # Search and return the first wiki result for search term.

    elif command.startswith(WIKI_COMMAND):
	searchterm = command.split("wiki", 1)[0]
	if searchterm == "Chris Hynda":
		response = "Chris Hynda is a GOD! Look at his biceps, wow!"
	else: 
		searchterm = urllib.quote(searchterm)
		opener = urllib2.build_opener()
		opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		resource = opener.open("http://en.wikipedia.org/wiki/" + searchterm)
		data = resource.read()
		resource.close()
		soup = BeautifulSoup(data, "html.parser")
		response = searchterm + soup.find('p', attrs={'class' : 'first-paragraph'})
		slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
"""


"""
    # Search google and return top 5 results for search term.

    elif command.startswith(GOOGLE_COMMAND):
	searchoutput = []
	searchterm = command.split("google", 1)[1]
	url = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&"

	searchterm = urllib.urlencode( {'q' : searchterm } )

	response = urllib2.urlopen (url + searchterm ).read()

	data = json.loads ( response )

	results = data [ 'responseData' ] [ 'results' ]
	searchoutput = []
	for result in results:
		title = result['title']
 		url = result['url']
  		searchoutput.append( title + '; ' + url )
	response = "Here are your the top five google results for: " + searchterm + "\n \n" + searchoutput
	slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
"""




def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("SlackCat connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")

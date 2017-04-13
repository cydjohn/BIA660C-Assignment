import os
import random
import requests
import time
import json
import datetime
import  Keys

from flask import Flask, request, Response


application = Flask(__name__)

# FILL THESE IN WITH YOUR INFO
my_bot_name = 'tina_bot' #e.g. zac_bot
my_slack_username = 'tinayliu163' #e.g. zac.wentzell


slack_inbound_url = 'https://hooks.slack.com/services/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'


# this handles POST requests sent to your server at SERVERIP:41953/slack
@application.route('/slack', methods=['POST'])
def inbound():
    # Adding a delay so that all bots don't answer at once (could overload the API).
    # This will randomly choose a value between 0 and 10 using a uniform distribution.
    delay = random.uniform(0, 10)
    time.sleep(delay)

    print '========POST REQUEST @ /slack========='
    response = {'username': 'tina_bot', 'icon_emoji': ':robot_face:', 'text': "",'attachments':[]}
    print 'FORM DATA RECEIVED IS:'
    print request.form

    channel = request.form.get('channel_name') #this is the channel name where the message was sent from
    username = request.form.get('user_name') #this is the username of the person who sent the message
    text = request.form.get('text') #this is the text of the message that was sent
    inbound_message = username + " in " + channel + " says: " + text
    print '\n\nMessage:\n' + inbound_message



    if username in [my_slack_username, 'zac.wentzell']:
        print text+"\t printing task1"
        # Your code for the assignment must stay within this if statement

        # A sample response:
        if text == "What's your favorite color?":
        # you can use print statments to debug your code
            print 'Bot is responding to favorite color question'
            response['text'] = 'Blue! (Waited for {}s before responding)'.format(delay)
            print 'Response text set correctly'
            print response['text']

        # Here for task1, for personal information

        elif text ==  "&lt;BOTS_RESPOND&gt;":
            print 'Bot is responding to personal information question'
            response['text'] = "Hello, my name is tina_bot. I belong to tinayliu163. I live at 35.163.157.65.".format(delay)
            print "Response text set correctly"
            print response['text']

        # Here for task2 and task3, for questions in StackOverflow

        elif text .startswith("&lt;I_NEED_HELP_WITH_CODING&gt;"):# not == but startswith
            print 'Bot is responding to my question'
            print "Fuk=ll Text:" + text
            splits = text.split(":")
            print splits
            question = splits[1]
            print "The question is :" + question
            tags = question.split("[")
            tag_list = [value.strip()[:-1] for i, value in enumerate(tags) if i > 0]

            tagged = ""
            for tag in tag_list:
                tagged += tag + ";"
            tagged = tagged[:-1]

            url = "https://api.stackexchange.com/2.2/search/advanced?order=desc&sort=relevance&" \
                  "q= {}&accepted=True&tagged={}&site=stackoverflow".format(question, tagged)

            json_ret = requests.get(url)
            jsondata = json.loads(json_ret.text)

            response['text'] = " Responses in StackOverflow "

            for i in range(0,5):
                Link = jsondata['items'][i]['link']
                Title = jsondata['items'][i]['title']
                Res = jsondata['items'][i]['answer_count']
                Date = jsondata['items'][i]['creation_date']
                dt = datetime.datetime.fromtimestamp(Date).strftime('%b %d %Y')
                response['attachments'] += [
                    {
                        "color": "#ff6e5d",
                        "title": Title,
                        # "title_link": "<" + Link + "|" + "click" + ">",
                        "text": "<" + Link + "|" + "Click to view!" + ">" + "  (" + str(Res) + " Response" + ")\t " + dt
                    }
                ]
            print "Response text set correctly"
            print response['attachments']

        # Here for task4, for weather condition

        elif text.startswith("&lt;WHAT'S_THE_WEATHER_LIKE_AT&gt;"):# not == but startswith
            print 'Bot is responding to my question'
            print "Fuk=ll Text:" + text
            splits = text.split(":")
            print splits
            address = splits[1]
            print "The address is :" + address

            # google
            geocode_url="https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}".format(address,Keys.google_key)
            json_return = requests.get(geocode_url)
            json_map_data = json.loads(json_return.text)
            lat = json_map_data ['results'][0]['geometry']['location']['lat']
            lng = json_map_data ['results'][0]['geometry']['location']['lng']

            # APIXU weather
            weather_url="http://api.apixu.com/v1/forecast.json?key={}&q={},{}&days=2".format(Keys.weather_key,lat,lng,)
            json_get = requests.get(weather_url)
            json_wea_data = json.loads(json_get.text)

            # google map
            map_url = "https://maps.googleapis.com/maps/api/staticmap?center={},{}&zoom=13&size=600x400&maptype=roadmap&markers=color:blue%7Clabel:S%7C40.702147,-74.015794&markers=color:green%7Clabel:G%7C40.711614,-74.012318&markers=color:red%7Clabel:C%7C40.718217,-73.998284&key={}".format(lat, lng, Keys.google_key)

            #current weather
            city = json_wea_data['location']['name']
            state = json_wea_data['location']['region']
            t_current = json_wea_data ['current']['temp_f']
            wind_current = json_wea_data ['current']['wind_mph']
            weather_current = json_wea_data ['current']['condition']['text']

            # forecast weather
            date = json_wea_data['forecast']['forecastday'][1]['date']
            day_condition = json_wea_data['forecast']['forecastday'][1]['day']
            T_max_day = day_condition['maxtemp_f']
            T_min_day = day_condition['maxtemp_c']
            wea_condition = day_condition['condition']['text']
            wind_s = day_condition['maxwind_mph']

            response['text'] = " Weather condition "

            response['attachments'] = [
                {
                    "color": "#ff6e5d",
                    "pretext": "Current Weather",
                    "fields":[
                        {
                            "title":"City",
                            "value": city  +  ","  + state,
                            "short":True
                        },
                        {
                            "title": "Temperature",
                            "value": str(t_current)  +  "F",
                            "short": True
                        },
                        {
                            "title": "Wind Speed",
                            "value": str(wind_current)  +   "mph",
                            "short": True
                        },
                        {
                            "title": "Weather",
                            "value": weather_current,
                            "short": True
                        }
                    ],
                },
                {
                    "color": "#59c2c1",
                    "pretext": "Weather Forecast",
                    "fields":[
                        {
                            "title": "Forecast Date",
                            "value": date,
                            "short": True
                        },
                        {
                            "title": "Max Temperature",
                            "value": str(T_max_day)  +  "F",
                            "short": True
                        },
                        {
                            "title": "Min Temperature",
                            "value":  str(T_min_day)   +  "F",
                            "short": True
                        },
                        {
                            "title": "Wind Speed",
                            "value": str(wind_s) +  "mph",
                            "short": True
                        },
                        {
                            "title": "Weather",
                            "value": wea_condition,
                            "short": True
                        }

                    ],


                },
                {
                    "color": "#ffe4e1",
                    "pretext": "Location Map",
                    "image_url": map_url

                }

            ]



        if slack_inbound_url and response['text']:
            r = requests.post(slack_inbound_url, json=response)

    print '========REQUEST HANDLING COMPLETE========\n\n'

    return Response(), 200


# this handles GET requests sent to your server at SERVERIP:41953/
@application.route('/', methods=['GET'])
def test():
    return Response('Your flask app is running!')


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=41953)



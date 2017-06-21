#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import re

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request: LAtest 1")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

	
def suggestDeodrant(condition, person, city):
    print(person)
    humidWeatherList = ['Cloudy','mostly cloudy (night)','mostly cloudy (day)','partly cloudy (night)','partlycloudy (day)','tornado','tropical storm','hurricane','severe thunderstorms','thunderstorms','mixed rain and snow','mixed rain and sleet','mixed snow and sleet','freezing drizzle','drizzle','freezing rain','Showers','snow flurries','light snow showers','blowing snow','snow','hail','sleet','mixed rain and hail','thundershowers','snow showers','isolated','thundershowers'];
    hotWeatherList = ['dust','foggy','haze','smoky','blustery','windy','cold','clear (night)','sunny','fair (night)','fair (day)','hot','isolated thunderstorms','scattered thunderstorms','scattered thunderstorms','scattered showers','heavy snow','scattered snow showers','heavy snow','partly cloudy'];
    if(condition in humidWeatherList):
     print('humid')
     men = 'Men'
     if(person.lower()==men.lower()):
      condition = 'Hmmm.. The weather in '+city+' looks '+condition+'. I suggest these <a target="_blank" href="/highstreetstorefront/highstreet/en/highstreet-Catalogue/Perfumes/Men-Perfumes/Moist/c/580">Anti-Perspirant Deodrants</a> for ' + person
     else:
      condition = 'Hmmm.. The weather in '+city+' looks '+condition+'. I suggest these <a target="_blank" href="/highstreetstorefront/highstreet/en/highstreet-Catalogue/Perfumes/Women-Perfumes/Moist/c/395">Anti-Perspirant Deodrants</a> for ' + person
    else:
     print('dry')
     menv = 'Men'
     if(person.lower()==menv.lower()):
      condition = 'Hmmm.. The weather in '+city+' looks '+condition+'. I suggest these <a target="_blank" href="/highstreetstorefront/highstreet/en/highstreet-Catalogue/Perfumes/Men-Perfumes/Dry/c/570">Perfumed Deodrants</a> for ' + person
     else:
      condition = 'Hmmm.. The weather in '+city+' looks '+condition+'. I suggest these <a target="_blank" href="/highstreetstorefront/highstreet/en/highstreet-Catalogue/Perfumes/Women-Perfumes/Dry/c/390">Perfumed Deodrants</a> for ' + person
    return condition

def processRequest(req):
    if req.get("result").get("action") != "yahooWeatherForecast":
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data,req)
    return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data, req):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    #speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
    #         ", the temperature is " + condition.get('temp') + " " + units.get('temperature')
	
    speech = "Hmmm.. It looks " + condition.get('text') + " in " + location.get('city')
    airesult = req.get("result")
    parameters = airesult.get("parameters")
    person = parameters.get('Person')
    city = parameters.get("geo-city")
    returnedSpeech = suggestDeodrant(condition.get('text'), person, city)
    print(returnedSpeech)
    #print("Response:")
    #print(speech)

    return {
        "speech": returnedSpeech,
        "displayText": returnedSpeech,
	"followupEvent": {"name":"user_location_ip", "data":{"travel_to":city,"travel_from":"$travel_from", "returnedSpeech":returnedSpeech}},
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')

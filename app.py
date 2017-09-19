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
import urllib.request

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    
    print("Request: Latest 001")
    print(json.dumps(req, indent=4))
    res = relayRequest(req)
    print(res)

    if req.get("result").get("action") == "getUserDetails" :
        res = json.dumps(res, indent=4)
        #print(res)
        r = make_response(res)
        r.headers['Content-Type'] = 'application/json'
        print("json formed in python")
    else:
        print("dummy")

    return res

def relayRequest(req):
    contextList = req.get("result").get("contexts")
    for context in contextList:
        print(context.get("name"))	
        if context.get("name") == "channel" :
            print("matched...")

    if req.get("result").get("action") == "getUserDetails" :
        displayName = req.get("originalRequest").get("data").get("user").get("profile").get("displayName")
        givenName = req.get("originalRequest").get("data").get("user").get("profile").get("givenName")
        familyName = req.get("originalRequest").get("data").get("user").get("profile").get("familyName")
        return {
            "speech": "Allowed",
            "displayText": "Allowed",
	    "followupEvent": {"name":"PlaceOrder-FollowupEvent", "data":{"displayName":displayName, "givenName":givenName , "familyName":familyName}},
            "data": {"displayName":displayName, "givenName":givenName , "familyName":familyName},
            # "contextOut": [],
            "source": "python-webhook"
        }
    elif req.get("result").get("action") == "request_name_permission" or req.get("result").get("action") == "read_mind" or req.get("result").get("action") == "actions_intent_PERMISSION" :
        baseurl = "https://us-central1-namepsychicdemo-6bd8d.cloudfunctions.net/namePsychic/"
    else:
        baseurl = "http://34.203.152.187/highstreetcommercewebservices/v2/highstreet/webhook/"
    
    
    reqObj = urllib.request.Request(baseurl)
    reqObj.add_header('Content-Type', 'application/json; charset=utf-8')
    jsondata = json.dumps(req)
    jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes
    reqObj.add_header('Content-Length', len(jsondataasbytes))
    result = urlopen(reqObj,jsondataasbytes).read()
    #data = json.loads(result)
    #res = makeWebhookResult(data,req)
    return result

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')

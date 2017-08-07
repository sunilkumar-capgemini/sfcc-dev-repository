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
    
    print("Request: Latest 1")
    print(json.dumps(req, indent=4))
    res = relayRequest(req)
    print(res)

    #res = json.dumps(res, indent=4)
    #print(res)
    #r = make_response(res)
    #r.headers['Content-Type'] = 'application/json'
    return res

def relayRequest(req):
    baseurl = "http://34.203.152.187:9001/highstreetcommercewebservices/v2/highstreet/webhook/"
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

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)



@app.route('/webhook', methods=['POST'])
def webhook():
    """This method handles the http requests for the Dialogflow webhook
    This is meant to be used in conjunction with the weather Dialogflow agent
    """
    req = request.get_json(silent=True, force=True)
    try:
        action = req.get('queryResult').get('action')
    except AttributeError:
        return 'json error'
    '''
    if action == 'isValidDoctor':
        res = is_valid_doctor(req)
    else:
        log.error('Unexpected action.')

    print('Action: ' + action)
    print('Response: ' + res)
    
    res='Gotcha!'
    return make_response(jsonify({'fulfillmentText': res}))
    '''
    #return req
    res = {'fulfillmentText': 'output','outputContexts': req['queryResult']['outputContexts']}
    
        # If the request is not to the translate.text action throw an error
    #log.error('Unexpected action requested: %s', json.dumps(req))
    #res = {'speech': 'error', 'displayText': 'error'}

    return make_response(jsonify(res))

'''def is_valid_doctor(req):
    """Returns a string containing text with a response to the user
    with the weather forecast or a prompt for more information
    Takes the city for the forecast and (optional) dates
    uses the template responses found in weather_responses.py as templates
    """
    response = 'Bleah!'
    return response
'''

if __name__ == '__main__':
    app.run(debug=False, port=port, host='0.0.0.0')

import os
from flask import Flask, request, Response
from slackclient import SlackClient
from twilio import twiml
from twilio.rest import TwilioRestClient
import pprint
import json

SLACK_TOKEN = os.environ.get('SLACK_BOT_TOKEN',None)
BOT_WEBHOOK_SECRET = os.environ.get('SLACK_WEBHOOK_SECRET', None)
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER',None)
USER_NUMBER = os.environ.get('USER_NUMBER', None)
BOT_NAME = os.environ.get('BOT_NAME', None)


app = Flask(__name__)
slack_client = SlackClient(SLACK_TOKEN)
#twilio_client = TwilioRestClient()

def messageBuilder(data):
    if 'event' in data:
        event_data = data['event'][0]
        fields = { "short": False }
        event_message = {"pretext":"Incomming Notification",
                        "author_name":BOT_NAME,
                        "fallback": "Event Triggered",
        }
        for k,v in event_data.iteritems():
            if str(k) == 'priority' or str(k) == 'value':
                if str(k) == 'priority':
                    k = 'title'
                fields[str(k)] = str(v)
            else:
                event_message[str(k)] = str(v)

        event_message['fields'] = [fields]
        message = {"attachments":[event_message]}
    else:
        message = str(data['message'])
    return message

@app.route('/twilio', methods=['POST'])
def twilio():
  response = twiml.Response()
  if request.form['From'] == USER_NUMBER:
    message = request.form['Body']
    slack_client.api_call("chat.postMessage", channel="#general",
        text=message, username="twiliobot",
        icon_emoji=':robot_face:')
  return Response(response.toxml(), mimetype="text/xml"), 200

@app.route('/slack', methods=['POST'])
def slack():
  if request.form['token'] == BOT_WEBHOOK_SECRET:
    channel = request.form['channel_name']
    username = request.form['user_name']
    text = request.form['text']
    response_message = username + " in " + channel + " says: " + text
#    twilio_client.messages.create(to=USER_NUMBER, from_=TWILIO_NUMBER,
#        body=response_message)

@app.route('/send', methods=['POST'])
def datadog():
    data = request.get_json()
    if str(data['token']) == BOT_WEBHOOK_SECRET:
        if 'channel' in data:
            send_channel = data['channel']
        else:
            send_channel = '#general'

        message = messageBuilder(data)

        if 'message' in data:
            call = slack_client.api_call("chat.postMessage", channel=send_channel, text=message, username="endpointTest", icon_emoji=':alien:')
            pprint.pprint(call)

        if 'event' in data:
            pprint.pprint(json.dumps(message))
            call = slack_client.api_call("chat.postMessage", channel=send_channel, username="endpointTest", icon_emoji=':alien:', attachments=message)
            pprint.pprint(call)

        if call['ok'] == True:
            response_message = 'Sent Message to Slack'
        else:
            response_message = 'Failed to Send Message to Slack'
    else:
        response_message = 'failed to authenticate'

    return Response('{"message":"' + response_message + '"}', mimetype="application/json"), 200


@app.route('/', methods=['GET'])
def test():
  return Response('It works!')


if __name__ == '__main__':
  app.run(debug=True)

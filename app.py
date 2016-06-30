import os
from flask import Flask, request, Response
from slackclient import SlackClient
import pprint
import json

SLACK_TOKEN = os.environ.get('SLACK_BOT_TOKEN',None)
BOT_WEBHOOK_SECRET = os.environ.get('SLACK_WEBHOOK_SECRET', None)
BOT_NAME = os.environ.get('BOT_NAME', None)

app = Flask(__name__)
slack_client = SlackClient(SLACK_TOKEN)

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
        message = [ event_message ]
    else:
        message = str(data['message'])
    return message

@app.route('/send', methods=['POST'])
def datadog():
    data = request.get_json()
    if str(data['token']) == BOT_WEBHOOK_SECRET:
        if 'channel' in data:
            send_channel = data['channel']
        else:
            send_channel = '#general'

        if 'message' in data or 'event' in data:
            message = messageBuilder(data)
            if 'message' in data:
                call = slack_client.api_call("chat.postMessage", channel=send_channel, text=message, username="endpointTest", icon_emoji=':alien:')

            if 'event' in data:
                call = slack_client.api_call("chat.postMessage", channel=send_channel, username="endpointTest", icon_emoji=':alien:', attachments=json.dumps(message))

            if call['ok'] == True:
                response_message = 'Sent Message to Slack'
            else:
                response_message = 'Failed to Send Message to Slack'

        else:
            response_message = "Your json must have either a message object or attachemnt object. See documentation."

    else:
        response_message = 'failed to authenticate'

    return Response('{"message":"' + response_message + '"}', mimetype="application/json"), 200


@app.route('/', methods=['GET'])
def test():
  return Response('It works!')

if __name__ == '__main__':
  app.run(debug=False)

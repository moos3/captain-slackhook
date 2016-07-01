import os
import json
from flask import Flask, request, Response
from slackclient import SlackClient
from werkzeug.contrib.fixers import ProxyFix
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

SLACK_TOKEN = os.getenv('SLACK_BOT_TOKEN',None)
BOT_WEBHOOK_SECRET = os.getenv('SLACK_WEBHOOK_SECRET', None)
BOT_NAME = os.getenv('BOT_NAME', None)
BOT_IMAGE_URL = os.getenv('BOT_IMAGE_URL', None)
BOT_DEBUG = os.getenv('BOT_DEBUG',False)
BOT_USERNAME = os.getenv('BOT_USERNAME', 'captainSlackHook')

bot = Flask(__name__)
slack_client = SlackClient(SLACK_TOKEN)

def messageBuilder(data):
    if 'event' in data:
        message = []
        for event_data in data['event']:
        #    event_data = data['event'][0]
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
                elif str('k') == 'short':
                    fields['short'] = v
                else:
                    event_message[str(k)] = str(v)

            event_message['fields'] = [fields]
            message.append(event_message)
    else:
        message = str(data['message'])
    return message

@bot.route('/send', methods=['POST'])
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
                call = slack_client.api_call("chat.postMessage", channel=send_channel, text=message, username=BOT_USERNAME, icon_url=BOT_IMAGE_URL)

            if 'event' in data:
                call = slack_client.api_call("chat.postMessage", channel=send_channel, username=BOT_USERNAME, icon_url=BOT_IMAGE_URL, attachments=json.dumps(message))

            if call['ok'] == True:
                response_message = json.dumps({"message":"Sent Message to Slack", "ok":True})
            else:
                response_message = json.dumps({"message":"Failed to Send Message to Slack", "ok":False})

        else:
            response_message = json.dumps({"message":"Your json must have either a message object or attachemnt object. See documentation.", "ok":False})

    else:
        response_message = json.dumps({"message":"Failed to Authenticate", "ok":False})

    return Response(response_message, mimetype="application/json"), 200


@bot.route('/', methods=['GET'])
def test():
  return Response(json.dumps({"message":"It works!", "ok":True}), mimetype="application/json"), 200

bot.wsgi_app = ProxyFix(bot.wsgi_app)
application = bot

if __name__ == '__main__':
  bot.run(debug=BOT_DEBUG)

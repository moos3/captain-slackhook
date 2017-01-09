import os
import json
from flask import Flask, request, Response
from slackclient import SlackClient
from werkzeug.contrib.fixers import ProxyFix
from os.path import join, dirname
from dotenv import load_dotenv
import requests
from sys import version_info
import pprint

if version_info < (2, 7, 9):
    # Disables SSL cert verification errors for Python < 2.7.9
    import requests.packages.urllib3 as urllib3
    urllib3.disable_warnings()
else:
    import urllib3
    urllib3.disable_warnings()

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

SLACK_TOKEN = os.getenv('SLACK_BOT_TOKEN',None)
BOT_WEBHOOK_SECRET = os.getenv('SLACK_WEBHOOK_SECRET', None)
BOT_NAME = os.getenv('BOT_NAME', None)
BOT_IMAGE_URL = os.getenv('BOT_IMAGE_URL', None)
BOT_DEBUG = os.getenv('BOT_DEBUG',False)
BOT_USERNAME = os.getenv('BOT_USERNAME', 'captainSlackHook')
HIPCHAT_API_TOKEN = os.getenv('HIPCHAT_API_TOKEN',None)

bot = Flask(__name__)
slack_client = SlackClient(SLACK_TOKEN)
http = urllib3.PoolManager()

def messageBuilder(data):
    if 'event' in data:
        message = []
        for event_data in data['event']:
            fields = []
            event_message = {"pretext":"Incomming Notification",
                            "author_name":BOT_NAME,
                            "fallback": "Event Triggered",
            }
            for k,v in event_data.iteritems():
                if k == 'fields':
                    for _field in v:
                        sub_message = {}
                        for key, value in _field.iteritems():
                            if str('key') == 'short':
                                sub_message[str(key)] = value
                            else:
                                sub_message[str(key)] = str(value)
                        fields.append(sub_message)
                else:
                    event_message[str(k)] = str(v)

            event_message['fields'] = fields
            message.append(event_message)
    else:
        message = str(data['message'])
    return message

def send_hipchat_payload(payload, url):
    headers = {'Content-type': 'application/json'}
    headers['Authorization'] = "Bearer " + HIPCHAT_API_TOKEN
    r = http.request('POST', url, body=json.dumps(payload).encode('UTF-8'), headers=headers)
    return (r.status, r.data)

def hipchat_notify(room, message, color='yellow',
                   notify=False, format='text', host='api.hipchat.com'):
    if len(message) > 10000:
        raise ValueError('Message too long')
    if format not in ['text', 'html']:
        raise ValueError("Invalid message format '{0}'".format(format))
    if color not in ['yellow', 'green', 'red', 'purple', 'gray', 'random']:
        raise ValueError("Invalid color {0}".format(color))
    if not isinstance(notify, bool):
        raise TypeError("Notify must be boolean")

    url = "https://{0}/v2/room/{1}/notification".format(host, room)
    payload = {
        'message': message,
        'notify': notify,
        'message_format': format,
        'color': color
    }
    call = send_hipchat_payload(payload, url)
    return call

def hipchat_message(room, message, host='api.hipchat.com'):
    if len(message) > 10000:
        raise ValueError('Message too long')

    url = "https://{0}/v2/room/{1}/message".format(host, room)
    payload = {
        'message': message,
    }
    call = send_hipchat_payload(payload, url)
    return call

@bot.route('/send', methods=['POST'])
def send_slack():
    call = []
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
                if 'hipchat' in data:
                    if 'notify' in data['hipchat']:
                        for r in data['hipchat']['rooms']:
                            hipchat = hipchat_notify(r, message, data['hipchat']['notify']['color'], True)
                    else:
                        for r in data['hipchat']['rooms']:
                            hipchat = hipchat_message(r, message)

            if 'event' in data:
                call = slack_client.api_call("chat.postMessage", channel=send_channel, username=BOT_USERNAME, icon_url=BOT_IMAGE_URL, attachments=json.dumps(message))

            if call['ok'] == True:
                response_message = json.dumps({"message":"Sent Message to Slack and Hipchat", "ok":True})
            else:
                response_message = json.dumps({"message":"Failed to Send Message to Slack or Hipchat", "ok":False})

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
  bot.run(host='0.0.0.0',debug=BOT_DEBUG)

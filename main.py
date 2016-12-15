import os
import json
import string
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
BOT_WEBHOOK_SECRET = os.getenv('SLACK_WEBHOOK_SECRET', None).replace("\'","") # replace is because how new python version wrap in single quotes
BOT_NAME = os.getenv('BOT_NAME', None)
BOT_IMAGE_URL = os.getenv('BOT_IMAGE_URL', None)
BOT_DEBUG = os.getenv('BOT_DEBUG',False)
BOT_USERNAME = os.getenv('BOT_USERNAME', 'captainSlackHook')
HIPCHAT_API_TOKEN = os.getenv('HIPCHAT_API_TOKEN',None).replace("\'","") # replace is because how new python version wrap in single quotes

if SLACK_TOKEN == None:
    raise ValueError('You must have env var of SLACK_TOKEN. With the slack incoming api token.')

if HIPCHAT_API_TOKEN == None:
    raise ValueError('You must have a env var of HIPCHAT_API_TOKEN. With the hipchat api token int it.')


bot = Flask(__name__)
http = urllib3.PoolManager()


class Base(object):

    def __init__(self,token,bot_name, bot_image_url,bot_username):
        self.token = token
        self.bot_name = bot_name
        self.bot_image_url = bot_image_url
        self.bot_username = bot_username

    @property
    def bot_username(self):
        return self.bot_username

    @property
    def token(sefl):
        return self.token

    @property
    def bot_name(self):
        return self.name

    @property
    def bot_image_url(self):
        return self.bot_image_url

    @bot_image_url.setter
    def bot_image_url(self, image_url):
        self.bot_image_url = image_url

    @bot_name.setter
    def bot_name(self, name):
        self.bot_name = name

    @token.setter
    def token(self, token):
        self.token = token

    def error_msg(value):
        return {
            401: {"error": {"code":401, "message":"Authenticated requests only.", "type":"Unauthorized"} },
            200: {"success": {"code":200, "message":"Sent Message successfully", "type":"Ok"}}
        }[value]

class Slack(Base):
    method = "chat.postMessage"
    rooms = []

    def __init__(self,token, bot_name, bot_image_url, bot_username):
        Base.__init__(self, token, bot_name, bot_image_url, bot_username)

    def connect(self):
        self.slack_client = SlackClient(self.token)

    def build_event(data):
        message = []
        for event_data in data['event']:
            fields = []
            event_message = {"pretext":"Incomming Notification",
                            "author_name":self.bot_name,
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
        return json.dumps(message)

    @rooms.setter
    def rooms(self,rooms):
        self.rooms = rooms

    @property
    def rooms(self):
        return self.rooms

    @property
    def method(self):
        return self.method

    def send_message(self,message,room):
        value = self.slack_client.api_call(self.slack_function,channel=room, username=self.bot_username(), icon_url=self.bot_image_url(), message=message)
        return value

    def send_event(self,payload,room):
        event = build_event(payload)
        value = self.slack_client.api_call(self.method,channel=room, username=self.bot_username(), icon_url=self.bot_image_url(), attachments=payload)
        return value


class Hipchat(Base):

    def __init__(self,token, bot_name, bot_image_url, bot_username):
        Base.__init__(self, token, bot_name, bot_image_url, bot_username)

    def send(payload, url):
        http = urllib3.PoolManager()
        headers = {'Content-type': 'application/json'}
        headers['Authorization'] = "Bearer " + HIPCHAT_API_TOKEN
        r = http.request('POST', url, body=json.dumps(payload).encode('UTF-8'), headers=headers,timeout=20)
        go = self.error_handler(r)
        return go

    def build_notify(room, message, color='yellow',
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
        return (payload, url)

    def build_message(room, message, host='api.hipchat.com'):
        if len(message) > 10000:
            raise ValueError('Message too long')

        url = "https://{0}/v2/room/{1}/message".format(host, room)
        payload = {
            'message': message,
        }
        return (payload, url)

    def error_handler(self,r):
        status = r.status
        if status == 401:
            return self.error_msg(status)
        elif status in [200,204,201]:
            return {"success":{"code":status, "message": "Message send secuessful", "type":"seccussful"}}
        else:
            return {"error":{"code":"405", "message":"Unable to handle request", "type":"bad_method"}}


def authorization(token):
    if data['token'] == BOT_WEBHOOK_SECRET:
        return True
    else:
        return False

@bot.route('/send', methods=['POST'])
def send_messages():

    data = request.get_json()

    if authorization(data['token']):
        if data['slack']:
            slack_data = data['slack']
            slack_client = Slack(SLACK_TOKEN, BOT_NAME, BOT_IMAGE_URL,BOT_USERNAME)

            if slack_data['message']['type'] == 'event':
                if len(slack_data['message']['rooms']) == 1:
                    slack_client.send_event(slack_data['message'])
                elif len(slack_data['message']['rooms']) > 1:
                    for r in slack_data['message']['rooms']:
                        slack_client.send_event(slack_data['message'])

            if slack_data['message']['type'] == 'message':
                if len(slack_data['message']['rooms']) == 1:
                    slack_client.send_message(slack_data['message'])
                elif len(slack_data['message']['rooms']) > 1:
                    for r in slack_data['message']['rooms']:
                        slack_client.send_message(slack_data['message'])

        if data['hipchat']:
            hipchat_data = data['hipchat']
            hipchat_client = Hipchat(HIPCHAT_API_TOKEN, BOT_NAME, BOT_IMAGE_URL, BOT_USERNAME)
            if hipchat_data['message']['type'] == 'notify':
                if len(hipchat_data['message']['rooms']) == 1:
                    payload, url = hipchat_client.build_notify(hipchat_data['message'])
                    d = hipchat_client.send(payload, url)
                    if d['error']:
                        return Response(json.dumps(d), mimetype="application/json"), d['error']['code']

                elif len(hipchat_data['message']['rooms']) > 1:
                    for r in hipchat_data['message']['rooms']:
                        payload, url = hipchat_client.build_notify(hipchat_data['message'])
                        d = hipchat_client.send(payload, url)
                        if d['error']:
                            break
                    return Response(json.dumps(d), mimetype="application/json"), d['error']['code']


    else:
        message = {"error": {"code":401, "message":"Authenticated requests only.", "type":"Unauthorized"} }
        return Response(json.dumps(error), mimetype="application/json"), message['error']['code']


@bot.route('/', methods=['GET'])
def index():
  return Response(json.dumps({"success":{"message":"It works! Please see the docs to use!", "code":200, "type":"successful"}}), mimetype="application/json"), 200

bot.wsgi_app = ProxyFix(bot.wsgi_app)
application = bot

if __name__ == '__main__':
  bot.run(debug=BOT_DEBUG)

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
import sys

if version_info < (2, 7, 9):
    # Disables SSL cert verification errors for Python < 2.7.9
    import requests.packages.urllib3 as urllib3
    urllib3.disable_warnings()
else:
    import urllib3
    urllib3.disable_warnings()

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Variables for Running the Application
DEFAULT_MIMETYPE=os.environ.get('DEFAULT_MIMETYPE',"application/json") # set the mime to send to the api's
SLACK_TOKEN = os.environ.get('SLACK_BOT_TOKEN',None).replace("\'","") # Slack Token for a Incomming API
AUTH_WEBHOOK_SECRET = os.environ.get('AUTH_WEBHOOK_SECRET', None).replace("\'","") # replace is because how new python version wrap in single quotes
BOT_NAME = os.environ.get('BOT_NAME', None).replace("\'","") # Name of the bot.
BOT_IMAGE_URL = os.environ.get('BOT_IMAGE_URL', None).replace("\'","") # Image to use for the Bot
BOT_DEBUG = os.environ.get('BOT_DEBUG',False)
BOT_USERNAME = os.environ.get('BOT_USERNAME', 'captainSlackHook').replace("\'","") # default bot username
HIPCHAT_API_TOKEN = os.environ.get('HIPCHAT_API_TOKEN',None).replace("\'","") # replace is because how new python version wrap in single quotes
HIPCHAT_API_HOST = os.environ.get('HIPCHAT_API_HOST', 'api.hipchat.com').replace("\'","") # allows for overridding for a private hipchat server.


if SLACK_TOKEN == None and HIPCHAT_API_TOKEN == None:
    raise ValueError('You must have env var of SLACK_TOKEN or HIPCHAT_API_TOKEN. With the slack incoming api token.')

bot = Flask(__name__)
http = urllib3.PoolManager()

class Base(object):

    def __init__(self,token,bot_name, bot_image_url,bot_username):
        Base.token = token
        Base.bot_name = bot_name
        Base.bot_image_url = bot_image_url
        Base.bot_username = bot_username

    #@property
    def bot_username(self):
        return Base.bot_username

    #@property
    def token(sefl):
        return Base.token

    #@property
    def bot_name(self):
        return Base.name

    #@property
    def bot_image_url(self):
        return Base.bot_image_url

    #@bot_image_url.setter
    def set_bot_image_url(self, image_url):
        Base.bot_image_url = image_url

    #@bot_name.setter
    def set_bot_name(self, name):
        Base.bot_name = name

    #@token.setter
    def set_token(self, token):
        Base.token = token

    def error_msg(value):
        return {
            401: {"error": {"code":401, "message":"Authenticated requests only.", "type":"Unauthorized"} },
            200: {"success": {"code":200, "message":"Sent Message successfully", "type":"Ok"}}
        }[value]

class Slack(Base):
    command = "chat.postMessage"
    rooms = []

    def __init__(self,token, bot_name, bot_image_url, bot_username):
        Base.__init__(self,token, bot_name, bot_image_url, bot_username)
        self.connect()

    def connect(self):
        from slackclient import SlackClient
        print self.token
        self.client = SlackClient(self.token)

    def build_event(self, data):
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

    @property
    def method(self):
        return self.method

    def error_handler(self, response):
        if response['ok']:
            return {'success': {"code":200, "message":"Message sent successfully", "type":"ok"}}
        elif response['ok'] == False:
            return {'error': { 'code': 418,"message": response['error'], "type": "error"}}

    def send_message(self, message, room):
        res = self.client.api_call(self.command, channel=room, username=self.bot_username, icon_url=self.bot_image_url, text=message)
        msg = self.error_handler(res)
        return msg

    def send_event(self, payload, room):
        event = self.build_event(payload)
        value = self.client.api_call(self.command, channel=room, username=self.bot_username, icon_url=self.bot_image_url, attachments=event)
        return value


class Hipchat(Base):

    host = 'api.hipchat.com'

    def __init__(self,token, bot_name, bot_image_url, bot_username, host):
        Base.__init__(self, token, bot_name, bot_image_url, bot_username)
        self.host = host

    def send(self, payload, url):
        http = urllib3.PoolManager()
        headers = {'Content-type': 'application/json'}
        headers['Authorization'] = "Bearer " + self.token
        print payload
        r = http.request('POST', url, body=json.dumps(payload).encode('UTF-8'), headers=headers, timeout=20)
        go = self.error_handler(r)
        return go


    def build_notify(self, room, msg_obj):
        if 'color' in msg_obj:
            color = msg_obj['color']
        else:
            color = 'yellow'
        if 'body' in msg_obj:
            body = msg_obj['body']
        if 'rooms' in msg_obj:
            rooms = msg_obj['rooms']
        if 'notify' in msg_obj:
            notify = msg_obj['notify']
        else:
            notify = False
        if 'format' in msg_obj:
            msg_format = msg_obj['format']
        else:
            msg_format = 'text'

        if len(body) > 10000:
            raise ValueError('Message too long')
        if msg_format not in ['text', 'html']:
            raise ValueError("Invalid message format '{0}'".format(msg_format))
        if color not in ['yellow', 'green', 'red', 'purple', 'gray', 'random']:
            raise ValueError("Invalid color {0}".format(color))
        if not isinstance(notify, bool):
            raise TypeError("Notify must be boolean")

        url = "https://{0}/v2/room/{1}/notification".format(self.host, room)
        payload = {
            'message': body,
            'notify': notify,
            'message_format': msg_format,
            'color': color
        }
        return (payload, url)

    def build_message(self, room, msg_obj):
        if 'body' in msg_obj:
            body = msg_obj['body']

        if len(body) > 10000:
            raise ValueError('Message too long')

        url = "https://{0}/v2/room/{1}/message".format(self.host, room)
        print url
        payload = {
            'message': body,
        }
        return (payload, url)

    def error_handler(self, r):
        status = r.status
        if status == 401:
            return self.error_msg(status)
        elif status in [200,204,201]:
            return {"success":{"code":status, "message": "Message send secuessful", "type":"seccussful"}}
        else:
            return {"error":{"code":"405", "message":"Unable to handle request", "type":"bad_method"}}


def authorization(token):
    if token == AUTH_WEBHOOK_SECRET:
        return True
    else:
        return False

@bot.route('/send', methods=['POST'])
def send_messages():
    data = request.get_json()
    rtn_data = {}

    if authorization(data['token']):
        if 'slack' in data:
            if SLACK_TOKEN == None:
                rtn_data['slack'] = {"error":{"type":"bad_request","message":"unable to send to Slack. No TOKEN provided", "code":"404"}}
            else:
                slack_data = data['slack']
                slack_client = Slack(SLACK_TOKEN, BOT_NAME, BOT_IMAGE_URL, BOT_USERNAME)

                if slack_data['message']['type'] == 'event':
                    if len(slack_data['message']['rooms']) == 1:
                        rtn_data['slack'] = slack_client.send_event(slack_data['message'], slack_data['message']['rooms'][0])

                    elif len(slack_data['message']['rooms']) > 1:
                        for r in slack_data['message']['rooms']:
                            res = slack_client.send_event(slack_data['message'], r)
                            if 'error' in res:
                                break
                        rtn_data['slack'] = res

                if slack_data['message']['type'] == 'message':
                    if len(slack_data['message']['rooms']) == 1:
                        rtn_data['slack'] = slack_client.send_message(slack_data['message']['body'], slack_data['message']['rooms'][0])

                    elif len(slack_data['message']['rooms']) > 1:
                        for r in slack_data['message']['rooms']:
                            res = slack_client.send_message(slack_data['message']['body'], r)
                            if 'error' in res:
                                break
                        rtn_data['slack'] = res

        if 'hipchat' in data:
            if HIPCHAT_API_TOKEN == None:
                rtn_data['hipchat'] = {"error":{"type":"bad_request","message":"unable to send to Hipchat. No TOKEN provided", "code":"404"}}
            else:
                hipchat_data = data['hipchat']
                hipchat_client = Hipchat(HIPCHAT_API_TOKEN, BOT_NAME, BOT_IMAGE_URL, BOT_USERNAME, HIPCHAT_API_HOST)
                if hipchat_data['message']['type'] == 'notify':
                    if len(hipchat_data['message']['rooms']) == 1:
                        payload, url = hipchat_client.build_notify(hipchat_data['message']['rooms'][0], hipchat_data['message'])
                        rtn_data['hipchat'] = hipchat_client.send(payload, url)

                    elif len(hipchat_data['message']['rooms']) > 1:
                        for r in hipchat_data['message']['rooms']:
                            payload, url = hipchat_client.build_notify(r, hipchat_data['message'])
                            res = hipchat_client.send(payload, url)
                            if 'error' in res:
                                break
                        rtn_data['hipchat'] = res

                if hipchat_data['message']['type'] == 'message':
                    if len(hipchat_data['message']['rooms']) == 1:
                        payload, url = hipchat_client.build_message(hipchat_data['message']['rooms'][0], hipchat_data['message'])
                        rtn_data['hipchat'] = hipchat_client.send(payload, url)

                    elif len(hipchat_data['message']['rooms']) > 1:
                        for r in hipchat_data['message']['rooms']:
                            payload, url = hipchat_client.build_message(r, hipchat_data['message'])
                            res = hipchat_client.send(payload, url)
                            if 'error' in res:
                                break
                        rtn_data['hipchat'] = res

        return Response(json.dumps(rtn_data), DEFAULT_MIMETYPE), 200
    else:
        message = {"error": {"code":401, "message":"Authenticated requests only.", "type":"Unauthorized"} }
        return Response(json.dumps(message), DEFAULT_MIMETYPE), message['error']['code']

@bot.route('/', methods=['GET'])
def index():
  return Response(json.dumps({"success":{"message":"It works! Please see the docs to use!", "code":200, "type":"successful"}}), DEFAULT_MIMETYPE), 200

bot.wsgi_app = ProxyFix(bot.wsgi_app)
application = bot

if __name__ == '__main__':
  bot.run(debug=BOT_DEBUG)

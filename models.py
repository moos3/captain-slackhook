from slackclient import SlackClient
from sys import version_info
import pprint
import requests
from requests.exceptions import ConnectionError
import sys
import json
import pprint

class Empty:
    pass

'''
if version_info < (2, 7, 9):
    # Disables SSL cert verification errors for Python < 2.7.9
    import requests.packages.urllib3 as urllib3
    urllib3.disable_warnings()
else:
    import urllib3
    urllib3.disable_warnings()

http = urllib3.PoolManager()
'''

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
        self.client = SlackClient(self.token)

    def build_event(self, data):
        message = []
        for event_data in data['event']:
            fields = []
            actions = []
            if 'pretext' in data['event']:
                pretext = data['event']['pretext']
            else:
                pretext = "Incoming Notification"

            if 'fallback' in data['event']:
                fallback = data['event']['fallback']
            else:
                fallback = "Event Triggered"

            event_message = {"pretext":pretext,
                            "author_name":self.bot_name,
                            "fallback": fallback,
            }

            for k,v in event_data.iteritems():
                if k == 'fields':
                    for _field in v:
                        sub_message = {}
                        for key, value in _field.iteritems():
                            print key
                            if str(key) == 'short':
                                sub_message[key] = value
                            else:
                                sub_message[str(key)] = str(value)
                        fields.append(sub_message)
                elif k == 'actions':
                    for _actions in v:
                        sub_actions = {}
                        for key, value in _actions.iteritems():
                            if str(key) == 'confirm':
                                sub_actions[str(key)] = value
                            else:
                                sub_actions[str(key)] = str(value)
                        actions.append(sub_actions)
                else:
                    event_message[str(k)] = str(v)
                if k == 'fields':
                    event_message['fields'] = fields
                elif k == 'actions':
                    event_message['actions'] = actions

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

    def run(self, bot, data):
        rtn_data = {}
        slack_data = data['slack']
        if slack_data['message']['type'] == 'event':
            if len(slack_data['message']['rooms']) == 1:
                rtn_data['slack'] = self.send_event(slack_data['message'], slack_data['message']['rooms'][0])

            elif len(slack_data['message']['rooms']) > 1:
                for r in slack_data['message']['rooms']:
                    res = self.send_event(slack_data['message'], r)
                    if 'error' in res:
                        break
                rtn_data['slack'] = res

        if slack_data['message']['type'] == 'message':
            if len(slack_data['message']['rooms']) == 1:
                rtn_data['slack'] = self.send_message(slack_data['message']['body'], slack_data['message']['rooms'][0])

            elif len(slack_data['message']['rooms']) > 1:
                for r in slack_data['message']['rooms']:
                    res = self.send_message(slack_data['message']['body'], r)
                    if 'error' in res:
                        break
                rtn_data['slack'] = res

        return rtn_data


class Hipchat(Base):

    host = 'api.hipchat.com'

    def __init__(self,token, bot_name, bot_image_url, bot_username, host):
        Base.__init__(self, token, bot_name, bot_image_url, bot_username)
        self.host = host

    def run(self, bot, data):
        rtn_data = {}
        hipchat_data = data['hipchat']
        if hipchat_data['message']['type'] == 'notify':
            if len(hipchat_data['message']['rooms']) == 1:
                payload, url = self.build_notify(hipchat_data['message']['rooms'][0], hipchat_data['message'])
                rtn_data['hipchat'] = self.send(payload, url)

            elif len(hipchat_data['message']['rooms']) > 1:
                for r in hipchat_data['message']['rooms']:
                    payload, url = self.build_notify(r, hipchat_data['message'])
                    res = self.send(payload, url)
                    if 'error' in res:
                        break
                rtn_data['hipchat'] = res

        if hipchat_data['message']['type'] == 'message':
            if len(hipchat_data['message']['rooms']) == 1:
                payload, url = self.build_message(hipchat_data['message']['rooms'][0], hipchat_data['message'])
                rtn_data['hipchat'] = self.send(payload, url)

            elif len(hipchat_data['message']['rooms']) > 1:
                for r in hipchat_data['message']['rooms']:
                    payload, url = self.build_message(r, hipchat_data['message'])
                    res = self.send(payload, url)
                    if 'error' in res:
                        break
                rtn_data['hipchat'] = res
        return rtn_data

    def send(self, payload, url):
        headers = {'Content-type': 'application/json'}
        headers['Authorization'] = "Bearer " + self.token
        try:
            r = requests.post(url, data=json.dumps(payload).encode('UTF-8'), headers=headers)
            go = self.error_handler(r)
        except requests.exceptions.ConnectionError as e:
            err = Empty()
            message = 'connection to %s failed!\n' % url
            err.status = message
            go = self.error_handler(err)

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

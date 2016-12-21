import os
import json
import string
from flask import Flask, request, Response, jsonify
from werkzeug.contrib.fixers import ProxyFix
from flask_dotenv import DotEnv
import requests
from sys import version_info
from models import Slack, Hipchat


__author__ = 'Richard <Moose> Genthner'
__email__ = 'richard.genthner@wheniwork.com'
__version__ = "2.0.0"

if version_info < (2, 7, 9):
    # Disables SSL cert verification errors for Python < 2.7.9
    import requests.packages.urllib3 as urllib3
    urllib3.disable_warnings()
else:
    import urllib3
    urllib3.disable_warnings()

bot = Flask(__name__)
http = urllib3.PoolManager()
env = DotEnv()
env.init_app(bot)

if bot.config.get('SLACK_TOKEN') == None and bot.config.get('HIPCHAT_API_TOKEN') == None:
    raise ValueError('You must have env var of SLACK_TOKEN or HIPCHAT_API_TOKEN. With the slack incoming api token.')

'''
Send Message API starts here
'''
def authorization(token):
    if token == bot.config.get('AUTH_WEBHOOK_SECRET'):
        return True
    else:
        return False

@bot.route('/send', methods=['POST'])
def send_messages():
    data = request.get_json()
    rtn_data = {}

    if not 'token' in data:
        message = {"error": {"code":401, "message":"Authenticated requests only. You must past a token in your request.", "type":"Unauthorized"} }
        return Response(json.dumps(message), bot.config.get('DEFAULT_MIMETYPE')), message['error']['code']

    if authorization(data['token']):
        if 'slack' in data:
            if bot.config.get('SLACK_TOKEN') == None:
                rtn_data['slack'] = {"error":{"type":"bad_request","message":"unable to send to Slack. No TOKEN provided", "code":"404"}}
            else:
                slack_client = Slack(bot.config.get('SLACK_TOKEN'), bot.config.get('BOT_NAME'), bot.config.get('BOT_IMAGE_URL'), bot.config.get('BOT_USERNAME'))
                rtn_data = slack_client.run(bot, data)

        if 'hipchat' in data:
            if bot.config.get('HIPCHAT_API_TOKEN') == None:
                rtn_data['hipchat'] = {"error":{"type":"bad_request","message":"unable to send to Hipchat. No TOKEN provided", "code":"404"}}
            else:
                hipchat = Hipchat(bot.config.get('HIPCHAT_API_TOKEN'), bot.config.get('BOT_NAME'), bot.config.get('BOT_IMAGE_URL'), bot.config.get('BOT_USERNAME'), bot.config.get('HIPCHAT_API_HOST'))
                rtn_data = hipchat.run(bot, data)

        return Response(json.dumps(rtn_data), bot.config.get('DEFAULT_MIMETYPE')), 200
    else:
        message = {"error": {"code":401, "message":"Authenticated requests only.", "type":"Unauthorized"} }
        return Response(json.dumps(message), bot.config.get('DEFAULT_MIMETYPE')), message['error']['code']

@bot.route('/', methods=['GET'])
def index():
  return Response(json.dumps({"success":{"message":"It works! Please see the docs to use!", "code":200, "type":"successful"}}), bot.config.get('DEFAULT_MIMETYPE')), 200

bot.wsgi_app = ProxyFix(bot.wsgi_app)
application = bot

if __name__ == '__main__':
    bot.run()

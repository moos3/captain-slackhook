# Captain Slackhook!

This flask application was written as a way to inject messages and notifications into both slack and hipchat. I wrote this while working for When I Work. So all credit for the idea for this creation goes to my fellow devops engineers at When I Work.

## Requirements
This webhook bot requires Python 2.x and pip to be installed. I would also recommend that you install nginx in front of it. As this will run as a flask server.

## Installation
1) Run a pip install
```pip install -r requirements.txt```

2) Copy the example.env file to .env and fill in the values

3) python main.py This will start it.


## Configuration
We will need to generate a .env file for the application. In this section I'll go over some basic connfiguration for the application. Lets look at the .env file for the application.

```
'DEFAULT_MIMETYPE',"application/json" # set the mime to send to the api's
'SLACK_BOT_TOKEN' # Slack Token for a Incomming API
'AUTH_WEBHOOK_SECRET' # replace is because how new python version wrap in single quotes
'BOT_NAME' # Name of the bot.
'BOT_IMAGE_URL' # Image to use for the Bot
'BOT_DEBUG',False
'BOT_USERNAME' # default bot username
'HIPCHAT_API_TOKEN' # replace is because how new python version wrap in single quotes
'HIPCHAT_API_HOST','api.hipchat.com' # allows for overridding for a private hipchat server.
```

Special Note `AUTH_WEBHOOK_SECRET` This is the Authentication token you want to use to allow services/scripts etc to talk to /send with out this then you can't send a message to the channels of slack or hipchat.
Also if you dont have a token for either hipchat or slack it will not send.

If you set any of these as system ENV Variables they will overwrite the .env file ones.


## How to send a simple message
To send a message to slack or hipchat. You will send a json object to the /send endpoint. Using the following examples. Things to note, Slack you can use the nice change names. Hipchat you must login to the webui and get the channel name to room number mapping. This has to do with hipchat using XMPP on the backend. To send a message to multiple rooms you just add them to the rooms json array as strings wrapped in double qoutes.

1) Slack Only

```json
{
"slack": {
		"message": {
			"type": "message",
			"rooms": ["#general"],
			"body": "Hello everybody from Captain Slackhook!"
		}
	},
	"token":"Your Token Here"
}
```

2) Hipchat Only

```json
{
	"hipchat": {
		"message": {
			"type": "message",
			"rooms": ["1527413"],
			"body": "Hello everybody from Captain Slackhook"
		}
	},
	"token":"Your Token Here"
}
```

3) Slack and Hipchat

```json
{
	"hipchat": {
		"message": {
			"type": "message",
			"rooms": ["1527413"],
			"body": "Hello everybody from Captain Slackhook"
		}
	},
	"slack": {
		"message": {
			"type": "message",
			"rooms": ["#general"],
			"body": "Hello everybody from Captain Slackhook!"
		}
	},
	"token":"Your Token Here"
}

```

## Send notifications/events
So in hipchat you can send room notifications and in slack they call these events to a room. Which just like messages you can send them to mutliple rooms. You can use both fields and actions in slack event messages.  These objects are structured like so:

1) Slack:

```json
{
"slack": {
        "message": {
            "type": "event",
            "rooms": ["#random"],
            "body": [{
                "title": "Multiple Events",
                "fields": [{
                    "title": "Defcon",
                    "value": "Double Take"
                }],
                "color": "good"
            }, {
                "title": "Multiple Event testing, Event 2",
                "fields": [{
                    "title": "Defcon",
                    "value": "Double Take"
                }, {
                    "title": "Second field",
                    "short": true,
                    "value": "this is a super long field value"
                }],
                "color": "danger"
            }]
        }
    },
    "token": "your token here"
}
```

2) Hipchat

```json
{
	"hipchat": {
        "message": {
            "type": "notify",
            "rooms": ["2754509", "12310"],
            "color": "green",
            "body": "body"
        }
    },
    "token": "your token here"

}

```

3) Hipchat + Slack

```json
{
"slack": {
        "message": {
            "type": "event",
            "rooms": ["#random"],
            "body": [{
                "title": "Multiple Events",
                "fields": [{
                    "title": "Defcon",
                    "value": "Double Take"
                }],
                "color": "good"
            }, {
                "title": "Multiple Event testing, Event 2",
                "fields": [{
                    "title": "Defcon",
                    "value": "Double Take"
                }, {
                    "title": "Second field",
                    "short": true,
                    "value": "this is a super long field value"
                }],
                "color": "danger"
            }]
        }
    },
	"hipchat": {
        "message": {
            "type": "notify",
            "rooms": ["2754509", "12310"],
            "color": "green",
            "body": "body"
        }
    },
    "token": "your token here"

}

```

4) Slack actions

```json
{
"slack": {
			"message": {
					"type": "event",
					"rooms": ["#random"],
					"event": [{
					"fallback": "DevOps Office Hours Notice",
					"color": "good",
					"title": "Up Coming Events",
					"callback_id": "wopr_game",
					"actions": [
							{
									"name": "chess",
									"text": "Chess",
									"type": "button",
									"value": "chess"
							},
							{
									"name": "maze",
									"text": "Falken's Maze",
									"type": "button",
									"value": "maze"
							},
							{
									"name": "war",
									"text": "Thermonuclear War",
									"style": "danger",
									"type": "button",
									"value": "war",
									"confirm": {
											"title": "Are you sure?",
											"text": "Wouldn't you prefer a good game of chess?",
											"ok_text": "Yes",
											"dismiss_text": "No"
									}
							}
					],
					"footer": "Delivered by The Captain!",
					"footer_icon": "http://www.hotelroomsearch.net/im/hotels/gr/the-captain-9.jpg"
			 }]
			}
		},
		"token": "your token here"
}
```

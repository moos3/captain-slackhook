### Slack Bot Using flask
This is a simple bot for making webhook endpoints to avoid integations.

### Currently Supported
#### endpoint /send
Supports the following objects, to be posted using a json.
You can set override the channel by specifying it before declaring events or a message.

Event: (Slack Attachment Api)

Supports sending multiple events at once. Supports any values that can been found in the attachment documentation for slack. Reference here [Api Doc](https://api.slack.com/docs/message-attachments) 
```
{
"event": [{
	"title": "Multiple Event Testing Event 1",
	"fields": [{
		"title": "Defcon",
		"value": "Double Take"
	}],
	"color": "green"
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
}],
"token": "ghYHapu1yZ9PfK"
}
```

Message: (Simple message)

If you added the following to your json object on a message ```"hipchat":{
"rooms": ['roomnumber'] } It will message each of those rooms as the API key
person. If you want notification style messages you can do this: ```"hipchat":{
"rooms": ['roomnumber'], "notify":{ "color":"green" } }```

```
{
	"message": "test message again",
	"token": "ghYHapu1yZ9PfK"
}
```
By default it will send messages to #general in slack. Unless you add ```'channel':'#slackchannelname'```

Calls will return a json object. That will contain ok set to True or False depending is the message send failed or was successful. Also will contian a message attribute with a message for logging.


## Examples
Simple Slack only:
```
{
	"message": "@flu give bottle of (rum) or i'll take your soul ", 
	'channel': "#rockemsockemrobots ", 
	"token": "g123qdinlkdho2"
}


```

Slack and Hipchat:

```
{
	"message": "@flu give bottle of (rum) or i'll take your soul ", 
	'channel': "#rockemsockemrobots ", 
	"hipchat ": {
		"rooms": ['672359'],
		"notify": {
			"color": "green"
		}
	}, 
	"token": "g123qdinlkdho2"
}

```

Slack Event:

```
{
	"event": [{
		"title": "Multiple Event Testing Event 1",
		"priority": "Defcon",
		"value": "Double Take",
		"color": "good"
	}, {
		"title": "Multiple Event testing, Event 2",
		"priority": "Defcon",
		"value": "this is a extra long description. Blah blah balh blah.",
		"short": True,
		"color": "danger"
	}],
	"token": "g123qdinlkdho2"
}
```



### Slack Bot Using flask
This is a simple bot for making webhook endpoints to avoid integations.

### Currently Supported
#### endpoint /send
Supports the following objects, to be posted using a json.
You can set override the channel by specifying it before declaring events or a message.

Event: (Slack Attachment Api)
Supports sending multiple events at once. Supports any values that can been found in the attachment documentation for slack. Reference here [Api Doc](https://api.slack.com/docs/message-attachments)
Priority and value will automatically mapped to the fields. If you can short but declaring it to override the default of False. 
```
{
	"event": [{
		"title": "its alive!",
		"priority": "Defcon",
		"value": "Double Take",
		"color": "green",
		"title_link": "https://en.wikipedia.org/wiki/DEFCON",
		"image_url": "http://i.imgur.com/o65azK1.jpg"
	}],
	"token": "ghYHapu1yZ9PfK"
}
```

Message: (Simple message)
```
{
	"message": "test message again",
	"token": "ghYHapu1yZ9PfK"
}
```

Calls will return a json object. That will contain ok set to True or False depending is the message send failed or was successful. Also will contian a message attribute with a message for logging.

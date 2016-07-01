### Slack Bot Using flask
This is a simple bot for making webhook endpoints to avoid integations.

### Currently Supported
#### endpoint /send
Supports the following objects, to be posted using a json.

Event: (Slack Attachment Api)
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

### Support Values in the Objects

channel: Can be a channel or @username

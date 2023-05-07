# Json2Pubsub

Json2Pubsub is another versatile tool for turning many types of incoming requests,
such as webhooks to Pub/Sub messages. It supports Common Expression Language,
CEL, both for validating that incoming requests are valid and for extracting the
Pub/Sub message payload.

Currently it has been tested with Slack incoming events. Currently the function
only accepts `POST` requests (both `application/x-www-form-urlencoded` and
`application/json` are supported).

## Configuring

The function can be deployed as a Cloud Run or Cloud Functions v2 function.
Configuration happens through environment variables, however all of the
environment variables also support fetching the contents from Secret Manager
(by prefixing them with `gsm:` and specifying the full secret name).

Configuration variables are:

- `PUBSUB_TOPIC`: target topic 
- `CUSTOM_HANDLER`: specify the URL where message will be submitted (default `/`)
- `CONTROL_CEL`: request control CEL expression, this will be first evaluated and it has to return `true` for the request to proceed
- `MESSAGE_CEL`: message extraction CEL expression

### Available CEL variables

- `request.body`: contains the entire request body raw
- `request.post`: contains the POST variables
- `request.json`: contains the JSON body in case the request was `application/json` or `text/json`
- `request.headers`: contains the request headers
- `request.unixtime`: unix time for current request
- `request.time.(year|month|day|hour|minute|second)`: split time for request
- 
### Available CEL functions

- `parseJWT(secret, string)`: parses a JWT token
- `hmacSHA256(secret, string)`: returns HMAC-SHA256
- `hmacSHA1(secret, string)`: returns HMAC-SHA1

## Example expressions

### Example of Slack incoming message processing

CEL expression for request verification:
```
'x-slack-signature' in request.headers && 
'x-slack-request-timestamp' in request.headers &&
(request.unixtime - int(request.headers['x-slack-request-timestamp'])) < 300 &&
('v0='+hmacSHA256('8f742231b10e8888abcd99yyyzzz85a5', 'v0:'+request.headers['x-slack-request-timestamp']+':'+request.body)) == request.headers['x-slack-signature']
```

CEL expression for extracting payload:

```
request.json.payload
```

Testing:
```sh
curl -XPOST -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'X-Slack-Request-Timestamp: 1531420618' \
  -H 'X-Slack-Signature: v0=a2114d57b48eac39b9ad189dd8316235a7b4a8d21a10bd27519666489c69b503' \
  -d 'token=xyzz0WbapA4vBCDEFasx0q6G&team_id=T1DC2JH3J&team_domain=testteamnow&channel_id=G8PSS9T3V&channel_name=foobar&user_id=U2CERLKJA&user_name=roadrunner&command=%2Fwebhook-collect&text=&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT1DC2JH3J%2F397700885554%2F96rGlfmibIGlgcZRskXaIFfN&trigger_id=398738663015.47445629121.803a0bc887a14d10d2c447fce8b6703c' \
  http://localhost:8080
```

### Example of validating JWT

Contents of sample JWT:
```
{
    "iss": "pubsub2inbox",
    "iat": 1683460421,
    "exp": 1967457252,
    "aud": "github.com/GoogleCloudPlatform/pubsub2inbox",
    "sub": "admin@example.com"
}
```

Key: `pubsub2inbox-rocks`

Signed token: `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwdWJzdWIyaW5ib3giLCJpYXQiOjE2ODM0NjA0MjEsImV4cCI6MTk2NzQ1NzI1MiwiYXVkIjoiZ2l0aHViLmNvbS9Hb29nbGVDbG91ZFBsYXRmb3JtL3B1YnN1YjJpbmJveCIsInN1YiI6ImFkbWluQGV4YW1wbGUuY29tIn0.UwsRpZTqZg03J8vcKDxHWg8CX4L_yijRF2tEDjpckEk`

Verification CEL:
```
parseJWT('pubsub2inbox-rocks', request.headers['authorization'].substring(7)).iss == 'pubsub2inbox'
```

Testing:
```
curl -XPOST \
  -H 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwdWJzdWIyaW5ib3giLCJpYXQiOjE2ODM0NjA0MjEsImV4cCI6MTk2NzQ1NzI1MiwiYXVkIjoiZ2l0aHViLmNvbS9Hb29nbGVDbG91ZFBsYXRmb3JtL3B1YnN1YjJpbmJveCIsInN1YiI6ImFkbWluQGV4YW1wbGUuY29tIn0.UwsRpZTqZg03J8vcKDxHWg8CX4L_yijRF2tEDjpckEk' \
  -H 'Content-Type: application/json' \
  -d '{"foo":"bar"}' \
  http://localhost:808
```

### Example of extracting map JSON from application/json request

CEL expression for extraction:

```
request.json
```

Testing:
```
curl -XPOST -H 'Content-Type: application/json' \
  -d '{"foo":"bar"}' \
  http://localhost:8080
```

### Example of extracting list JSON from application/json request

CEL expression for extraction:

```
request.json
```

Testing:
```
curl -XPOST -H 'Content-Type: application/json' \
  -d '["foo","bar"]' \
  http://localhost:8080
```


### Example of extracting JSON from query string

CEL expression for extraction:
```
request.post.jsoncontents[0]
```

Testing:
```
curl -XPOST -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'jsoncontents=%7B%22foo%22%3A%22bar%22%7D' \
  http://localhost:8080
```

### Example of constructing JSON from query string

CEL expression for extraction: 
```
{ "key": request.post.key }
```

```
curl -XPOST -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'key=123' \
  http://localhost:8080
```

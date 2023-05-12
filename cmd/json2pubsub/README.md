# Json2Pubsub

Json2Pubsub is another versatile tool for turning many types of incoming requests,
such as webhooks, to Pub/Sub messages. It supports Common Expression Language,
CEL, both for validating that incoming requests are valid and for extracting the
Pub/Sub message payload.

Currently it has been tested with Slack incoming events. The function only accepts 
`POST` requests (both `application/x-www-form-urlencoded` and `application/json` are supported).

The only permission on Google Cloud that it requires is `roles/pubsub.publisher`
on the target Pub/Sub topic.

## Deploying

The main Pubsub2Inbox [Terraform code](../../variables.tf) supports automatically
deploying Json2Pubsub alongside with a Pubsub2Inbox function. Simply add the 
following variable in the module:

```hcl
  deploy_json2pubsub = {
    enabled         = true
    suffix          = "-json2pubsub"
    control_cel     = "request.header['x-authorization-token'] == '12345678'"
    message_cel     = "request.json"
    public_access   = true 
    container_image = null # if using Cloud Run
    min_instances   = 0
    max_instances   = 10
  }
```

If you are deploying via Cloud Run, a `Dockerfile` is supplied. Remember to
point `container_image` to the correct container image then.

## Running locally

```sh
export FUNCTION_TARGET=Json2Pubsub
go run cmd/main.go
```

## Configuring

The function can be deployed as a Cloud Run or Cloud Functions v2 function.
Configuration happens through environment variables, however all of the
environment variables also support fetching the contents from Secret Manager
(by prefixing them with `gsm:` and specifying the full secret name).

Configuration variables are:

- `GOOGLE_CLOUD_PROJECT`: the Google Cloud project to use 
- `PUBSUB_TOPIC`: target topic 
- `CUSTOM_HANDLER`: specify the URL where message will be submitted (default `/`)
- `CONTROL_CEL`: request control CEL expression, this will be first evaluated and it has to return `true` for the request to proceed
- `MESSAGE_CEL`: message extraction CEL expression
- `RESPONSE_CEL`: for returning a response

### Available CEL variables

- `request.body`: contains the entire request body raw
- `request.post`: contains the POST variables
- `request.json`: contains the JSON body in case the request was `application/json` or `text/json`
- `request.headers`: contains the request headers
- `request.unixtime`: unix time for current request
- `request.time.(year|month|day|hour|minute|second)`: split time for request
- `request.scheme`: http or https (generally always https)
- `request.method`: always POST
- `request.path`: request path
- `request.query`: raw query string
- `origin.ip`: originating IP address

### Available CEL functions

- `parseJWT(secret, string)`: parses a JWT token
- `hmacSHA256(secret, string)`: returns HMAC-SHA256
- `hmacSHA1(secret, string)`: returns HMAC-SHA1
- `ipInRange(ip, iprange)`: checks if IP is within IP range
- `parseJSON(string)`: parses a string format JSON (supports only map-style output)
- 
## Example expressions

### Example of Slack incoming event processing

CEL expression for request verification:
```
'x-slack-signature' in request.headers && 
'x-slack-request-timestamp' in request.headers &&
(request.unixtime - int(request.headers['x-slack-request-timestamp'])) < 300 &&
('v0='+hmacSHA256('8f742231b10e8888abcd99yyyzzz85a5', 'v0:'+request.headers['x-slack-request-timestamp']+':'+request.body)) == request.headers['x-slack-signature']
```

CEL expression for extracting payload:

```
request.json
```

CEL expression for returning the response body (used for challenge):

```
'challenge' in request.json ? request.json.challenge : 'OK'
```

Testing:
```sh
curl -XPOST -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'X-Slack-Request-Timestamp: 1531420618' \
  -H 'X-Slack-Signature: v0=a2114d57b48eac39b9ad189dd8316235a7b4a8d21a10bd27519666489c69b503' \
  -d 'token=xyzz0WbapA4vBCDEFasx0q6G&team_id=T1DC2JH3J&team_domain=testteamnow&channel_id=G8PSS9T3V&channel_name=foobar&user_id=U2CERLKJA&user_name=roadrunner&command=%2Fwebhook-collect&text=&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT1DC2JH3J%2F397700885554%2F96rGlfmibIGlgcZRskXaIFfN&trigger_id=398738663015.47445629121.803a0bc887a14d10d2c447fce8b6703c' \
  http://localhost:8080
```

JSON body (not valid request):

```sh
curl -i -XPOST -H 'Content-Type: application/json' \
  -H 'X-Slack-Request-Timestamp: 1531420618' \
  -H 'X-Slack-Signature: v0=a2114d57b48eac39b9ad189dd8316235a7b4a8d21a10bd27519666489c69b503' \
  -d '{"token":"Jhj5dZrVaK7ZwHHjRyZWjbDl","challenge":"3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P", "type":"url_verification"}' \
  http://localhost:8080
```

### Example of Slack incoming event processing (legacy)

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

CEL expression for returning the response body (used for challenge):

```
'challenge' in parseJSON(request.json.payload) ? parseJSON(request.json.payload).challenge : 'OK'
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

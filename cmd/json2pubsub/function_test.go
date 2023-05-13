package function

import (
	"context"
	"fmt"
	"io/ioutil"
	"math/rand"
	"net/http"
	"net/http/httptest"

	"strings"
	"testing"

	"cloud.google.com/go/pubsub"
	"github.com/google/cel-go/cel"
	"github.com/stretchr/testify/assert"
	"google.golang.org/api/option"
	"google.golang.org/grpc"

	"cloud.google.com/go/pubsub/pstest"
)

func makeHttpRequest(remoteAddr, method, body string, headers map[string]string) (r *http.Request, err error) {
	r, err = http.NewRequest(method, "/", strings.NewReader(body))
	if err == nil {
		r.RemoteAddr = fmt.Sprintf("%s:%d", remoteAddr, rand.Intn(63976))
	}
	for k, v := range headers {
		r.Header.Add(k, v)
	}
	return
}

var publisherMockClient *pubsub.Client
var pubsubMockServer *pstest.Server
var pubsubMockTopic *pubsub.Topic

func createPubsubMockServer() error {
	srv := pstest.NewServer()

	pubsubMockServer = srv
	return nil
}

func getPubsubTopicMock(ctx context.Context, cloudProjectId string, userAgent string, pubsubTopic string) (*pubsub.Topic, error) {
	if pubsubMockTopic != nil {
		return pubsubMockTopic, nil
	}

	conn, err := grpc.Dial(pubsubMockServer.Addr, grpc.WithInsecure())
	if err != nil {
		return nil, err
	}

	publisherMockClient, err = pubsub.NewClient(ctx, cloudProjectId, option.WithGRPCConn(conn))
	if err != nil {
		return nil, err
	}
	pubsubMockTopic, err = publisherMockClient.CreateTopic(ctx, pubsubTopic)
	if err != nil {
		return nil, err
	}

	return pubsubMockTopic, nil
}

func mergeMaps(m1 map[string]string, m2 map[string]string) (merged map[string]string) {
	merged = make(map[string]string, 0)
	for k, v := range m1 {
		merged[k] = v
	}
	for k, v := range m2 {
		merged[k] = v
	}
	return
}

func TestControlCel(t *testing.T) {
	err := createPubsubMockServer()
	assert.Nil(t, err)

	celEnv, err := GetCelEnv()
	assert.IsType(t, celEnv, &cel.Env{})
	assert.Nil(t, err)

	var defaultJson = "{\"test\":\"unit\"}"
	var defaultHeaders = map[string]string{
		"Content-type": "application/json",
	}
	var tests = []struct {
		testName    string
		controlCel  string
		messageCel  string
		responseCel string
		status      int
		body        string
		remoteAddr  string
		headers     map[string]string
		expect      string
		expectBody  string
	}{
		{
			testName:    "disallow all",
			controlCel:  "false",
			messageCel:  "request.json",
			responseCel: "",
			status:      403,
			body:        defaultJson,
			remoteAddr:  "127.0.0.1",
			headers:     defaultHeaders,
			expect:      "",
			expectBody:  "",
		},
		{
			testName:    "allow all",
			controlCel:  "true",
			messageCel:  "request.json",
			responseCel: "",
			status:      200,
			body:        defaultJson,
			remoteAddr:  "127.0.0.1",
			headers:     defaultHeaders,
			expect:      defaultJson,
			expectBody:  "",
		},
		{
			testName:    "valid JWT",
			controlCel:  "parseJWT('pubsub2inbox-rocks', request.headers['authorization'].substring(7)).iss == 'pubsub2inbox'",
			messageCel:  "request.json",
			responseCel: "",
			status:      200,
			body:        defaultJson,
			remoteAddr:  "127.0.0.1",
			headers: mergeMaps(defaultHeaders, map[string]string{
				"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwdWJzdWIyaW5ib3giLCJpYXQiOjE2ODM0NjA0MjEsImV4cCI6MTk2NzQ1NzI1MiwiYXVkIjoiZ2l0aHViLmNvbS9Hb29nbGVDbG91ZFBsYXRmb3JtL3B1YnN1YjJpbmJveCIsInN1YiI6ImFkbWluQGV4YW1wbGUuY29tIn0.UwsRpZTqZg03J8vcKDxHWg8CX4L_yijRF2tEDjpckEk",
			}),
			expect:     defaultJson,
			expectBody: "",
		},
		{
			testName:    "unauthorized JWT",
			controlCel:  "parseJWT('pubsub2inbox-rocks', request.headers['authorization'].substring(7)).iss != 'pubsub2inbox'",
			messageCel:  "request.json",
			responseCel: "",
			status:      403,
			body:        defaultJson,
			remoteAddr:  "127.0.0.1",
			headers: mergeMaps(defaultHeaders, map[string]string{
				"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwdWJzdWIyaW5ib3giLCJpYXQiOjE2ODM0NjA0MjEsImV4cCI6MTk2NzQ1NzI1MiwiYXVkIjoiZ2l0aHViLmNvbS9Hb29nbGVDbG91ZFBsYXRmb3JtL3B1YnN1YjJpbmJveCIsInN1YiI6ImFkbWluQGV4YW1wbGUuY29tIn0.UwsRpZTqZg03J8vcKDxHWg8CX4L_yijRF2tEDjpckEk",
			}),
			expect:     defaultJson,
			expectBody: "",
		},
		{
			testName:    "invalid JWT",
			controlCel:  "parseJWT('pubsub2inbox-rocks', request.headers['authorization'].substring(7)).iss == 'pubsub2inbox'",
			messageCel:  "request.json",
			responseCel: "",
			status:      500,
			body:        defaultJson,
			remoteAddr:  "127.0.0.1",
			headers: mergeMaps(defaultHeaders, map[string]string{
				"Authorization": "Bearer AyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwdWJzdWIyaW5ib3giLCJpYXQiOjE2ODM0NjA0MjEsImV4cCI6MTk2NzQ1NzI1MiwiYXVkIjoiZ2l0aHViLmNvbS9Hb29nbGVDbG91ZFBsYXRmb3JtL3B1YnN1YjJpbmJveCIsInN1YiI6ImFkbWluQGV4YW1wbGUuY29tIn0.UwsRpZTqZg03J8vcKDxHWg8CX4L_yijRF2tEDjpckEk",
			}),
			expect:     defaultJson,
			expectBody: "",
		},
		{
			testName:    "expired JWT",
			controlCel:  "parseJWT('pubsub2inbox-rocks', request.headers['authorization'].substring(7)).iss == 'pubsub2inbox'",
			messageCel:  "request.json",
			responseCel: "",
			status:      500,
			body:        defaultJson,
			remoteAddr:  "127.0.0.1",
			headers: mergeMaps(defaultHeaders, map[string]string{
				"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwdWJzdWIyaW5ib3giLCJpYXQiOjE2ODMyMDE0NjIsImV4cCI6MTY4MzI4ODEzNywiYXVkIjoiZ2l0aHViLmNvbS9Hb29nbGVDbG91ZFBsYXRmb3JtL3B1YnN1YjJpbmJveCIsInN1YiI6ImFkbWluQGV4YW1wbGUuY29tIiwiUmFuZG9tIjoiVmFsdWUifQ.0fPJcqhNslxP0hujs97vKVdyoUFfQC2NGtTrJqZm9qI",
			}),
			expect:     defaultJson,
			expectBody: "",
		},
		{
			testName: "valid Slack authentication",
			controlCel: `
				'x-slack-signature' in request.headers && 
				'x-slack-request-timestamp' in request.headers &&
				(request.unixtime - int(request.headers['x-slack-request-timestamp'])) < 3000000000 &&
				('v0='+hmacSHA256('8f742231b10e8888abcd99yyyzzz85a5', 'v0:'+request.headers['x-slack-request-timestamp']+':'+request.body)) == request.headers['x-slack-signature']
			`,
			messageCel:  "{\"username\": request.post.user_name[0]}",
			responseCel: "",
			status:      200,
			body:        "token=xyzz0WbapA4vBCDEFasx0q6G&team_id=T1DC2JH3J&team_domain=testteamnow&channel_id=G8PSS9T3V&channel_name=foobar&user_id=U2CERLKJA&user_name=roadrunner&command=%2Fwebhook-collect&text=&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT1DC2JH3J%2F397700885554%2F96rGlfmibIGlgcZRskXaIFfN&trigger_id=398738663015.47445629121.803a0bc887a14d10d2c447fce8b6703c",
			remoteAddr:  "127.0.0.1",
			headers: map[string]string{
				"Content-type":              "application/x-www-form-urlencoded",
				"X-Slack-Request-Timestamp": "1531420618",
				"X-Slack-Signature":         "v0=a2114d57b48eac39b9ad189dd8316235a7b4a8d21a10bd27519666489c69b503",
			},
			expect:     "{\"username\":\"roadrunner\"}",
			expectBody: "",
		},
		{
			testName: "invalid Slack authentication",
			controlCel: `
				'x-slack-signature' in request.headers && 
				'x-slack-request-timestamp' in request.headers &&
				(request.unixtime - int(request.headers['x-slack-request-timestamp'])) < 3000000000 &&
				('v0='+hmacSHA256('9f742231b10e8888abcd99yyyzzz85a5', 'v0:'+request.headers['x-slack-request-timestamp']+':'+request.body)) == request.headers['x-slack-signature']
			`,
			messageCel:  "{\"username\": request.post.user_name[0]}",
			responseCel: "",
			status:      403,
			body:        "token=xyzz0WbapA4vBCDEFasx0q6G&team_id=T1DC2JH3J&team_domain=testteamnow&channel_id=G8PSS9T3V&channel_name=foobar&user_id=U2CERLKJA&user_name=roadrunner&command=%2Fwebhook-collect&text=&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT1DC2JH3J%2F397700885554%2F96rGlfmibIGlgcZRskXaIFfN&trigger_id=398738663015.47445629121.803a0bc887a14d10d2c447fce8b6703c",
			remoteAddr:  "127.0.0.1",
			headers: map[string]string{
				"Content-type":              "application/x-www-form-urlencoded",
				"X-Slack-Request-Timestamp": "1531420618",
				"X-Slack-Signature":         "v0=a2114d57b48eac39b9ad189dd8316235a7b4a8d21a10bd27519666489c69b503",
			},
			expect:     "{\"username\":\"roadrunner\"}",
			expectBody: "",
		},
		{
			testName: "origin IP limitation, valid",
			controlCel: `
				origin.ip == "192.168.1.1"
			`,
			messageCel:  "request.post.jsoncontents[0]",
			responseCel: "",
			status:      200,
			body:        "jsoncontents=%7B%22foo%22%3A%22bar%22%7D",
			remoteAddr:  "192.168.1.1",
			headers: map[string]string{
				"Content-type": "application/x-www-form-urlencoded",
			},
			expect:     "{\"foo\":\"bar\"}",
			expectBody: "",
		},
		{
			testName: "origin IP limitation, invalid",
			controlCel: `
				origin.ip == "10.1.0.1"
			`,
			messageCel:  "request.post.jsoncontents[0]",
			responseCel: "",
			status:      403,
			body:        "jsoncontents=%7B%22foo%22%3A%22bar%22%7D",
			remoteAddr:  "192.168.1.1",
			headers: map[string]string{
				"Content-type": "application/x-www-form-urlencoded",
			},
			expect:     "{\"foo\":\"bar\"}",
			expectBody: "",
		},
		{
			testName: "origin IP range limitation, valid",
			controlCel: `
				ipInRange(origin.ip, "192.168.1.0/24")
			`,
			messageCel:  "request.post.jsoncontents[0]",
			responseCel: "",
			status:      200,
			body:        "jsoncontents=%7B%22foo%22%3A%22bar%22%7D",
			remoteAddr:  "192.168.1.1",
			headers: map[string]string{
				"Content-type": "application/x-www-form-urlencoded",
			},
			expect:     "{\"foo\":\"bar\"}",
			expectBody: "",
		},
		{
			testName: "origin IP range limitation, invalid",
			controlCel: `
				ipInRange(origin.ip, "192.168.1.0/24")
			`,
			messageCel:  "request.post.jsoncontents[0]",
			responseCel: "",
			status:      403,
			body:        "jsoncontents=%7B%22foo%22%3A%22bar%22%7D",
			remoteAddr:  "10.1.0.1",
			headers: map[string]string{
				"Content-type": "application/x-www-form-urlencoded",
			},
			expect:     "{\"foo\":\"bar\"}",
			expectBody: "",
		},
		{
			testName:    "test response string",
			controlCel:  "true",
			messageCel:  "{ 'type': request.json.type }",
			responseCel: "request.json.challenge",
			status:      200,
			body:        `{"token":"Jhj5dZrVaK7ZwHHjRyZWjbDl","challenge":"3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P","type":"url_verification"}`,
			remoteAddr:  "10.1.0.1",
			headers: map[string]string{
				"Content-type": "application/json",
			},
			expect:     `{"type":"url_verification"}`,
			expectBody: "3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P",
		},
		{
			testName:    "test response list",
			controlCel:  "true",
			messageCel:  "{ 'type': request.json.type }",
			responseCel: "[request.json.challenge]",
			status:      200,
			body:        `{"token":"Jhj5dZrVaK7ZwHHjRyZWjbDl","challenge":"3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P","type":"url_verification"}`,
			remoteAddr:  "10.1.0.1",
			headers: map[string]string{
				"Content-type": "application/json",
			},
			expect:     `{"type":"url_verification"}`,
			expectBody: `["3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P"]`,
		},
		{
			testName:    "test response map",
			controlCel:  "true",
			messageCel:  "{ 'type': request.json.type }",
			responseCel: "{'challenge':request.json.challenge}",
			status:      200,
			body:        `{"token":"Jhj5dZrVaK7ZwHHjRyZWjbDl","challenge":"3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P","type":"url_verification"}`,
			remoteAddr:  "10.1.0.1",
			headers: map[string]string{
				"Content-type": "application/json",
			},
			expect:     `{"type":"url_verification"}`,
			expectBody: `{"challenge":"3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P"}`,
		},
		{
			testName:    "test JSON string parse",
			controlCel:  "true",
			messageCel:  `parseJSON('{"foo":"bar"}')`,
			responseCel: "",
			status:      200,
			body:        `{}`,
			remoteAddr:  "10.1.0.1",
			headers: map[string]string{
				"Content-type": "application/json",
			},
			expect:     `{"foo":"bar"}`,
			expectBody: ``,
		},
	}
	GetPubsubTopic = getPubsubTopicMock
	for _, tt := range tests {
		t.Run(tt.testName, func(t *testing.T) {
			err = setControlCel(celEnv, tt.controlCel)
			assert.Nil(t, err)
			err = setMessageCel(celEnv, tt.messageCel)
			assert.Nil(t, err)
			err = setResponseBodyCel(celEnv, tt.responseCel)
			assert.Nil(t, err)

			r, err := makeHttpRequest(tt.remoteAddr, "POST", tt.body, tt.headers)
			assert.Nil(t, err)
			assert.IsType(t, r, &http.Request{})

			w := httptest.NewRecorder()
			RequestHandler(w, r)
			resp := w.Result()
			assert.Equal(t, tt.status, resp.StatusCode)

			respBody, err := ioutil.ReadAll(resp.Body)
			assert.Nil(t, err)
			assert.Equal(t, tt.expectBody, string(respBody))

			pubsubMockServer.Wait()
			if tt.expect != "" {
				for _, msg := range pubsubMockServer.Messages() {
					assert.Equal(t, tt.expect, string(msg.Data))
				}
			}
			pubsubMockServer.ClearMessages()
		})
	}
}

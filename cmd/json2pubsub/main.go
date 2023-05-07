package main

//    Copyright 2023 Google LLC
//
//    Licensed under the Apache License, Version 2.0 (the "License");
//    you may not use this file except in compliance with the License.
//    You may obtain a copy of the License at
//
//        http://www.apache.org/licenses/LICENSE-2.0
//
//    Unless required by applicable law or agreed to in writing, software
//    distributed under the License is distributed on an "AS IS" BASIS,
//    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//    See the License for the specific language governing permissions and
//    limitations under the License.
import (
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"os"
	"reflect"
	"strings"
	"time"

	"cloud.google.com/go/pubsub"
	secretmanager "cloud.google.com/go/secretmanager/apiv1"
	"cloud.google.com/go/secretmanager/apiv1/secretmanagerpb"
	"github.com/google/cel-go/cel"
	celtypes "github.com/google/cel-go/common/types"
	"google.golang.org/api/option"
)

var VERSION string = "0.1.0"

var requestControlExpr cel.Program
var extractMessage cel.Program

var pubsubTopic string
var cloudProjectId string
var userAgent string

func getEnvironmentVariable(name string, required bool) (string, error) {
	envVar := os.Getenv(name)
	if envVar == "" && required {
		log.Fatalf("Environment variable %s is required.", name)
	}
	// Check if this is a Secret Manager secret
	if strings.HasPrefix(envVar, "gsm:") {
		ctx := context.Background()
		client, err := secretmanager.NewClient(ctx, option.WithUserAgent(userAgent))
		if err != nil {
			log.Fatalf("Failed to setup Secret Manager client: %v", err)
		}
		defer client.Close()

		accessRequest := &secretmanagerpb.AccessSecretVersionRequest{
			Name: envVar[3:],
		}

		result, err := client.AccessSecretVersion(ctx, accessRequest)
		if err != nil {
			log.Fatalf("Failed to access Secret %s: %v", envVar[3:], err)
		}

		log.Printf("Plaintext: %s", result.Payload.Data)
		return string(result.Payload.Data), nil
	}
	return envVar, nil
}

func main() {
	log.Printf("Starting Json2Pubsub server, version %s...", VERSION)
	userAgent = fmt.Sprintf("google-pso-tool/json2pubsub/%s", VERSION)
	cloudProjectId = os.Getenv("GOOGLE_CLOUD_PROJECT")
	if cloudProjectId == "" {
		log.Fatalf("Environment variable GOOGLE_CLOUD_PROJECT is not set.")
	}
	log.Printf("Using cloud project: %s", cloudProjectId)

	var err error
	pubsubTopic, err = getEnvironmentVariable("PUBSUB_TOPIC", true)
	if err != nil {
		log.Fatalf("Failed to get PUBSUB_TOPIC: %v", err)
	}
	log.Printf("Using Pub/Sub topic: %s", pubsubTopic)

	handlerUrl, err := getEnvironmentVariable("CUSTOM_HANDLER", false)
	if err != nil {
		log.Fatalf("Failed to get CUSTOM_HANDLER: %v", err)
	}

	if handlerUrl == "" {
		handlerUrl = "/"
	} else {
		log.Printf("Using custom handler location: %s", handlerUrl)
	}
	http.HandleFunc("/", handler)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	celEnv, err := GetCelEnv()
	if err != nil {
		log.Fatalf("Failed to setup CEL environment: %v", err)
	}

	controlCel, err := getEnvironmentVariable("CONTROL_CEL", true)
	if err != nil {
		log.Fatalf("Failed to get CONTROL_CEL: %v", err)
	}
	requestControlExpr, err = GetCelProgram(celEnv, controlCel, true)
	if err != nil {
		log.Fatalf("Failed to compile request control CEL program (%s): %v", controlCel, err)
	}

	messageCel, err := getEnvironmentVariable("MESSAGE_CEL", true)
	if err != nil {
		log.Fatalf("Failed to get MESSAGE_CEL: %v", err)
	}
	extractMessage, err = GetCelProgram(celEnv, messageCel, false)
	if err != nil {
		log.Fatalf("Failed to compile message extract CEL program (%s): %v", messageCel, err)
	}

	log.Printf("Listening on TCP port %s", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal(err)
	}
}

func handler(w http.ResponseWriter, r *http.Request) {
	// Only accept POST requests
	if r.Method != "POST" {
		log.Printf("[%s] Not a POST request.", r.RemoteAddr)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	postBody, err := ioutil.ReadAll(r.Body)
	if err != nil {
		log.Printf("[%s] Failed to read request body: %v", r.RemoteAddr, err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}
	if len(postBody) == 0 {
		log.Printf("[%s] Empty request body.", r.RemoteAddr)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	requestHeaders := make(map[string]string, 0)
	for key := range r.Header {
		requestHeaders[strings.ToLower(key)] = r.Header.Get(key)
	}

	var postValues url.Values
	contentType := r.Header.Get("Content-Type")
	if contentType == "application/x-www-form-urlencoded" {
		postValues, err = url.ParseQuery(string(postBody))
		if err != nil {
			log.Printf("[%s] Failed to parse post body for application/x-www-form-urlencoded", r.RemoteAddr)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
	}

	var jsonBody interface{}
	if contentType == "application/json" || contentType == "text/json" {
		if json.Valid([]byte(postBody)) {
			json.Unmarshal([]byte(postBody), &jsonBody)
		} else {
			log.Printf("[%s] Invalid JSON body.", r.RemoteAddr)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
	} else {
		jsonBody = postValues
	}

	currentTime := time.Now()
	currentTimeUTC := currentTime.UTC()
	celParams := map[string]interface{}{
		"request": map[string]interface{}{
			"body":     string(postBody),
			"json":     jsonBody,
			"post":     postValues,
			"headers":  requestHeaders,
			"unixtime": currentTime.Unix(),
			"time": map[string]int{
				"year":   currentTimeUTC.Year(),
				"month":  int(currentTimeUTC.Month()),
				"day":    currentTimeUTC.Day(),
				"hour":   currentTimeUTC.Hour(),
				"minute": currentTimeUTC.Minute(),
				"second": currentTimeUTC.Second(),
			},
		},
	}

	out, _, err := requestControlExpr.Eval(celParams)
	if err != nil {
		log.Printf("[%s] Failed to evaluate request control check: %v", r.RemoteAddr, err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	result, ok := out.(celtypes.Bool)
	if !ok || result.Equal(celtypes.False).Value().(bool) {
		log.Printf("[%s] Request control check failed.", r.RemoteAddr)
		w.WriteHeader(http.StatusForbidden)
		return
	}

	messageOut, _, err := extractMessage.Eval(celParams)
	if err != nil {
		log.Printf("[%s] Failed to evaluate message extraction: %v", r.RemoteAddr, err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}
	var messageJson interface{}
	if messageOut.Type() == celtypes.StringType {
		_messageOut, err := messageOut.ConvertToNative(reflect.TypeOf(""))
		if err != nil {
			log.Printf("[%s] Failed to convert message output to string: %v", r.RemoteAddr, err)
			w.WriteHeader(http.StatusInternalServerError)
			return
		}
		if json.Valid([]byte(_messageOut.(string))) {
			json.Unmarshal([]byte(_messageOut.(string)), &messageJson)
		} else {
			log.Printf("[%s] Invalid JSON string.", r.RemoteAddr)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
	} else if messageOut.Type() == celtypes.MapType {
		_messageOut, err := messageOut.ConvertToNative(reflect.TypeOf(map[string]interface{}{}))
		if err != nil {
			log.Printf("[%s] Failed to convert message output to map: %v", r.RemoteAddr, err)
			w.WriteHeader(http.StatusInternalServerError)
			return
		}
		messageJson = _messageOut.(map[string]interface{})
	} else if messageOut.Type() == celtypes.ListType {
		_messageOut, err := messageOut.ConvertToNative(reflect.TypeOf([]interface{}{}))
		if err != nil {
			log.Printf("[%s] Failed to convert message output to list: %v", r.RemoteAddr, err)
			w.WriteHeader(http.StatusInternalServerError)
			return
		}
		messageJson = _messageOut.([]interface{})
	}
	if messageJson == nil {
		log.Printf("[%s] Failed to turn request into a Pub/Sub message.", r.RemoteAddr)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	client, err := pubsub.NewClient(r.Context(), cloudProjectId, option.WithUserAgent(userAgent))
	if err != nil {
		log.Printf("[%s] Unable to create Pub/Sub client: %v", r.RemoteAddr, err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}
	defer client.Close()

	messageData, err := json.Marshal(messageJson)
	if err != nil {
		log.Printf("[%s] Unable to marshal message data to JSON: %v", r.RemoteAddr, err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	msg := &pubsub.Message{
		Data: messageData,
	}

	log.Printf("[%s] Publishing a message to topic %s, len=%d", r.RemoteAddr, pubsubTopic, len(msg.Data))
	topic := client.Topic(pubsubTopic)
	if _, err := topic.Publish(r.Context(), msg).Get(r.Context()); err != nil {
		log.Printf("[%s] Unable to publish message to Pub/Sub topic: %v", r.RemoteAddr, err)
		w.WriteHeader(http.StatusServiceUnavailable)
		return
	}
	w.WriteHeader(http.StatusOK)
}

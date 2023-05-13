package function

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
	"net"
	"net/http"
	"net/url"
	"os"
	"reflect"
	"strings"
	"time"

	"cloud.google.com/go/pubsub"
	secretmanager "cloud.google.com/go/secretmanager/apiv1"
	"cloud.google.com/go/secretmanager/apiv1/secretmanagerpb"
	"github.com/GoogleCloudPlatform/functions-framework-go/functions"
	"github.com/google/cel-go/cel"
	celtypes "github.com/google/cel-go/common/types"
	"google.golang.org/api/option"

	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
)

var VERSION string = "0.2.0"

var requestControlExpr cel.Program
var extractMessage cel.Program
var responseBody cel.Program
var defaultResponseBody = true

var pubsubTopic string
var cloudProjectId string
var userAgent string

type GetPubsubTopicFunc func(ctx context.Context, cloudProjectId string, userAgent string, pubsubTopic string) (*pubsub.Topic, error)

func getPubsubTopicReal(ctx context.Context, cloudProjectId string, userAgent string, pubsubTopic string) (*pubsub.Topic, error) {
	client, err := pubsub.NewClient(ctx, cloudProjectId, option.WithUserAgent(userAgent))
	if err != nil {
		return nil, err
	}
	topic := client.Topic(pubsubTopic)
	return topic, nil
}

var GetPubsubTopic GetPubsubTopicFunc = getPubsubTopicReal

func getEnvironmentVariable(name string, required bool) (string, error) {
	envVar := os.Getenv(name)
	if envVar == "" && required {
		log.Fatal().Msgf("Environment variable %s is required.", name)
	}
	// Check if this is a Secret Manager secret
	if strings.HasPrefix(envVar, "gsm:") {
		ctx := context.Background()
		client, err := secretmanager.NewClient(ctx, option.WithUserAgent(userAgent))
		if err != nil {
			log.Fatal().Err(err).Msgf("Failed to setup Secret Manager client: %v", err)
		}
		defer client.Close()

		accessRequest := &secretmanagerpb.AccessSecretVersionRequest{
			Name: envVar[4:],
		}

		result, err := client.AccessSecretVersion(ctx, accessRequest)
		if err != nil {
			log.Fatal().Err(err).Msgf("Failed to access Secret %s: %v", envVar[4:], err)
		}
		return string(result.Payload.Data), nil
	}
	return envVar, nil
}

func setControlCel(celEnv *cel.Env, controlCel string) (err error) {
	requestControlExpr, err = GetCelProgram(celEnv, controlCel, true)
	if err != nil {
		return err
	}
	return nil
}

func setMessageCel(celEnv *cel.Env, messageCel string) (err error) {
	extractMessage, err = GetCelProgram(celEnv, messageCel, false)
	if err != nil {
		return err
	}
	return nil
}

func setResponseBodyCel(celEnv *cel.Env, bodyCel string) (err error) {
	if bodyCel != "" {
		responseBody, err = GetCelProgram(celEnv, bodyCel, false)
		if err != nil {
			return err
		}
		defaultResponseBody = false
	} else {
		defaultResponseBody = true
	}
	return nil
}

func Startup() (port string) {
	port = os.Getenv("PORT")
	if port == "" {
		// Probably not running as function, configure a more console friendly logger
		log.Logger = log.Output(zerolog.ConsoleWriter{Out: os.Stderr})
		port = "8080"
	}

	log.Info().Msgf("Starting Json2Pubsub server, version %s...", VERSION)

	userAgent = fmt.Sprintf("google-pso-tool/json2pubsub/%s", VERSION)
	cloudProjectId = os.Getenv("GOOGLE_CLOUD_PROJECT")
	if cloudProjectId == "" {
		log.Fatal().Msg("Environment variable GOOGLE_CLOUD_PROJECT is not set.")
	}
	log.Info().Msgf("Using cloud project: %s", cloudProjectId)

	var err error
	pubsubTopic, err = getEnvironmentVariable("PUBSUB_TOPIC", true)
	if err != nil {
		log.Fatal().Msgf("Failed to get PUBSUB_TOPIC: %v", err)
	}
	log.Info().Msgf("Using Pub/Sub topic: %s", pubsubTopic)

	handlerUrl, err := getEnvironmentVariable("CUSTOM_HANDLER", false)
	if err != nil {
		log.Fatal().Err(err).Msgf("Failed to get CUSTOM_HANDLER: %v", err)
	}

	if handlerUrl == "" {
		handlerUrl = "/"
	} else {
		log.Info().Msgf("Using custom handler location: %s", handlerUrl)
	}
	http.HandleFunc("/", RequestHandler)

	celEnv, err := GetCelEnv()
	if err != nil {
		log.Fatal().Err(err).Msgf("Failed to setup CEL environment: %v", err)
	}

	controlCel, err := getEnvironmentVariable("CONTROL_CEL", true)
	if err != nil {
		log.Fatal().Err(err).Msgf("Failed to get CONTROL_CEL: %v", err)
	}
	err = setControlCel(celEnv, controlCel)
	if err != nil {
		log.Fatal().Err(err).Msgf("Failed to compile request control CEL program (%s): %v", controlCel, err)
	}

	messageCel, err := getEnvironmentVariable("MESSAGE_CEL", true)
	if err != nil {
		log.Fatal().Err(err).Msgf("Failed to get MESSAGE_CEL: %v", err)
	}
	err = setMessageCel(celEnv, messageCel)
	if err != nil {
		log.Fatal().Err(err).Msgf("Failed to compile message extract CEL program (%s): %v", messageCel, err)
	}

	responseCel, err := getEnvironmentVariable("RESPONSE_CEL", false)
	if err != nil {
		log.Fatal().Err(err).Msgf("Failed to get RESPONCE_CEL: %v", err)
	}
	err = setResponseBodyCel(celEnv, responseCel)
	if err != nil {
		log.Fatal().Err(err).Msgf("Failed to compile message extract CEL program (%s): %v", messageCel, err)
	}
	if responseCel == "" {
		log.Info().Msg("No response body CEL specified, using empty responses.")
	}
	return port
}

func init() {
	// Slightly ugly hack for testing
	if !strings.HasSuffix(os.Args[0], ".test") {
		Startup()
	} else {
		zerolog.SetGlobalLevel(zerolog.Disabled)
	}

	functions.HTTP("Json2Pubsub", RequestHandler)
}

func RequestHandler(w http.ResponseWriter, r *http.Request) {
	originIp, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		log.Warn().Err(err).Str("RemoteAddr", r.RemoteAddr).Msg("Unable to parse remote address")
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	// Only accept POST requests
	if r.Method != "POST" {
		log.Warn().Str("RemoteAddr", r.RemoteAddr).Msg("Not a POST request.")
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	postBody, err := ioutil.ReadAll(r.Body)
	if err != nil {
		log.Warn().Err(err).Str("RemoteAddr", r.RemoteAddr).Msgf("Failed to read request body: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}
	if len(postBody) == 0 {
		log.Warn().Str("RemoteAddr", r.RemoteAddr).Msg("Empty request body.")
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
			log.Warn().Str("RemoteAddr", r.RemoteAddr).Msg("Failed to parse post body for content type application/x-www-form-urlencoded")
			w.WriteHeader(http.StatusBadRequest)
			return
		}
	}

	var jsonBody interface{}
	if contentType == "application/json" || contentType == "text/json" {
		if json.Valid([]byte(postBody)) {
			json.Unmarshal([]byte(postBody), &jsonBody)
		} else {
			log.Warn().Str("RemoteAddr", r.RemoteAddr).Msg("Invalid JSON body.")
			w.WriteHeader(http.StatusBadRequest)
			return
		}
	} else {
		jsonBody = postValues
	}

	// Set up request structure
	currentTime := time.Now()
	currentTimeUTC := currentTime.UTC()
	celParams := map[string]interface{}{
		"origin": map[string]interface{}{
			"ip": originIp,
		},
		"request": map[string]interface{}{
			"body":     string(postBody),
			"method":   r.Method,
			"path":     r.URL.RawPath,
			"scheme":   r.URL.Scheme,
			"query":    r.URL.RawQuery,
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
		log.Error().Err(err).Str("RemoteAddr", r.RemoteAddr).Msgf("Failed to evaluate request control check: %v", out)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	result, ok := out.(celtypes.Bool)
	if !ok || result.Equal(celtypes.False).Value().(bool) {
		log.Error().Str("RemoteAddr", r.RemoteAddr).Msgf("Request control check failed: %v", out)
		w.WriteHeader(http.StatusForbidden)
		return
	}

	messageOut, _, err := extractMessage.Eval(celParams)
	if err != nil {
		log.Error().Err(err).Str("RemoteAddr", r.RemoteAddr).Msgf("Failed to evaluate message extraction: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}
	var messageJson interface{}
	if messageOut.Type() == celtypes.StringType {
		_messageOut, err := messageOut.ConvertToNative(reflect.TypeOf(""))
		if err != nil {
			log.Error().Err(err).Str("RemoteAddr", r.RemoteAddr).Msgf("Failed to convert message output to string: %v", err)
			w.WriteHeader(http.StatusInternalServerError)
			return
		}
		if json.Valid([]byte(_messageOut.(string))) {
			json.Unmarshal([]byte(_messageOut.(string)), &messageJson)
		} else {
			log.Error().Str("RemoteAddr", r.RemoteAddr).Str("json", _messageOut.(string)).Msg("Invalid JSON string from message CEL.")
			w.WriteHeader(http.StatusBadRequest)
			return
		}
	} else if messageOut.Type() == celtypes.MapType {
		_messageOut, err := messageOut.ConvertToNative(reflect.TypeOf(map[string]interface{}{}))
		if err != nil {
			log.Error().Err(err).Str("RemoteAddr", r.RemoteAddr).Msgf("Failed to convert message output to map: %v", err)
			w.WriteHeader(http.StatusInternalServerError)
			return
		}
		messageJson = _messageOut.(map[string]interface{})
	} else if messageOut.Type() == celtypes.ListType {
		_messageOut, err := messageOut.ConvertToNative(reflect.TypeOf([]interface{}{}))
		if err != nil {
			log.Error().Err(err).Str("RemoteAddr", r.RemoteAddr).Msgf("Failed to convert message output to list: %v", err)
			w.WriteHeader(http.StatusInternalServerError)
			return
		}
		messageJson = _messageOut.([]interface{})
	}
	if messageJson == nil {
		log.Error().Str("RemoteAddr", r.RemoteAddr).Msg("Failed to turn request into a Pub/Sub message.")
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	messageData, err := json.Marshal(messageJson)
	if err != nil {
		log.Error().Err(err).Str("RemoteAddr", r.RemoteAddr).Msgf("Unable to marshal message data to JSON: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	msg := &pubsub.Message{
		Data: messageData,
	}

	topic, err := GetPubsubTopic(r.Context(), cloudProjectId, userAgent, pubsubTopic)
	if err != nil {
		log.Error().Err(err).Str("RemoteAddr", r.RemoteAddr).Msg("Unable to get Pub/Sub client for topic.")
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	log.Info().Str("RemoteAddr", r.RemoteAddr).Msgf("Publishing a message to topic %s, len=%d bytes", topic.String(), len(msg.Data))
	if _, err := topic.Publish(r.Context(), msg).Get(r.Context()); err != nil {
		log.Error().Err(err).Str("RemoteAddr", r.RemoteAddr).Msgf("Unable to publish message to Pub/Sub topic: %v", err)
		w.WriteHeader(http.StatusServiceUnavailable)
		return
	}

	if !defaultResponseBody {
		bodyOut, _, err := responseBody.Eval(celParams)
		if err != nil || bodyOut == nil {
			log.Error().Err(err).Str("RemoteAddr", r.RemoteAddr).Msgf("Failed to evaluate response boy: %v", err)
			w.WriteHeader(http.StatusInternalServerError)
			return
		}
		if bodyOut.Type() == celtypes.StringType {
			_bodyOut, err := bodyOut.ConvertToNative(reflect.TypeOf(""))
			if err != nil {
				log.Error().Err(err).Str("RemoteAddr", r.RemoteAddr).Msgf("Failed to convert response body to string: %v", err)
				w.WriteHeader(http.StatusInternalServerError)
				return
			}
			w.WriteHeader(http.StatusOK)
			w.Write([]byte(_bodyOut.(string)))
		} else if bodyOut.Type() == celtypes.MapType {
			_bodyOut, err := bodyOut.ConvertToNative(reflect.TypeOf(map[string]interface{}{}))
			if err != nil {
				log.Error().Err(err).Str("RemoteAddr", r.RemoteAddr).Msgf("Failed to convert response body to map: %v", err)
				w.WriteHeader(http.StatusInternalServerError)
				return
			}
			_bodyAsMap := _bodyOut.(map[string]interface{})
			_bodyJson, err := json.Marshal(_bodyAsMap)
			if err != nil {
				log.Error().Err(err).Str("RemoteAddr", r.RemoteAddr).Msgf("Failed to convert response body map to JSON: %v", err)
				w.WriteHeader(http.StatusInternalServerError)
				return
			}
			w.WriteHeader(http.StatusOK)
			w.Write(_bodyJson)
		} else if bodyOut.Type() == celtypes.ListType {
			_bodyOut, err := bodyOut.ConvertToNative(reflect.TypeOf([]interface{}{}))
			if err != nil {
				log.Error().Err(err).Str("RemoteAddr", r.RemoteAddr).Msgf("Failed to convert response body to list: %v", err)
				w.WriteHeader(http.StatusInternalServerError)
				return
			}
			_bodyAsList := _bodyOut.([]interface{})
			_bodyJson, err := json.Marshal(_bodyAsList)
			if err != nil {
				log.Error().Err(err).Str("RemoteAddr", r.RemoteAddr).Msgf("Failed to convert response body list to JSON: %v", err)
				w.WriteHeader(http.StatusInternalServerError)
				return
			}
			w.WriteHeader(http.StatusOK)
			w.Write(_bodyJson)
		}
	} else {
		w.WriteHeader(http.StatusOK)
	}
}

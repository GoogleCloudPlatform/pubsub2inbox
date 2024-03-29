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
	"fmt"
	"net"
	"reflect"

	"crypto/hmac"
	"crypto/sha1"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"

	"github.com/google/cel-go/cel"
	"github.com/google/cel-go/common/types"
	"github.com/google/cel-go/common/types/ref"
	"github.com/google/cel-go/ext"

	jwt "github.com/golang-jwt/jwt/v5"
)

type CelLib struct{}

func GetCelEnv() (*cel.Env, error) {
	env, err := cel.NewEnv(
		ext.Strings(),
		ext.Encoders(),
		cel.Variable("request", cel.MapType(cel.StringType, cel.DynType)),
		cel.Variable("origin", cel.MapType(cel.StringType, cel.DynType)),
		cel.Function("ipInRange",
			cel.Overload("string_ipInRange_string",
				[]*cel.Type{cel.StringType, cel.StringType},
				cel.BoolType,
				cel.BinaryBinding(func(ipAddr, ipRange ref.Val) ref.Val {
					_ipAddr, err := ipAddr.ConvertToNative(reflect.TypeOf(""))
					if err != nil {
						return types.NewErr("IP address is not a string")
					}
					_ipRange, err := ipRange.ConvertToNative(reflect.TypeOf(""))
					if err != nil {
						return types.NewErr("IP range is not a string")
					}

					ipAddrParsed := net.ParseIP(_ipAddr.(string))
					if ipAddrParsed == nil {
						return types.NewErr("Invalid IP address")
					}

					_, ipRangeParsed, err := net.ParseCIDR(_ipRange.(string))
					if err != nil {
						return types.NewErr("Invalid IP range")
					}

					if ipRangeParsed.Contains(ipAddrParsed) {
						return types.Bool(true)
					}
					return types.Bool(false)

				},
				),
			),
		),
		cel.Function("parseJSON",
			cel.Overload("dynmap_parseJSON_string",
				[]*cel.Type{cel.StringType},
				cel.MapType(cel.StringType, cel.DynType),
				cel.UnaryBinding(func(jsonValue ref.Val) ref.Val {
					_jsonValue, err := jsonValue.ConvertToNative(reflect.TypeOf(""))
					if err != nil {
						return types.NewErr("JSON value is not a string")
					}
					var jsonParsed map[string]interface{}
					if !json.Valid([]byte(_jsonValue.(string))) {
						return types.NewErr("JSON value is not valid")
					}
					json.Unmarshal([]byte(_jsonValue.(string)), &jsonParsed)

					return types.NewStringInterfaceMap(types.DefaultTypeAdapter, jsonParsed)
				},
				),
			),
		),
		cel.Function("parseJWT",
			cel.Overload("string_parseJWT_string",
				[]*cel.Type{cel.StringType, cel.StringType},
				cel.MapType(cel.StringType, cel.DynType),
				cel.BinaryBinding(func(jwtKey, jwtValue ref.Val) ref.Val {
					_jwtKey, err := jwtKey.ConvertToNative(reflect.TypeOf(""))
					if err != nil {
						return types.NewErr("JWT key is not a string")
					}
					_jwtValue, err := jwtValue.ConvertToNative(reflect.TypeOf(""))
					if err != nil {
						return types.NewErr("JWT value is not a string")
					}
					claims := jwt.MapClaims{}
					token, err := jwt.ParseWithClaims(_jwtValue.(string), claims, func(token *jwt.Token) (interface{}, error) {
						return []byte(_jwtKey.(string)), nil
					}, jwt.WithIssuedAt())
					if err != nil {
						return types.NewErr("Failed to parse JWT")
					}
					if !token.Valid {
						return types.NewErr("JWT is not valid")
					}

					claimsOut := make(map[string]interface{}, 0)
					for key, val := range claims {
						claimsOut[key] = val
					}

					return types.NewStringInterfaceMap(types.DefaultTypeAdapter, claimsOut)
				},
				),
			),
		),
		cel.Function("hmacSHA256",
			cel.Overload("string_hmacSHA256_string",
				[]*cel.Type{cel.StringType, cel.StringType},
				cel.StringType,
				cel.BinaryBinding(func(hmacKey, hmacValue ref.Val) ref.Val {
					_hmacKey, err := hmacKey.ConvertToNative(reflect.TypeOf(""))
					if err != nil {
						return types.NewErr("HMAC key is not a string")
					}
					_hmacValue, err := hmacValue.ConvertToNative(reflect.TypeOf(""))
					if err != nil {
						return types.NewErr("HMAC value is not a string")
					}

					mac := hmac.New(sha256.New, []byte(_hmacKey.(string)))
					mac.Write([]byte(_hmacValue.(string)))
					macSum := mac.Sum(nil)
					return types.String(hex.EncodeToString(macSum))
				},
				),
			),
		),
		cel.Function("hmacSHA1",
			cel.Overload("string_hmacSHA1_string",
				[]*cel.Type{cel.StringType, cel.StringType},
				cel.StringType,
				cel.BinaryBinding(func(hmacKey, hmacValue ref.Val) ref.Val {
					_hmacKey, err := hmacKey.ConvertToNative(reflect.TypeOf(""))
					if err != nil {
						return types.NewErr("HMAC key is not a string")
					}
					_hmacValue, err := hmacValue.ConvertToNative(reflect.TypeOf(""))
					if err != nil {
						return types.NewErr("HMAC value is not a string")
					}

					mac := hmac.New(sha1.New, []byte(_hmacKey.(string)))
					mac.Write([]byte(_hmacValue.(string)))
					macSum := mac.Sum(nil)
					return types.String(hex.EncodeToString(macSum))
				},
				),
			),
		),
	)
	return env, err
}

func GetCelProgram(env *cel.Env, expr string, mustBeBool bool) (cel.Program, error) {
	celAst, celIss := env.Compile(expr)
	if celIss.Err() != nil {
		return nil, fmt.Errorf("Encountered error when compiling instance CEL: %s\n", celIss.Err())
	}
	if mustBeBool {
		if celAst.OutputType() != cel.BoolType {
			return nil, fmt.Errorf("Error compiling CEL, got %v as return value, wanted type bool", celAst.OutputType())
		}
	}

	celPrg, err := env.Program(celAst)
	if err != nil {
		return nil, fmt.Errorf("Encountered error when processing instance CEL: %s\n", err.Error())
	}
	return celPrg, nil
}

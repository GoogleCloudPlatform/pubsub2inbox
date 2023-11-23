#!/bin/bash
#   Copyright 2023 Google LLC
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
set -euo pipefail

CLOUD_RUN_TASK_INDEX=${CLOUD_RUN_TASK_INDEX:=0}
CLOUD_RUN_TASK_ATTEMPT=${CLOUD_RUN_TASK_ATTEMPT:=0}

echo "Starting Cloud Run job ${CLOUD_RUN_JOB}, execution ${CLOUD_RUN_EXECUTION}, task #${CLOUD_RUN_TASK_INDEX}, attempt #${CLOUD_RUN_TASK_ATTEMPT}..."

echo "Your fortune is:"
/usr/games/fortune

# If we have a Pub/Sub topic, post the details of this execution to it
if [ -n "${PUBSUB_TOPIC}" ] ;
then
    # Grab a token from the metadata endpoint
    TOKEN=$(curl -sH "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token" | jq -r ".access_token")
    # Encode the task information in JSON and wrap it in base64
    MESSAGE=$(echo -n "{\"job\":\"${CLOUD_RUN_JOB}\",\"execution\":\"${CLOUD_RUN_EXECUTION}\",\"index\":${CLOUD_RUN_TASK_INDEX},\"attempt\":${CLOUD_RUN_TASK_ATTEMPT}}" )
    MESSAGE_B64=$(echo $MESSAGE | base64 | tr -d \\n)
    # Post a message to the public topic
    curl -sH "Authorization: Bearer ${TOKEN}" \
      -H "Content-Type: application/json" \
      -X POST \
      -d "{'messages':[{'data':'${MESSAGE_B64}'}]}" \
      "https://pubsub.googleapis.com/v1/${PUBSUB_TOPIC}:publish"
fi

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
FROM marketplace.gcr.io/google/debian12:latest

ENV PUBSUB_TOPIC projects/example-projects/topics/example-topic

RUN apt-get update && \ 
    DEBIAN_FRONTEND=noninteractive apt-get upgrade -y && \
    apt-get install -y fortune-mod curl jq

COPY hello_world.sh /hello_world.sh
RUN chmod +x /hello_world.sh

ENTRYPOINT ["/hello_world.sh"]
#   Copyright 2024 Google LLC
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

# Synchronize changes from Artifactory Docker registry into Google Cloud
# Artifact Registry
pipeline:
  - type: processor.genericjson
  - type: output.logger
    config:
      message: |
        Webhook details: {{ data }}

  - type: processor.docker
    runIf: "{% if data.event_type == 'pushed' %}1{% endif %}"
    config:
      mode: image.copy
      hostname: "{{ data.jpd_origin }}"
      username: "${username}"
      password: "${password}"
      image: "{{ data.data.repo_key }}/{{ data.data.image_name }}"
      tag: "{{ data.data.tag }}"
      destination_hostname: "${ar_hostname}"
      destination_image: "${project_id}/${ar_repository}/{{ data.data.image_name }}"
      tls_verify: ${tls_verify}

  - type: processor.docker
    runIf: "{% if data.event_type == 'deleted' %}1{% endif %}"
    config:
      mode: image.deleteversion
      hostname: "${ar_hostname}"
      image: "${project_id}/${ar_repository}/{{ data.data.image_name }}"
      tag: "{{ data.data.tag }}"
      tls_verify: ${tls_verify}


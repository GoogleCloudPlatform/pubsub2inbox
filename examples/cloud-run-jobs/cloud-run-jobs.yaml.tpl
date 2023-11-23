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

# Query Cloud Run job logs from Cloud Logging and send them via email.
pipeline:
  - type: processor.genericjson
  - type: output.logger
    config:
      message: |
        Cloud Run Job details: {{ data }}
  - type: processor.cloudrun
    output: job_execution
    config:
      location: "${region}"
      job: "{{ data.job }}"
      execution: "{{ data.execution }}"
      mode: jobs.executions.get
  - type: output.logger
    config:
      message: |
        Job execution: {{ job_execution }}
  - type: processor.logging
    output: log_messages
    config:
      mode: logging.entries
      format: with-timestamps
      resourceNames:
        - "projects/${project_id}"
      filter: |
        resource.type="cloud_run_job"
        resource.labels.job_name="{{ job_execution.job }}"
        resource.labels.location="${region}"
        labels."run.googleapis.com/execution_name"="{{ data.execution }}"
        timestamp>="{{ job_execution.createTime }}"
        timestamp<="{{ job_execution.completionTime }}"
  - type: output.logger
    config:
      message: |
        Logs: {{ log_messages }}
  - type: output.mail
    config:
      transports:
        %{~ if sendgrid_api_token != null }
        - type: sendgrid
          apiKey: "${sendgrid_api_token}"
        %{~ else }
        - type: smtp
          host: smtp-relay.gmail.com
          port: 587
          starttls: true
          %{~ if username != null && password != null }
          user: "${username}"
          password: "${password}"
          %{~ endif }
        %{~ endif }
      from: ${sender}
      to: ${recipient}
      subject: |
        Cloud Run Job {{ job_execution.job }} finished
      body:
        text: |
          The Cloud Run job finished on {{ job_execution.completionTime }} and its output was:

          {% for msg in log_messages -%}
          {{ msg }}
          {% endfor %}

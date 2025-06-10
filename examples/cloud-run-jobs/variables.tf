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

variable "project_id" {
  type        = string
  description = "Google Cloud project ID"
}

variable "region" {
  type        = string
  description = "Region to deploy into"
  default     = "europe-west4"
}

variable "job_container" {
  type        = string
  description = "Cloud Run job container"
}

variable "sender" {
  type        = string
  description = "Email sender"
}

variable "recipient" {
  type        = string
  description = "Recipient for the email notifications"
}

variable "username" {
  type        = string
  description = "Username from smtp-relay.gmail.com (Workspace email address)"
  default     = null
}

variable "password" {
  type        = string
  description = "Password from smtp-relay.gmail.com (Workspace account)"
  default     = null
}

variable "sendgrid_api_token" {
  type        = string
  description = "SendGrid API token"
  default     = null
}



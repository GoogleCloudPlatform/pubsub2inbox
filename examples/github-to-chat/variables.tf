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
  description = "Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "Region where to deploy Cloud Functions"
  type        = string
}

variable "deployer_sa" {
  description = "IAM binding for the deploying service account (eg. a@b.iam.gserviceaccount.com)"
  type        = string
  default     = null
}

variable "pubsub_topic" {
  description = "Pub/Sub topic name"
  type        = string
  default     = "pubsub2inbox-github"
}

variable "github_secret" {
  description = "GitHub webhook secret"
  type        = string
}
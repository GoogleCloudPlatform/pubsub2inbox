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

variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "create_custom_role" {
  description = "Create a custom role containing only the bare minimum necessary permissions"
  type        = bool
  default     = true
}

variable "region" {
  description = "Region where to deploy Cloud Functions"
  type        = string
}

variable "vertex_region" {
  description = "Region where to call Vertex GenAI resources from"
  type        = string
  default     = "us-central1"
}

variable "vertex_model" {
  description = "Vertex AI model to use"
  type        = string
  default     = "gemini-1.0-pro"
}

variable "vertex_model_multimodal" {
  description = "Vertex AI multimodal model to use"
  type        = string
  default     = "gemini-1.0-pro-vision"
}

variable "slack_token" {
  description = "Slack bot token"
  type        = string
}

variable "slack_app_id" {
  description = "Slack app ID"
  type        = string
}

variable "slack_signing_key" {
  description = "Slack signing key"
  type        = string
}

variable "pubsub_topic" {
  description = "Pub/Sub topic name"
  type        = string
  default     = "pubsub2inbox-gemini-pro-bot"
}

variable "vertex_search" {
  description = "Integrate Vertex Search as a Gemini function"
  type = object({
    enabled      = optional(bool, false)
    location     = optional(string)
    datastore_id = optional(string)
  })
}

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
  type        = string
  description = "Google Cloud project ID"
}

variable "region" {
  type        = string
  description = "Region to deploy into"
  default     = "europe-west4"
}

variable "vpc_config" {
  type = object({
    network          = string
    network_project  = optional(string)
    cidr             = string
    create_connector = optional(bool, true)
    connector        = optional(string)
  })
  description = "Settings for deploying Serverless VPC Connector"
}

variable "artifact_registry_repository" {
  type        = string
  description = "Name of the Artifact Registry repository. Must match the repository on Artifactory side."
  default     = "pubsub2inbox"
}

variable "artifactory_username" {
  type        = string
  description = "Artifactory username for pulling images"
  sensitive   = true
}

variable "artifactory_password" {
  type        = string
  description = "Artifactory password for pulling images"
  sensitive   = true
}

variable "artifactory_webhook_secret" {
  type        = string
  description = "Artifactory webhook secret"
  sensitive   = true
}

variable "tls_verify" {
  type        = bool
  default     = true
  description = "Set false to disable TLS verify of JFrog's cert. This allows JFrog to use a self-signed cert."
}

variable "ingress_settings" {
  type        = string
  # See
  #   - https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloudfunctions2_function#ingress_settings
  #   - https://cloud.google.com/functions/docs/networking/network-settings#ingress_settings
  description = "VPC Service Controls ingress settings for the Cloud Functions. Default value is ALLOW_ALL. Possible values are: ALLOW_ALL, ALLOW_INTERNAL_ONLY, ALLOW_INTERNAL_AND_GCLB."
  default     = "ALLOW_ALL"
}

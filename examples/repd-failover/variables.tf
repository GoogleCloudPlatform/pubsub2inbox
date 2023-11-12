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

variable "zones" {
  type = object({
    primary   = string
    secondary = string
  })
  description = "Zones to deploy into"
  default = {
    primary   = "europe-west4-b"
    secondary = "europe-west4-c"
  }
}

variable "vpc_config" {
  description = "Network and subnetwork configuration."
  type = object({
    network         = optional(string, "failover-vpc")
    subnetwork      = optional(string, "failover-vpc-subnet")
    vpc_create      = optional(bool, false)
    subnetwork_cidr = optional(string, "192.168.123.0/24")
  })
  default = {
    vpc_create = true
  }
}
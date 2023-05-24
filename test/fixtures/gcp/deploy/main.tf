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

terraform {
  required_version = ">= 1.4.4"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.60.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = ">= 4.60.0"
    }
  }
}

module "project" {
  source         = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/project?ref=daily-2023.05.06"
  name           = var.project_id
  project_create = false
  services = [
    "serviceusage.googleapis.com",
    "cloudfunctions.googleapis.com",
    "run.googleapis.com",
    "eventarc.googleapis.com",
  ]
}

module "pubsub-topic" {
  source     = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/pubsub?ref=daily-2023.05.06"
  project_id = module.project.project_id
  name       = format("p2i-test-%s", random_string.random.result)
  iam        = {}
}

resource "random_string" "random" {
  length  = 8
  special = false
  upper   = false
}

# Manage service account manually, as it needs to go into the configuration file
resource "google_service_account" "service-account" {
  project = module.project.project_id

  account_id   = format("p2i-test-%s", random_string.random.result)
  display_name = "Pubsub2Inbox acceptance test account"
}

module "function-cfv2" {
  source = "../../../.."

  project_id         = module.project.project_id
  region             = var.region
  cloud_functions_v2 = true

  function_name = format("p2i-test-cfv2-%s", random_string.random.result)

  create_service_account = true
  grant_token_creator    = true

  pubsub_topic = module.pubsub-topic.id

  config = templatefile("${path.module}/test-config.yaml", {
    service_account_email = google_service_account.service-account.email
  })
  use_local_files  = true
  local_files_path = "../../../../"

  bucket_name     = format("p2i-test-cfv2-%s", random_string.random.result)
  bucket_location = var.region

  function_roles = []
}

module "function-cfv1" {
  source = "../../../.."

  project_id         = module.project.project_id
  region             = var.region
  cloud_functions_v2 = false

  function_name = format("p2i-test-cfv1-%s", random_string.random.result)

  create_service_account = true
  grant_token_creator    = true

  pubsub_topic = module.pubsub-topic.id

  config = templatefile("${path.module}/test-config.yaml", {
    service_account_email = google_service_account.service-account.email
  })
  use_local_files  = true
  local_files_path = "../../../../"

  bucket_name     = format("p2i-test-cfv1-%s", random_string.random.result)
  bucket_location = var.region

  function_roles = []
}

# module "function-cr" {
#   source = "../.."

#   project_id = module.project.project_id
#   region     = var.region
#   cloud_run  = true

#   function_name = format("p2i-test-cfv2-%s", random_string.random.result)

#   create_service_account = true
#   grant_token_creator    = true

#   pubsub_topic = module.pubsub-topic.id

#   config = templatefile("${path.module}/test-config.yaml", {
#     service_account_email = google_service_account.service-account.email
#   })
#   use_local_files  = true
#   local_files_path = "../../../../"

#   bucket_name     = format("p2i-test-cfv2-%s", random_string.random.result)
#   bucket_location = var.region

#   function_roles = []
# }

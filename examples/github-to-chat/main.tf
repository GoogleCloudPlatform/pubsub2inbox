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
  backend "gcs" {
  }
}

module "project" {
  source         = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/project?ref=daily-2023.05.06"
  name           = var.project_id
  project_create = false
  services = [
    "serviceusage.googleapis.com",
    "chat.googleapis.com",
    "cloudfunctions.googleapis.com",
    "run.googleapis.com",
    "eventarc.googleapis.com",
  ]
}

module "pubsub-topic" {
  source     = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/pubsub?ref=daily-2023.05.06"
  project_id = module.project.project_id
  name       = var.pubsub_topic
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

  account_id   = "github-bot"
  display_name = "GitHub bot service account"
}

resource "google_service_account_iam_member" "service-account-user" {
  service_account_id = google_service_account.service-account.name
  role               = "roles/iam.serviceAccountUser"
  member             = format("serviceAccount:%s", var.deployer_sa)
}

data "google_service_account" "compute-default-sa" {
  account_id = format("%d-compute@developer.gserviceaccount.com", module.project.number)
}

resource "google_service_account_iam_member" "compute-service-account-user" {
  service_account_id = data.google_service_account.compute-default-sa.name
  role               = "roles/iam.serviceAccountUser"
  member             = format("serviceAccount:%s", var.deployer_sa)
}

module "function" {
  source = "../.."

  project_id         = module.project.project_id
  region             = var.region
  cloud_functions_v2 = true

  function_name = "github-bot"

  service_account        = google_service_account.service-account.email
  create_service_account = false
  grant_token_creator    = true

  pubsub_topic = module.pubsub-topic.id

  config = templatefile("${path.module}/github-bot.yaml", {
    service_account_email = google_service_account.service-account.email
  })
  use_local_files  = true
  local_files_path = "../.."

  bucket_name     = format("github-bot-build-%s", random_string.random.result)
  bucket_location = var.region

  function_roles = []

  deploy_json2pubsub = {
    enabled = true
    suffix  = "-json2pubsub"
    control_cel = format(<<-EOT
      'x-hub-signature-256' in request.headers &&
      ('sha256='+hmacSHA256('%s', request.body)) == request.headers['x-hub-signature-256']
    EOT
    , var.github_secret)
    message_cel     = "request.json"
    response_cel    = "'OK'"
    public_access   = true
    container_image = null
    min_instances   = 0
    max_instances   = 2
    grant_sa_user   = var.deployer_sa
  }
  depends_on = [
    google_service_account_iam_member.service-account-user,
    google_service_account_iam_member.compute-service-account-user
  ]
}

resource "google_cloud_run_service_iam_member" "member" {
  location = module.function.run_service.location
  project  = module.function.run_service.project
  service  = module.function.run_service.service
  role     = "roles/run.invoker"
  member   = format("serviceAccount:%s", data.google_service_account.compute-default-sa.email)
}
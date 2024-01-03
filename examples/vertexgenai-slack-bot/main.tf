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
    "aiplatform.googleapis.com",
    "cloudfunctions.googleapis.com",
    "run.googleapis.com",
    "artifactregistry.googleapis.com"
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

module "function" {
  source = "../.."

  project_id         = module.project.project_id
  region             = var.region
  cloud_functions_v2 = true

  function_name = "vertex-genai-bot"

  service_account        = "vertex-genai-bot"
  create_service_account = true

  pubsub_topic = module.pubsub-topic.id

  config = templatefile("${path.module}/slack-bot.yaml", {
    slack_token   = var.slack_token
    slack_app_id  = var.slack_app_id
    vertex_region = var.vertex_region
    vertex_model  = var.vertex_model
  })
  use_local_files  = true
  local_files_path = "../.."

  bucket_name     = format("vertex-genai-bot-build-%s", random_string.random.result)
  bucket_location = var.region

  function_roles = var.create_custom_role ? [] : ["vertexai-user"]

  deploy_json2pubsub = {
    enabled = true
    suffix  = "-json2pubsub"
    control_cel = format(<<-EOT
      'x-slack-signature' in request.headers && 
      'x-slack-request-timestamp' in request.headers &&
      (request.unixtime - int(request.headers['x-slack-request-timestamp'])) < 300 &&
      ('v0='+hmacSHA256('%s', 'v0:'+request.headers['x-slack-request-timestamp']+':'+request.body)) == request.headers['x-slack-signature']
    EOT
    , var.slack_signing_key)
    message_cel     = "request.json"
    response_cel    = "'challenge' in request.json ? request.json.challenge : 'OK'"
    public_access   = true
    container_image = null
    min_instances   = 0
    max_instances   = 10
    grant_sa_user   = null
  }
}

resource "google_project_iam_custom_role" "custom-role" {
  count       = var.create_custom_role ? 1 : 0
  project     = module.project.project_id
  role_id     = "vertexAiPredict"
  title       = "Vertex AI predict only"
  description = "Only allow to perform online predictions"
  permissions = ["aiplatform.endpoints.predict"]
  stage       = "BETA"
}

resource "google_project_iam_member" "custom-role-binding" {
  count   = var.create_custom_role ? 1 : 0
  project = module.project.project_id
  role    = google_project_iam_custom_role.custom-role[0].id
  member  = format("serviceAccount:%s", module.function.service_account)
}


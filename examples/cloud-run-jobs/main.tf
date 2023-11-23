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

module "project" {
  source         = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/project?ref=daily-2023.11.11"
  name           = var.project_id
  project_create = false
  services = [
    "compute.googleapis.com",
    "cloudfunctions.googleapis.com",
    "run.googleapis.com",
    "pubsub.googleapis.com",
  ]
}

module "job-service-account" {
  source     = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/iam-service-account?ref=daily-2023.11.11"
  project_id = module.project.project_id
  name       = "cloud-run-job"
  iam        = {}
}

module "pubsub" {
  source     = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/pubsub?ref=daily-2023.11.11"
  project_id = module.project.project_id
  name       = "cloud-run-jobs"
  iam = {
    "roles/pubsub.publisher" = [module.job-service-account.iam_email]
  }
}

resource "google_cloud_run_v2_job" "default" {
  name     = "cloud-run-job-example"
  project  = module.project.project_id
  location = var.region

  template {
    template {
      service_account = module.job-service-account.email
      containers {
        image = var.job_container
        env {
          name  = "PUBSUB_TOPIC"
          value = module.pubsub.id
        }
      }
    }
  }

  lifecycle {
    ignore_changes = [
      launch_stage,
    ]
  }
}

resource "random_id" "random" {
  byte_length = 6
}

module "pubsub2inbox" {
  source = "../.."

  project_id = module.project.project_id
  region     = var.region

  function_name      = "cloud-run-logs"
  function_roles     = ["cloud-run-ro", "logging-ro"]
  cloud_functions_v2 = true

  service_account = "cloud-run-logs"
  pubsub_topic    = module.pubsub.id

  config = templatefile("${path.module}/cloud-run-jobs.yaml.tpl", {
    sender             = var.sender
    recipient          = var.recipient
    username           = var.username
    password           = var.password
    sendgrid_api_token = var.sendgrid_api_token
    region             = var.region
    project_id         = module.project.project_id
  })
  use_local_files  = true
  local_files_path = "../.."

  bucket_name     = format("cloud-run-lgos-source-%s", random_id.random.hex)
  bucket_location = var.region
}


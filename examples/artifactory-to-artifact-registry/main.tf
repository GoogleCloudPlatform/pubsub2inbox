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

module "project" {
  source         = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/project?ref=daily-2023.11.11"
  name           = var.project_id
  project_create = false
  services = [
    "compute.googleapis.com",
    "cloudfunctions.googleapis.com",
    "run.googleapis.com",
    "pubsub.googleapis.com",
    "vpcaccess.googleapis.com",
  ]
}

# Create the Pub/Sub topic
module "pubsub" {
  source     = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/pubsub?ref=daily-2023.11.11"
  project_id = module.project.project_id
  name       = "artifactory-to-ar"
  iam        = {}
}

resource "random_id" "random" {
  byte_length = 6
}

# Create Serverless VPC Connector to access 
resource "google_vpc_access_connector" "connector" {
  name          = "ar-vpc-connector"
  region        = var.region
  project       = var.vpc_config.network_project == null ? module.project.project_id : var.vpc_config.network_project
  ip_cidr_range = var.vpc_config.cidr
  network       = var.vpc_config.network
}

# Make sure the Service Agent has access to the Serverless VPC Connector
resource "google_project_iam_member" "connector-iam" {
  count   = var.vpc_config.network_project != null ? 1 : 0
  project = var.vpc_config.network_project
  role    = "roles/vpcaccess.user"
  member  = format("serviceAccount:service-%d@gcp-sa-vpcaccess.iam.gserviceaccount.com", module.project.number)
}

resource "google_project_iam_member" "cloud-run-iam" {
  count   = var.vpc_config.network_project != null ? 1 : 0
  project = var.vpc_config.network_project
  role    = "roles/vpcaccess.user"
  member  = format("serviceAccount:service-%d@serverless-robot-prod.iam.gserviceaccount.com", module.project.number)
}

# Create target Artifact Registry
resource "google_artifact_registry_repository" "repository" {
  project       = module.project.project_id
  location      = var.region
  repository_id = "pubsub2inbox"
  description   = "Target Artifact Registry from Artifactory artifacts"
  format        = "DOCKER"
  docker_config {
    immutable_tags = false
  }
}

# Grant the function permissions to write and delete in Artifact Registry
resource "google_artifact_registry_repository_iam_member" "repository-iam" {
  project    = google_artifact_registry_repository.repository.project
  location   = google_artifact_registry_repository.repository.location
  repository = google_artifact_registry_repository.repository.name
  role       = "roles/artifactregistry.repoAdmin"
  member     = format("serviceAccount:%s", module.pubsub2inbox.service_account)
}

# Deploy the Cloud Function
module "pubsub2inbox" {
  source = "../.."

  project_id = module.project.project_id
  region     = var.region

  function_name      = "artifactory-to-artifact-registry"
  function_roles     = []
  cloud_functions_v2 = true

  available_memory_mb = 2048 # Container contents have to be kept in memory, so the function might need a lot of memory
  available_cpu       = 2
  vpc_connector       = google_vpc_access_connector.connector.id

  service_account = "artifactory-to-ar"
  pubsub_topic    = module.pubsub.id

  config = templatefile("${path.module}/artifactory-to-ar.yaml.tpl", {
    project_id    = module.project.project_id
    username      = var.artifactory_username
    password      = var.artifactory_password
    ar_hostname   = format("https://%s-docker.pkg.dev", var.region)
    ar_repository = google_artifact_registry_repository.repository.repository_id
  })
  use_local_files  = true
  local_files_path = "../.."

  bucket_name     = format("artifactory-to-ar-%s", random_id.random.hex)
  bucket_location = var.region

  deploy_json2pubsub = {
    enabled = true
    suffix  = "-json2pubsub"
    control_cel = format(<<-EOT
      'x-jfrog-event-auth' in request.headers && 
      request.headers['x-jfrog-event-auth'] == '%s'
    EOT
    , var.artifactory_webhook_secret)
    message_cel     = "request.json"
    response_cel    = "'OK'"
    public_access   = true
    container_image = null
    min_instances   = 0
    max_instances   = 10
    grant_sa_user   = null
  }

  depends_on = [
    google_project_iam_member.connector-iam,
    google_project_iam_member.cloud-run-iam
  ]
}


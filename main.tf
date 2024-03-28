#   Copyright 2022 Google LLC
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
  required_version = ">= 1.0.0"

  required_providers {
    google  = ">= 5.0.0"
    archive = ">= 2.2.0"
    http = {
      source  = "hashicorp/http"
      version = ">= 3.2.1"
    }
    local = {
      source  = "hashicorp/local"
      version = ">= 2.2.3"
    }
  }
}

data "google_project" "project" {
  project_id = var.project_id
}

# Secret Manager secret for the function
resource "google_secret_manager_secret" "config-secret" {
  project = var.project_id

  secret_id = var.secret_id != "" ? var.secret_id : var.function_name

  replication {
    auto {}
  }

  depends_on = [
    google_project_service.secret-manager-api
  ]
}

# Secret version for the function config
resource "google_secret_manager_secret_version" "config-secret-version" {
  secret = google_secret_manager_secret.config-secret.id

  secret_data = var.config != null ? var.config : file(var.config_file)
}

# Service account for running the function
resource "google_service_account" "service-account" {
  count   = var.create_service_account ? 1 : 0
  project = var.project_id

  account_id   = var.service_account != "" ? var.service_account : var.function_name
  display_name = format("%s Service Account", title(var.service_account))
}

locals {
  # If you specify function_roles, the Terraform code will grant the service account some
  # privileges required for the particular functionalities.

  default_apis = [var.cloud_run ? "run.googleapis.com" : "cloudfunctions.googleapis.com", "cloudbuild.googleapis.com"]

  iam_permissions = {
    scc = {
      org     = ["roles/browser"]
      project = []
      apis    = ["cloudresourcemanager.googleapis.com"]
    }
    scc_writer = {
      org     = ["roles/browser", "roles/securitycenter.findingsEditor", "roles/securitycenter.findingSecurityMarksWriter", "roles/compute.networkViewer"]
      project = []
      apis    = ["cloudresourcemanager.googleapis.com"]
    }
    budgets = {
      org     = ["roles/browser", "roles/billing.viewer"]
      project = []
      apis    = ["cloudresourcemanager.googleapis.com"]
    }
    bigquery_reader = {
      org     = []
      project = ["roles/bigquery.dataViewer", "roles/bigquery.jobUser"]
      apis    = ["bigquery.googleapis.com"]
    }
    bigquery_writer = {
      org     = []
      project = ["roles/bigquery.dataEditor", "roles/bigquery.jobUser"]
      apis    = ["bigquery.googleapis.com"]
    }
    recommender = {
      org     = [/*"roles/recommender.bigQueryCapacityCommitmentsBillingAccountViewer", "roles/recommender.bigQueryCapacityCommitmentsProjectViewer",*/ "roles/recommender.bigQueryCapacityCommitmentsViewer", "roles/recommender.billingAccountCudViewer", "roles/recommender.cloudAssetInsightsViewer", "roles/recommender.cloudsqlViewer", "roles/recommender.computeViewer", "roles/recommender.firewallViewer", "roles/recommender.iamViewer", "roles/recommender.productSuggestionViewer", "roles/recommender.projectCudViewer", "roles/recommender.projectUtilViewer"]
      project = ["roles/compute.viewer"]
      apis    = ["cloudresourcemanager.googleapis.com", "recommender.googleapis.com"]
    }
    monitoring = {
      org     = []
      project = ["roles/monitoring.viewer"]
      apis    = ["cloudresourcemanager.googleapis.com"]
    }
    cai = {
      org     = []
      project = ["roles/cloudasset.viewer"]
      apis    = ["cloudasset.googleapis.com"]
    }
    transcoder = {
      org     = []
      project = ["roles/transcoder.admin"]
      apis    = ["transcoder.googleapis.com"]
    }
    cloud-deploy = {
      org     = []
      project = ["roles/clouddeploy.operator", "roles/clouddeploy.approver"]
      apis    = ["clouddeploy.googleapis.com"]
    }
    cloud-deploy-ro = {
      org     = []
      project = ["roles/clouddeploy.viewer"]
      apis    = ["clouddeploy.googleapis.com"]
    }
    vertexai-user = {
      org     = []
      project = ["roles/aiplatform.user"]
      apis    = ["aiplatform.googleapis.com"]
    }
    vertexai-search = {
      org     = []
      project = ["roles/discoveryengine.viewer"]
      apis    = ["discoveryengine.googleapis.com"]
    }
    compute-engine = {
      org     = []
      project = ["roles/compute.instanceAdmin.v1", "roles/compute.loadBalancerAdmin"]
      apis    = ["compute.googleapis.com"]
    }
    cloud-run-ro = {
      org     = []
      project = ["roles/run.viewer"]
      apis    = ["run.googleapis.com"]
    }
    logging-ro = {
      org     = []
      project = ["roles/logging.viewer"]
      apis    = ["logging.googleapis.com"]
    }
  }
  org_permissions     = flatten([for role in var.function_roles : local.iam_permissions[role].org])
  project_permissions = flatten([for role in var.function_roles : local.iam_permissions[role].project])
  _apis               = flatten([for role in var.function_roles : local.iam_permissions[role].apis])
  apis                = var.cloud_run || var.cloud_functions_v2 ? concat(local._apis, ["eventarc.googleapis.com"]) : local._apis
}

# Activate the necessary APIs in the project where the function is running
# (for API quota etc)
resource "google_project_service" "service-account-apis" {
  for_each = toset(concat(local.default_apis, local.apis))
  project  = var.project_id
  service  = each.value

  disable_on_destroy = false
}

# Activate the Secrets Manager API
resource "google_project_service" "secret-manager-api" {
  project            = var.project_id
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

# Add necessary project permissions to the service account in the project
resource "google_project_iam_member" "service-account-project" {
  for_each = var.create_service_account ? toset(concat(["roles/serviceusage.serviceUsageConsumer"], local.project_permissions)) : toset([])
  project  = var.project_id
  role     = each.value
  member   = format("serviceAccount:%s", google_service_account.service-account[0].email)
}

resource "google_project_iam_member" "existing-service-account-project" {
  for_each = !var.create_service_account ? toset(concat(["roles/serviceusage.serviceUsageConsumer"], local.project_permissions)) : toset([])
  project  = var.project_id
  role     = each.value
  member   = format("serviceAccount:%s", var.service_account)
}

# Add necessary project permissions to the service account in the organization
resource "google_organization_iam_member" "service-account-org" {
  for_each = var.create_service_account ? toset(local.org_permissions) : toset([])
  org_id   = var.organization_id
  role     = each.value
  member   = format("serviceAccount:%s", google_service_account.service-account[0].email)
}

# If a helper bucket is specified, grant the service account permissions to it
resource "google_storage_bucket_iam_member" "service-account-bucket" {
  for_each = toset(var.create_service_account && var.helper_bucket_name != "" ? ["roles/storage.objectAdmin"] : [])
  bucket   = var.helper_bucket_name
  role     = each.value
  member   = format("serviceAccount:%s", google_service_account.service-account[0].email)
}

resource "google_storage_bucket_iam_member" "existing-service-account-bucket" {
  for_each = toset(!var.create_service_account && var.helper_bucket_name != "" ? ["roles/storage.objectAdmin"] : [])
  bucket   = var.helper_bucket_name
  role     = each.value
  member   = format("serviceAccount:%s", var.service_account)
}

data "google_service_account" "existing-service-account" {
  count      = !var.create_service_account && var.grant_token_creator ? 1 : 0
  account_id = var.service_account
}

# Allow the service account to create differently scoped tokens
resource "google_service_account_iam_member" "service-account-actas-self" {
  count              = var.grant_token_creator ? 1 : 0
  service_account_id = var.create_service_account ? google_service_account.service-account[0].name : data.google_service_account.existing-service-account[0].name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = format("serviceAccount:%s", var.create_service_account ? google_service_account.service-account[0].email : data.google_service_account.existing-service-account[0].email)
}

# Allow the service account to access the configuration from the secret
resource "google_secret_manager_secret_iam_member" "config-secret-iam" {
  count   = var.create_service_account ? 1 : 0
  project = var.project_id

  secret_id = google_secret_manager_secret.config-secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = format("serviceAccount:%s", google_service_account.service-account[0].email)
}

resource "google_secret_manager_secret_iam_member" "existing-config-secret-iam" {
  count   = !var.create_service_account ? 1 : 0
  project = var.project_id

  secret_id = google_secret_manager_secret.config-secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = format("serviceAccount:%s", var.service_account)
}

## Cloud Function

resource "random_id" "bucket-suffix" {
  count = !var.cloud_run ? 1 : 0

  byte_length = 8
}

# Bucket for storing the function archive
resource "google_storage_bucket" "function-bucket" {
  count = !var.cloud_run ? 1 : 0

  project = var.project_id

  name                        = format("%s-%s", var.bucket_name, random_id.bucket-suffix[0].hex)
  location                    = var.bucket_location
  uniform_bucket_level_access = true
  force_destroy               = true
}

locals {
  function_files       = ["main.py", "requirements.txt", "filters/*.py", "output/*.py", "processors/*.py", "helpers/*.py", "_vendor/*.pyi", "_vendor/python_docker/*.py"]
  local_files_path     = var.local_files_path == null ? path.module : var.local_files_path
  all_function_files   = var.use_local_files ? setunion([for glob in local.function_files : fileset(local.local_files_path, glob)]...) : []
  function_file_hashes = [for file_path in local.all_function_files : filemd5(format("%s/%s", local.local_files_path, file_path))]

  json2pubsub_files          = ["cmd/json2pubsub/*.go", "cmd/json2pubsub/go.*"]
  json2pubsub_function_files = var.use_local_files ? setunion([for glob in local.json2pubsub_files : fileset(local.local_files_path, glob)]...) : []
  json2pubsub_file_hashes    = [for file_path in local.all_function_files : filemd5(format("%s/%s", local.local_files_path, file_path))]
}

data "archive_file" "function-zip" {
  count = !var.cloud_run && var.use_local_files ? 1 : 0

  type        = "zip"
  output_path = "${path.module}/index.zip"
  dynamic "source" {
    for_each = local.all_function_files
    content {
      content  = file(format("%s/%s", path.module, source.value))
      filename = source.value
    }
  }
}

data "archive_file" "json2pubsub-function-zip" {
  count = var.deploy_json2pubsub.enabled && var.use_local_files ? 1 : 0

  type        = "zip"
  output_path = "${path.module}/json2pubsub.zip"
  dynamic "source" {
    for_each = local.json2pubsub_function_files
    content {
      content  = file(format("%s/%s", path.module, source.value))
      filename = replace(source.value, "cmd/json2pubsub/", "")
    }
  }
}

resource "google_storage_bucket_object" "function-archive" {
  count = !var.cloud_run && var.use_local_files ? 1 : 0

  name   = format("index-%s.zip", md5(join(",", local.function_file_hashes)))
  bucket = google_storage_bucket.function-bucket[0].name
  source = var.use_local_files ? format("%s/index.zip", path.module) : null
  depends_on = [
    data.archive_file.function-zip.0
  ]
}

resource "google_storage_bucket_object" "json2pubsub-function-archive" {
  count = var.deploy_json2pubsub.enabled && var.use_local_files ? 1 : 0

  name   = format("json2pubsub-%s.zip", md5(join(",", local.json2pubsub_file_hashes)))
  bucket = google_storage_bucket.function-bucket[0].name
  source = var.use_local_files ? format("%s/json2pubsub.zip", path.module) : null
  depends_on = [
    data.archive_file.json2pubsub-function-zip.0
  ]
}

data "http" "function-archive" {
  count  = !var.use_local_files ? 1 : 0
  url    = format("https://github.com/GoogleCloudPlatform/pubsub2inbox/releases/download/%s/pubsub2inbox-%s.zip.b64", var.release_version, var.release_version)
  method = "GET"
}

resource "local_file" "function-archive" {
  count          = !var.use_local_files ? 1 : 0
  filename       = "index.zip"
  content_base64 = data.http.function-archive[0].response_body
}

resource "google_storage_bucket_object" "function-archive-release" {
  count = !var.cloud_run && !var.use_local_files ? 1 : 0

  name   = format("index-%s.zip", md5(data.http.function-archive[0].response_body))
  bucket = google_storage_bucket.function-bucket[0].name
  source = "index.zip"

  depends_on = [
    local_file.function-archive.0
  ]
}

# If you are getting error messages relating to iam.serviceAccount.actAs, see this bug:
# https://github.com/hashicorp/terraform-provider-google/issues/5889
#
# Workaround is to use "terraform taint google_cloudfunctions_function.function"
# before plan/apply.
resource "google_cloudfunctions_function" "function" {
  count = !var.cloud_run && !var.cloud_functions_v2 ? 1 : 0

  project = var.project_id
  region  = var.region

  name        = var.function_name
  description = "Pubsub2Inbox"
  runtime     = "python39"

  service_account_email = var.create_service_account ? google_service_account.service-account[0].email : var.service_account

  available_memory_mb   = var.available_memory_mb
  source_archive_bucket = google_storage_bucket.function-bucket[0].name
  source_archive_object = var.use_local_files ? google_storage_bucket_object.function-archive[0].name : google_storage_bucket_object.function-archive-release[0].name
  entry_point           = var.api == null ? "process_pubsub" : "process_api"
  timeout               = var.function_timeout

  vpc_connector = var.vpc_connector

  dynamic "event_trigger" {
    for_each = var.api == null || try(var.api.enabled, false) == false ? [""] : []
    content {
      event_type = "google.pubsub.topic.publish"
      resource   = var.pubsub_topic
      failure_policy {
        retry = true
      }
    }
  }

  min_instances = var.instance_limits.min_instances
  max_instances = var.instance_limits.max_instances

  environment_variables = merge({
    # You could also specify latest secret version here, in case you don't want to redeploy
    # and are fine with the function picking up the new config on subsequent runs.
    CONFIG          = google_secret_manager_secret_version.config-secret-version.name
    LOG_LEVEL       = var.log_level
    SERVICE_ACCOUNT = var.create_service_account ? google_service_account.service-account[0].email : var.service_account
  }, var.api != null && try(var.api.enabled, false) == true ? { WEBSERVER = "1" } : {})
}

resource "google_cloudfunctions2_function" "function" {
  count = !var.cloud_run && var.cloud_functions_v2 ? 1 : 0

  project = var.project_id

  name        = var.function_name
  location    = var.region
  description = "Pubsub2Inbox"

  build_config {
    runtime     = "python310"
    entry_point = var.api == null || try(var.api.enabled, false) == false ? "process_pubsub_v2" : "process_api_v2"
    source {
      storage_source {
        bucket = google_storage_bucket.function-bucket[0].name
        object = var.use_local_files ? google_storage_bucket_object.function-archive[0].name : google_storage_bucket_object.function-archive-release[0].name
      }
    }
  }

  service_config {
    service_account_email            = var.create_service_account ? google_service_account.service-account[0].email : var.service_account
    max_instance_count               = var.instance_limits.max_instances
    max_instance_request_concurrency = 1
    available_memory                 = format("%dM", var.available_memory_mb)
    available_cpu                    = var.available_cpu != null ? var.available_cpu : "0.333"
    timeout_seconds                  = var.function_timeout
    vpc_connector                    = var.vpc_connector
    environment_variables = {
      CONFIG          = google_secret_manager_secret_version.config-secret-version.name
      LOG_LEVEL       = var.log_level
      SERVICE_ACCOUNT = var.create_service_account ? google_service_account.service-account[0].email : var.service_account
    }
  }

  dynamic "event_trigger" {
    for_each = var.api == null || try(var.api.enabled, false) == false ? [""] : []
    content {
      trigger_region = var.trigger_region != null ? var.trigger_region : var.region
      event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
      pubsub_topic   = var.pubsub_topic
      retry_policy   = "RETRY_POLICY_RETRY"
    }
  }
}

## Cloud Run

# Service account for Pub/Sub invoker
resource "google_service_account" "invoker-service-account" {
  count   = var.cloud_run ? 1 : 0
  project = var.project_id

  account_id   = var.service_account != "" ? format("%s-invoker", var.service_account) : format("%s-invoker", var.function_name)
  display_name = format("%s Cloud Run invoker Service Account", title(var.function_name))
}

# Allow the invoker service account to run the Cloud Run function
resource "google_cloud_run_service_iam_member" "pubsub-invoker" {
  count   = var.cloud_run && (var.api == null || try(var.api.enabled, false) == false) ? 1 : 0
  project = var.project_id

  location = google_cloud_run_service.function[0].location
  service  = google_cloud_run_service.function[0].name
  role     = "roles/run.invoker"
  member   = format("serviceAccount:%s", google_service_account.invoker-service-account[0].email)
}

resource "google_cloud_run_service_iam_member" "pubsub-api-invokers" {
  for_each = toset(var.api != null && try(var.api.enabled, false) == true ? var.api.iam_invokers : [])
  project  = var.project_id

  location = google_cloud_run_service.function[0].location
  service  = google_cloud_run_service.function[0].name
  role     = "roles/run.invoker"
  member   = each.value
}

# Grant Pub/Sub P4SA to create auth tokens for the invoker service account
resource "google_service_account_iam_member" "pubsub-token-creator" {
  count = var.cloud_run ? 1 : 0

  service_account_id = google_service_account.invoker-service-account[0].name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = format("serviceAccount:service-%d@gcp-sa-pubsub.iam.gserviceaccount.com", data.google_project.project.number)
}

# Create a Pub/Sub push subscription that calls the Cloud Run function
resource "google_pubsub_subscription" "pubsub-subscription" {
  count   = var.cloud_run && (var.api == null || try(var.api.enabled, false) == false) ? 1 : 0
  project = var.project_id

  name  = format("%s-subscription", var.function_name)
  topic = var.pubsub_topic
  push_config {
    push_endpoint = google_cloud_run_service.function[0].status[0].url
    oidc_token {
      service_account_email = google_service_account.invoker-service-account[0].email
    }
    attributes = {
      x-goog-version = "v1"
    }
  }
  retry_policy {
    minimum_backoff = var.retry_minimum_backoff
    maximum_backoff = var.retry_maximum_backoff
  }
  depends_on = [
    google_service_account_iam_member.pubsub-token-creator[0],
    google_cloud_run_service_iam_member.pubsub-invoker[0]
  ]
}

resource "google_cloud_run_service" "function" {
  count   = var.cloud_run ? 1 : 0
  project = var.project_id

  name     = var.function_name
  location = var.region

  template {
    spec {
      containers {
        image = var.cloud_run_container

        env {
          name  = "CONFIG"
          value = google_secret_manager_secret_version.config-secret-version.name
        }
        env {
          name  = "LOG_LEVEL"
          value = var.log_level
        }
        env {
          name  = "SERVICE_ACCOUNT"
          value = var.create_service_account ? google_service_account.service-account[0].email : var.service_account
        }
        dynamic "env" {
          for_each = var.api != null && try(var.api.enabled, false) == true ? [""] : []
          content {
            name  = "WEBSERVER"
            value = "1"
          }
        }
        resources {
          limits = {
            memory = format("%dMi", var.available_memory_mb)
            cpu    = var.available_cpu != null ? var.available_cpu : 1
          }
        }
      }
      service_account_name  = var.create_service_account ? google_service_account.service-account[0].email : var.service_account
      container_concurrency = var.container_concurrency
      timeout_seconds       = var.function_timeout
    }
    metadata {
      annotations = merge({
        "autoscaling.knative.dev/minScale" = var.instance_limits.min_instances
        "autoscaling.knative.dev/maxScale" = var.instance_limits.max_instances
        }, var.cloudsql_connection != null ? {
        "run.googleapis.com/cloudsql-instances" = var.cloudsql_connection
        } : {}, var.vpc_connector != null ? {
        "run.googleapis.com/vpc-access-connector" = var.vpc_connector
        } : {}, var.vpc_egress != null ? {
        "run.googleapis.com/vpc-access-egress"  = var.vpc_egress.egress,
        "run.googleapis.com/network-interfaces" = jsonencode([{ network = var.vpc_egress.network, subnetwork = var.vpc_egress.subnetwork, tags = var.vpc_egress.tags }])
        } : {}
      )
    }
  }
  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Json2Pubsub resources
locals {
  json2pubsub_sa = (
    var.create_service_account ?
    format("%s%s", (var.service_account != "" ? var.service_account : var.function_name), var.deploy_json2pubsub.suffix) :
    format("%s%s", element(split("@", var.service_account), 0), var.deploy_json2pubsub.suffix)
  )
}

resource "google_service_account" "json2pubsub-service-account" {
  count   = var.deploy_json2pubsub.enabled ? 1 : 0
  project = var.project_id

  account_id   = local.json2pubsub_sa
  display_name = format("%s Json2Pubsub Service Account", title(local.json2pubsub_sa))
}

resource "google_service_account_iam_member" "json2pubsub-service-account-user" {
  count              = var.deploy_json2pubsub.enabled && var.deploy_json2pubsub.grant_sa_user != null ? 1 : 0
  service_account_id = google_service_account.json2pubsub-service-account[0].name
  role               = "roles/iam.serviceAccountUser"
  member             = format("serviceAccount:%s", var.deploy_json2pubsub.grant_sa_user)
}

resource "google_secret_manager_secret" "json2pubsub-message-cel" {
  count   = var.deploy_json2pubsub.enabled ? 1 : 0
  project = var.project_id

  secret_id = format("%s%s-message", var.secret_id != "" ? var.secret_id : var.function_name, var.deploy_json2pubsub.suffix)

  replication {
    auto {}
  }

  depends_on = [
    google_project_service.secret-manager-api
  ]
}

resource "google_secret_manager_secret_version" "json2pubsub-message-cel" {
  count  = var.deploy_json2pubsub.enabled ? 1 : 0
  secret = google_secret_manager_secret.json2pubsub-message-cel[0].id

  secret_data = var.deploy_json2pubsub.message_cel
}

resource "google_secret_manager_secret" "json2pubsub-control-cel" {
  count   = var.deploy_json2pubsub.enabled ? 1 : 0
  project = var.project_id

  secret_id = format("%s%s-control", var.secret_id != "" ? var.secret_id : var.function_name, var.deploy_json2pubsub.suffix)

  replication {
    auto {}
  }

  depends_on = [
    google_project_service.secret-manager-api
  ]
}

resource "google_secret_manager_secret_version" "json2pubsub-control-cel" {
  count  = var.deploy_json2pubsub.enabled ? 1 : 0
  secret = google_secret_manager_secret.json2pubsub-control-cel[0].id

  secret_data = var.deploy_json2pubsub.control_cel
}

resource "google_secret_manager_secret" "json2pubsub-response-cel" {
  count   = var.deploy_json2pubsub.enabled ? 1 : 0
  project = var.project_id

  secret_id = format("%s%s-response", var.secret_id != "" ? var.secret_id : var.function_name, var.deploy_json2pubsub.suffix)

  replication {
    auto {}
  }

  depends_on = [
    google_project_service.secret-manager-api
  ]
}

resource "google_secret_manager_secret_version" "json2pubsub-response-cel" {
  count  = var.deploy_json2pubsub.enabled ? 1 : 0
  secret = google_secret_manager_secret.json2pubsub-response-cel[0].id

  secret_data = var.deploy_json2pubsub.response_cel
}

resource "google_secret_manager_secret_iam_member" "json2pubsub-message-cel" {
  count   = var.deploy_json2pubsub.enabled ? 1 : 0
  project = var.project_id

  secret_id = google_secret_manager_secret.json2pubsub-message-cel[0].secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = format("serviceAccount:%s", google_service_account.json2pubsub-service-account[0].email)
}

resource "google_secret_manager_secret_iam_member" "json2pubsub-control-cel" {
  count   = var.deploy_json2pubsub.enabled ? 1 : 0
  project = var.project_id

  secret_id = google_secret_manager_secret.json2pubsub-control-cel[0].secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = format("serviceAccount:%s", google_service_account.json2pubsub-service-account[0].email)
}

resource "google_secret_manager_secret_iam_member" "json2pubsub-response-cel" {
  count   = var.deploy_json2pubsub.enabled ? 1 : 0
  project = var.project_id

  secret_id = google_secret_manager_secret.json2pubsub-response-cel[0].secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = format("serviceAccount:%s", google_service_account.json2pubsub-service-account[0].email)
}

resource "google_pubsub_topic_iam_member" "json2pubsub-publisher" {
  count   = var.deploy_json2pubsub.enabled ? 1 : 0
  project = var.project_id

  topic  = var.pubsub_topic
  role   = "roles/pubsub.publisher"
  member = format("serviceAccount:%s", google_service_account.json2pubsub-service-account[0].email)
}

resource "google_cloud_run_service" "json2pubsub-function" {
  count   = var.deploy_json2pubsub.enabled && var.cloud_run ? 1 : 0
  project = var.project_id

  name     = format("%s%s", var.function_name, var.deploy_json2pubsub.suffix)
  location = var.region

  template {
    spec {
      containers {
        image = var.deploy_json2pubsub.container_image

        env {
          name  = "MESSAGE_CEL"
          value = format("gsm:%s", google_secret_manager_secret_version.json2pubsub-message-cel[0].name)
        }
        env {
          name  = "CONTROL_CEL"
          value = format("gsm:%s", google_secret_manager_secret_version.json2pubsub-control-cel[0].name)
        }
        env {
          name  = "RESPONSE_CEL"
          value = format("gsm:%s", google_secret_manager_secret_version.json2pubsub-response-cel[0].name)
        }
        env {
          name  = "PUBSUB_TOPIC"
          value = basename(var.pubsub_topic)
        }
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }
      }
      service_account_name  = google_service_account.json2pubsub-service-account[0].email
      container_concurrency = 1
      timeout_seconds       = var.function_timeout
    }
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = var.deploy_json2pubsub.min_instances
        "autoscaling.knative.dev/maxScale" = var.deploy_json2pubsub.max_instances
      }
    }
  }
  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_service_account_iam_member.json2pubsub-service-account-user
  ]
}

resource "google_cloud_run_service_iam_member" "json2pubsub-public-access" {
  count   = var.deploy_json2pubsub.enabled && var.cloud_run && var.deploy_json2pubsub.public_access ? 1 : 0
  project = var.project_id

  location = google_cloud_run_service.json2pubsub-function[0].location
  service  = google_cloud_run_service.json2pubsub-function[0].name
  role     = "roles/cloudfunctions.invoker"
  member   = "allUsers"
}

resource "google_cloudfunctions2_function" "json2pubsub-function" {
  count = var.deploy_json2pubsub.enabled && !var.cloud_run && var.cloud_functions_v2 ? 1 : 0

  project = var.project_id

  name        = format("%s%s", var.function_name, var.deploy_json2pubsub.suffix)
  location    = var.region
  description = "Json2Pubsub"

  build_config {
    runtime     = "go120"
    entry_point = "Json2Pubsub"
    source {
      storage_source {
        bucket = google_storage_bucket.function-bucket[0].name
        object = var.use_local_files ? google_storage_bucket_object.json2pubsub-function-archive[0].name : null
      }
    }
  }

  service_config {
    service_account_email            = google_service_account.json2pubsub-service-account[0].email
    max_instance_count               = var.deploy_json2pubsub.max_instances
    available_memory                 = "256M"
    timeout_seconds                  = var.function_timeout
    max_instance_request_concurrency = 1
    environment_variables = {
      GOOGLE_CLOUD_PROJECT = var.project_id
      PUBSUB_TOPIC         = basename(var.pubsub_topic)
      MESSAGE_CEL          = format("gsm:%s", google_secret_manager_secret_version.json2pubsub-message-cel[0].name)
      CONTROL_CEL          = format("gsm:%s", google_secret_manager_secret_version.json2pubsub-control-cel[0].name)
      RESPONSE_CEL         = format("gsm:%s", google_secret_manager_secret_version.json2pubsub-response-cel[0].name)
    }
  }

  depends_on = [
    google_service_account_iam_member.json2pubsub-service-account-user
  ]
}

resource "google_cloud_run_service_iam_member" "json2pubsub-public-access-v2" {
  count   = var.deploy_json2pubsub.enabled && !var.cloud_run && var.cloud_functions_v2 && var.deploy_json2pubsub.public_access ? 1 : 0
  project = var.project_id

  location = google_cloudfunctions2_function.json2pubsub-function[0].location
  service  = google_cloudfunctions2_function.json2pubsub-function[0].service_config[0].service
  role     = "roles/run.invoker"
  member   = "allUsers"
}

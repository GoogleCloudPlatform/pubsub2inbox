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

output "service_account" {
  value = var.create_service_account ? google_service_account.service-account[0].email : var.service_account
}

output "service_account_name" {
  value = var.create_service_account ? google_service_account.service-account[0].name : null
}

output "name" {
  value = var.function_name
}

output "region" {
  value = var.region
}

output "project_id" {
  value = var.project_id
}

output "secret" {
  value     = google_secret_manager_secret.config-secret
  sensitive = true
}

output "bucket" {
  value = !var.cloud_run ? google_storage_bucket.function-bucket : null
}

output "json2pubsub_url" {
  value = var.deploy_json2pubsub.enabled ? (
    var.cloud_functions_v2 ?
    google_cloudfunctions2_function.json2pubsub-function[0].service_config[0].uri :
    google_cloud_run_service.json2pubsub-function[0].status[0].url
  ) : null
}
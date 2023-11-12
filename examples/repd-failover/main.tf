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

locals {
  disk_name = "repd-failover-data-disk"
}

module "project" {
  source         = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/project?ref=daily-2023.11.11"
  name           = var.project_id
  project_create = false
  services = [
    "compute.googleapis.com",
    "cloudfunctions.googleapis.com",
    "run.googleapis.com",
  ]
  logging_sinks = {
    repd-failover-healthcheck = {
      destination = module.pubsub.id
      filter      = <<-EOT
        logName="projects/${var.project_id}/logs/compute.googleapis.com%2Fhealthchecks" AND
        jsonPayload.healthCheckProbeResult.healthState="UNHEALTHY" AND
        resource.type="gce_instance_group" AND
        resource.labels.instance_group_name:"repd-failover"
      EOT
      type        = "pubsub"
    }
  }
}

resource "google_project_service" "pubsub" {
  project = var.project_id
  service = "pubsub.googleapis.com"

  timeouts {
    create = "30m"
    update = "40m"
  }

  disable_dependent_services = true
  disable_on_destroy         = false
}

module "vpc" {
  source     = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/net-vpc?ref=daily-2023.11.11"
  project_id = module.project.project_id
  name       = var.vpc_config.network
  subnets = [
    {
      ip_cidr_range = var.vpc_config.subnetwork_cidr
      name          = var.vpc_config.subnetwork
      region        = var.region
    },
  ]
  vpc_create = var.vpc_config.vpc_create
}

module "firewall" {
  source     = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/net-vpc-firewall?ref=daily-2023.11.11"
  project_id = module.project.project_id
  network    = module.vpc.name
  default_rules_config = {
    disabled = true
  }
  ingress_rules = {
    allow-ingress-http = {
      description   = "Allow ingress to HTTP"
      source_ranges = ["0.0.0.0/0"]
      targets       = ["repd-failover"]
      rules         = [{ protocol = "tcp", ports = [80] }]
    }
    allow-ingress-iap-ssh = {
      description   = "Allow ingress to SSH from Identity-Aware Proxy"
      source_ranges = ["35.235.240.0/20"]
      targets       = ["repd-failover"]
      rules         = [{ protocol = "tcp", ports = [22] }]
    }
    allow-ingress-healthcheck = {
      description   = "Allow ingress from health check to HTTP port"
      source_ranges = ["35.191.0.0/16", "209.85.152.0/22", "209.85.204.0/22", "130.211.0.0/22"]
      targets       = ["repd-failover"]
      rules         = [{ protocol = "tcp", ports = [80] }]
    }
  }
}

module "nat" {
  source         = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/net-cloudnat?ref=daily-2023.11.11"
  project_id     = module.project.project_id
  region         = var.region
  name           = "repd-failover-nat"
  router_network = module.vpc.name
}

resource "google_compute_region_disk" "data-disk" {
  project                   = module.project.project_id
  name                      = local.disk_name
  type                      = "pd-balanced"
  region                    = var.region
  size                      = 10
  physical_block_size_bytes = 4096

  replica_zones = [
    var.zones.primary,
    var.zones.secondary,
  ]
}

module "cos-nginx" {
  source = "./modules/nginx"
  runcmd_pre = [
    "if [ -e /dev/disk/by-id/google-${local.disk_name} ] && ! blkid /dev/disk/by-id/google-${local.disk_name} ; then mkfs -t ext4 -m 0 -F -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/disk/by-id/google-${local.disk_name} ; fi",
    "if [ ! -e /dev/disk/by-id/google-${local.disk_name} ] ; then poweroff ; else mkdir -p /mnt/disks/data ; mount /dev/disk/by-id/google-${local.disk_name} /mnt/disks/data ; fi",
    "if [ ! -e /mnt/disks/data/index.html ] ; then echo RePD failover example > /mnt/disks/data/index.html ; fi",
  ]
  image = "nginx:1.25"
  additional_mounts = {
    "/mnt/disks/data" = "/usr/share/nginx/html"
  }
}

module "primary-vm" {
  source     = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/compute-vm?ref=daily-2023.11.11"
  project_id = module.project.project_id
  zone       = var.zones.primary
  name       = "repd-failover-primary"
  boot_disk = {
    initialize_params = {
      image = "projects/cos-cloud/global/images/family/cos-stable"
      type  = "pd-ssd"
      size  = 10
    }
  }
  attached_disks = [{
    name        = google_compute_region_disk.data-disk.name
    size        = google_compute_region_disk.data-disk.size
    source_type = "attach"
    source      = google_compute_region_disk.data-disk.id
  }]
  network_interfaces = [{
    network    = module.vpc.self_link
    subnetwork = module.vpc.subnet_self_links[format("%s/%s", var.region, var.vpc_config.subnetwork)]
  }]
  tags = ["repd-failover"]
  metadata = {
    user-data              = module.cos-nginx.cloud_config
    google-logging-enabled = true
  }
  service_account = {
    auto_create = true
  }
}

module "secondary-vm" {
  source     = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/compute-vm?ref=daily-2023.11.11"
  project_id = module.project.project_id
  zone       = var.zones.secondary
  name       = "repd-failover-secondary"
  boot_disk = {
    initialize_params = {
      image = "projects/cos-cloud/global/images/family/cos-stable"
      type  = "pd-ssd"
      size  = 10
    }
  }
  attached_disks = []
  network_interfaces = [{
    network    = module.vpc.self_link
    subnetwork = module.vpc.subnet_self_links[format("%s/%s", var.region, var.vpc_config.subnetwork)]
  }]
  tags = ["repd-failover"]
  metadata = {
    user-data              = module.cos-nginx.cloud_config
    google-logging-enabled = true
  }
  service_account = {
    email = module.primary-vm.service_account_email
  }
}

resource "google_service_account_iam_member" "member" {
  service_account_id = module.primary-vm.service_account.name
  role               = "roles/iam.serviceAccountUser"
  member             = format("serviceAccount:%s", module.pubsub2inbox.service_account)
}

module "nlb" {
  source     = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/net-lb-ext?ref=daily-2023.11.11"
  project_id = module.project.project_id
  region     = var.region
  name       = "repd-failover"

  backend_service_config = {
    protocol  = "TCP"
    port_name = "http"
  }

  forwarding_rules_config = {
    "" = {
      ports = [80]
    }
  }

  group_configs = {
    umig-primary = {
      zone = module.primary-vm.instance.zone
      instances = [
        module.primary-vm.self_link
      ]
      named_ports = { "http" = 80 }
    }
    umig-secondary = {
      zone = module.secondary-vm.instance.zone
      instances = [
        module.secondary-vm.self_link
      ]
      named_ports = { "http" = 80 }
    }
  }

  backends = [{
    group = module.nlb.groups.umig-primary.self_link
  }]

  health_check_config = {
    enable_logging      = true
    check_interval_sec  = 5
    healthy_threshold   = 2
    timeout_sec         = 5
    unhealthy_threshold = 4
    http = {
      port = 80
    }
  }
}

resource "random_id" "random" {
  byte_length = 6
}

module "pubsub" {
  source     = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/pubsub?ref=daily-2023.11.11"
  project_id = var.project_id # Use var to avoid circular dependency
  name       = "repd-failover"
  iam = {
  }
  depends_on = [
    google_project_service.pubsub
  ]
}

module "lock-bucket" {
  source     = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/gcs?ref=daily-2023.11.11"
  project_id = module.project.project_id
  prefix     = "repd-failover"
  name       = format("lock-%s", random_id.random.hex)
  versioning = false
  labels     = {}
}

resource "google_storage_bucket_iam_member" "member" {
  bucket = module.lock-bucket.name
  role   = "roles/storage.objectAdmin"
  member = format("serviceAccount:%s", module.pubsub2inbox.service_account)
}

module "pubsub2inbox" {
  source = "../.."

  project_id = module.project.project_id
  region     = var.region

  function_name      = "repd-failover"
  function_roles     = ["compute-engine"]
  cloud_functions_v2 = true

  service_account = "repd-failover-pubsub2inbox"
  pubsub_topic    = module.pubsub.id

  config = templatefile("${path.module}/repd-failover.yaml.tpl", {
    concurrency_bucket = module.lock-bucket.name
    project            = module.project.project_id
    primary = {
      instance       = module.primary-vm.instance.name
      zone           = module.primary-vm.instance.zone
      instance_group = module.nlb.group_self_links["umig-primary"]
    }
    secondary = {
      instance       = module.secondary-vm.instance.name
      zone           = module.secondary-vm.instance.zone
      instance_group = module.nlb.group_self_links["umig-secondary"]
    }
    regional_disk = {
      id          = google_compute_region_disk.data-disk.id
      region      = var.region
      device_name = google_compute_region_disk.data-disk.name
    }
    load_balancer = {
      backend_service = module.nlb.backend_service.name
      region          = var.region
    }
  })
  use_local_files  = true
  local_files_path = "../.."

  bucket_name     = format("repd-failover-source-%s", random_id.random.hex)
  bucket_location = var.region
}


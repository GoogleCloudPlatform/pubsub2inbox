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

# Failover example using regional persistent disk.

globals:
  project: ${project}
  instances:
    primary: ${primary.instance}
    secondary: ${secondary.instance}
  zones:
    ${primary.instance}: ${primary.zone}
    ${secondary.instance}: ${secondary.zone}
  instance_groups:
    ${primary.instance}: ${primary.instance_group}
    ${secondary.instance}: ${secondary.instance_group}
  regional_disk:
    id: ${regional_disk.id}
    region: ${regional_disk.region}
    device_name: ${regional_disk.device_name}
  load_balancer:
    backend_service: ${load_balancer.backend_service}
    region: ${load_balancer.region}

concurrency:
  bucket: ${concurrency_bucket}
  period: "10 minutes" # If the function fails unexpectedly, wait at least 10 minutes until retrying
  defer: true # Allow Pub/Sub to retry the concurrency controlled messages

pipeline:
  - type: processor.genericjson
  - type: processor.computeengine
    output: primary
    config:
      mode: instances.get
      project: "{{ project }}"
      zone: "{{ zones[instances.primary] }}"
      instance: "{{ instances.primary }}"
  - type: processor.setvariable # Check which instance has the disk currently
    output: primary_instance
    config:
      value: |
        {% if primary.disks|selectattr("deviceName", "==", regional_disk.device_name)|list|length > 0 %}{{ instances.primary }}{% else %}{{ instances.secondary }}{% endif %}
  - type: processor.setvariable # Check which instance does not have the disk currently
    output: secondary_instance
    config:
      value: |
        {% if primary.disks|selectattr("deviceName", "==", regional_disk.device_name)|list|length > 0 %}{{ instances.secondary }}{% else %}{{ instances.primary }}{% endif %}
  - type: output.logger
    config:
      message: |
        Current primary instance: {{ primary_instance }} -- New primary instance: {{ secondary_instance }}
  - type: processor.computeengine # Make a snapshot of the disk before stopping the instance
    canFail: true
    config:
      mode: disks.snapshots.create
      project: "{{ project }}"
      region: "{{ regional_disk.region }}"
      storageLocations:
        - "{{ regional_disk.region }}"
      disk: "{{ regional_disk.self_link|split('/')|last }}"
      snapshotName: "{{ regional_disk.device_name }}-{{ ''|utc_strftime('%Y%m%d-%H%M%S') }}"
  - type: processor.computeengine # Only keep 3 last snapshots
    canFail: true
    config:
      mode: disks.snapshots.purge
      project: "{{ project }}"
      snapshotName: "^{{ regional_disk.device_name }}-"
      maxSnapshots: 3
  - type: processor.computeengine # Attempt to stop the instance (may not succeed in case of zonal outage)
    canFail: true
    config:
      mode: instances.stop
      timeout: 60
      project: "{{ project }}"
      zone: "{{ zones[primary_instance] }}"
      instance: "{{ primary_instance }}"
  - type: processor.computeengine # Attempt to politely detach the disk from the previous primary instance
    canFail: true
    config:
      mode: instances.detachdisk
      zone: "{{ zones[primary_instance] }}"
      project: "{{ project }}"
      instance: "{{ primary_instance }}"
      disk: "{{ regional_disk.id }}"
  - type: processor.computeengine # Forcibly attach the disk to the new primary instance
    config:
      mode: instances.attachdisk
      project: "{{ project }}"
      zone: "{{ zones[secondary_instance] }}"
      instance: "{{ secondary_instance }}"
      disk: "{{ regional_disk.id }}"
      deviceName: "{{ regional_disk.device_name }}"
      forceAttach: true
  - type: processor.computeengine # Start the new primary instance
    canFail: true
    config:
      mode: instances.start
      project: "{{ project }}"
      zone: "{{ zones[secondary_instance] }}"
      instance: "{{ secondary_instance }}"
  - type: processor.loadbalancing # Patch the backend service with the new unmanaged instance group
    config:
      mode: regionbackendservice.patch
      project: "{{ project }}"
      region: "{{ load_balancer.region }}"
      backendService: "{{ load_balancer.backend_service }}"
      patch:
        backends:
          - group: "{{ instance_groups[secondary_instance] }}"
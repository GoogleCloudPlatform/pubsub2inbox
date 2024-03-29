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
from .base import Processor, NotConfiguredException
import google.auth
from googleapiclient import discovery
import time
import re


class ComputeengineOperationFailed(Exception):
    pass


class ComputeengineProcessor(Processor):
    """
    Perform actions on Compute Engine instances.

    Args:
        project (str, optional): Google Cloud project ID.
        instance (str): Instance to operate on.
        disk (str, optional): Disk to operate on.
        deviceName (str, optional): Device name to operate on.
        snapshotName (str, optional): Snapshot name (or regexp for disks.instanceSnapshots) for instant snapshots.
        maxSnapshots (int, optional): Maximum snapshots for disks.instanceSnapshots.purge.
        storageLocations (list, optional): Storage locations for disk.snapshots.
        snapshotParameters (dict, optional): Additional snapshot configuration.
        labels (dict, optional): Labels for instant snapshots.
        region (str, optional): Google Cloud region.
        zone (str, optional): Google Cloud zone for the instance.
        mode (str): One of: instances.get, instances.stop, instances.reset, instances.start, 
          instances.detachDisk, instances.attachDisk, disks.instantSnapshots.create, disks.instantSnapshots.purge,
          disk.snapshots.create, disk.snapshots.purge
    """

    def get_default_config_key():
        return 'computeengine'

    def wait_for_operation_done(self,
                                compute_service,
                                operation_name,
                                operation_self_link,
                                project,
                                zone,
                                region,
                                timeout=30):
        end_time = start_time = time.monotonic()
        while True and (end_time - start_time) < timeout:
            if '/global/' in operation_self_link:
                op_request = compute_service.globalOperations().get(
                    project=project, operation=operation_name).execute()
            elif '/zones/' in operation_self_link:
                op_request = compute_service.zoneOperations().get(
                    project=project, zone=zone,
                    operation=operation_name).execute()
            else:
                op_request = compute_service.regionOperations().get(
                    project=project, region=region,
                    operation=operation_name).execute()
            if 'status' in op_request and op_request['status'] == 'DONE':
                if 'error' in op_request:
                    self.logger.error(
                        'Error while waiting for long running operation %s to complete.'
                        % (operation_name),
                        extra={'error': op_request['error']})
                    return op_request['error']
                return op_request
            time.sleep(5)
            end_time = time.monotonic()

    def get_instance(self, compute_service, project, zone, instance):
        get_request = compute_service.instances().get(project=project,
                                                      zone=zone,
                                                      instance=instance)
        get_response = get_request.execute()
        if 'id' in get_response:
            return get_response
        else:
            raise ComputeengineOperationFailed('Failed to get instance: %s' %
                                               str(get_response))

    def process(self, output_var='computeengine'):
        if 'mode' not in self.config:
            raise NotConfiguredException(
                'No Compute Engine operation specified.')
        if self.config['mode'].startswith('instances.'):
            if 'instance' not in self.config:
                raise NotConfiguredException(
                    'No instance specified in configuration.')
        if self.config['mode'].lower() in [
                'instances.attachdisk', 'instances.detachdisk'
        ]:
            if 'disk' not in self.config:
                raise NotConfiguredException(
                    'No disk specified in configuration.')

        credentials, credentials_project_id = google.auth.default()
        project = self._jinja_expand_string(
            self.config['project'],
            'project') if 'project' in self.config else credentials_project_id
        if not project:
            project = credentials.quota_project_id

        compute_service = discovery.build(
            'compute', 'v1', http=self._get_branded_http(credentials))

        timeout = self._jinja_expand_int(
            self.config['timeout']) if 'timeout' in self.config else 30
        zone = self._jinja_expand_string(
            self.config['zone']) if 'zone' in self.config else None
        region = self._jinja_expand_string(
            self.config['region']) if 'region' in self.config else None
        instance = self._jinja_expand_string(
            self.config['instance']) if 'instance' in self.config else None

        disk = self._jinja_expand_string(
            self.config['disk']) if 'disk' in self.config else None
        device_name = self._jinja_expand_string(
            self.config['deviceName']) if 'deviceName' in self.config else None
        if disk is not None:
            disk = disk.replace('https://www.googleapis.com/compute/v1/', '')

        if self.config['mode'] == 'instances.get':
            return {
                output_var:
                    self.get_instance(compute_service, project, zone, instance)
            }

        if self.config['mode'] == 'instances.stop':
            inst = self.get_instance(compute_service, project, zone, instance)
            if inst['status'] == 'RUNNING':
                self.logger.info('Stopping instance %s in zone %s' %
                                 (instance, zone))
                stop_request = compute_service.instances().stop(
                    project=project, zone=zone, instance=instance)
                stop_response = stop_request.execute()
                if 'id' in stop_response:
                    self.wait_for_operation_done(compute_service,
                                                 stop_response['id'],
                                                 stop_response['selfLink'],
                                                 project, zone, region, timeout)
                    return {
                        output_var:
                            self.get_instance(compute_service, project, zone,
                                              instance)
                    }
                else:
                    raise ComputeengineOperationFailed(
                        'Failed to stop instance: %s' % str(stop_response))
            return {output_var: inst}

        if self.config['mode'] == 'instances.reset':
            inst = self.get_instance(compute_service, project, zone, instance)
            self.logger.info('Resetting instance %s in zone %s' %
                             (instance, zone))
            reset_request = compute_service.instances().reset(project=project,
                                                              zone=zone,
                                                              instance=instance)
            reset_response = reset_request.execute()
            if 'id' in reset_response:
                self.wait_for_operation_done(compute_service,
                                             reset_response['id'],
                                             reset_response['selfLink'],
                                             project, zone, region, timeout)
                return {
                    output_var:
                        self.get_instance(compute_service, project, zone,
                                          instance)
                }
            else:
                raise ComputeengineOperationFailed(
                    'Failed to reset instance: %s' % str(reset_response))
            return {output_var: inst}

        if self.config['mode'] == 'instances.start':
            inst = self.get_instance(compute_service, project, zone, instance)
            if inst['status'] != 'RUNNING':
                self.logger.info('Starting instance %s in zone %s' %
                                 (instance, zone))
                start_request = compute_service.instances().start(
                    project=project, zone=zone, instance=instance)
                start_response = start_request.execute()
                if 'id' in start_response:
                    self.wait_for_operation_done(compute_service,
                                                 start_response['id'],
                                                 start_response['selfLink'],
                                                 project, zone, region, timeout)
                    return {
                        output_var:
                            self.get_instance(compute_service, project, zone,
                                              instance)
                    }
                else:
                    raise ComputeengineOperationFailed(
                        'Failed to start instance: %s' % str(start_response))
            return {output_var: inst}

        if self.config['mode'].lower() == 'instances.detachdisk':
            wait_for_stopped = self._jinja_expand_bool(
                self.config['waitForStopped']
            ) if 'waitForStopped' in self.config else True

            # Wait for instance to be stopped if required
            inst = self.get_instance(compute_service, project, zone, instance)
            count = 0
            while wait_for_stopped and True:
                if inst['status'] != 'TERMINATED':
                    time.sleep(2)
                    count += 2
                    if count > timeout:
                        raise ComputeengineOperationFailed(
                            'Instance did not stop in time: %s' % (inst))
                else:
                    break

            # Check if disk is already detached
            disk_is_detached = True
            if 'disks' in inst:
                for attached_disk in inst['disks']:
                    if attached_disk[
                            'deviceName'] == device_name or attached_disk[
                                'source'].replace(
                                    'https://www.googleapis.com/compute/v1/',
                                    '') == disk:
                        disk_is_detached = False
                        if device_name is None:
                            device_name = attached_disk['deviceName']
                        break

            if not disk_is_detached:
                self.logger.info(
                    'Detaching disk %s from instance %s (zone %s)' %
                    (disk if disk is not None else device_name, instance, zone))

                detach_request = compute_service.instances().detachDisk(
                    project=project,
                    zone=zone,
                    instance=instance,
                    deviceName=device_name)
                detach_response = detach_request.execute()
                if 'id' in detach_response:
                    self.wait_for_operation_done(compute_service,
                                                 detach_response['id'],
                                                 detach_response['selfLink'],
                                                 project, zone, region, timeout)
                    return {
                        output_var:
                            self.get_instance(compute_service, project, zone,
                                              instance)
                    }
                else:
                    raise ComputeengineOperationFailed(
                        'Failed to detach disk %s from %s: %s' %
                        (disk, instance, str(detach_response)))
            else:
                return {output_var: inst}

        if self.config['mode'] == 'instances.attachdisk':
            force_attach = self._jinja_expand_bool(
                self.config['forceAttach']
            ) if 'forceAttach' in self.config else False

            # Check if disk is already attached
            inst = self.get_instance(compute_service, project, zone, instance)
            disk_is_attached = False
            if 'disks' in inst:
                for attached_disk in inst['disks']:
                    if attached_disk[
                            'deviceName'] == device_name or attached_disk[
                                'source'].replace(
                                    'https://www.googleapis.com/compute/v1/',
                                    '') == disk:
                        disk_is_attached = True
                        break

            if not disk_is_attached:
                request_body = {
                    'type': 'PERSISTENT',
                    'mode': 'READ_WRITE',
                    'source': disk,
                    'deviceName': device_name,
                    'boot': False,
                    'forceAttach': force_attach,
                }
                if 'attachParameters' in self.config:
                    request_body = {
                        **request_body,
                        **self._jinja_expand_dict_all(
                            self.config['attachParameters'], 'attach_parameters')
                    }

                self.logger.info('Attaching disk %s to instance %s (zone %s)' %
                                 (disk, instance, zone))

                attach_request = compute_service.instances().attachDisk(
                    project=project,
                    zone=zone,
                    instance=instance,
                    forceAttach=force_attach,
                    body=request_body)
                attach_response = attach_request.execute()
                if 'id' in attach_response:
                    self.wait_for_operation_done(compute_service,
                                                 attach_response['id'],
                                                 attach_response['selfLink'],
                                                 project, zone, region, timeout)
                    return {
                        output_var:
                            self.get_instance(compute_service, project, zone,
                                              instance)
                    }
                else:
                    raise ComputeengineOperationFailed(
                        'Failed to attach disk %s to %s: %s' %
                        (disk, instance, str(attach_response)))

        if self.config['mode'].lower().startswith('disks.snapshots.'):
            if 'snapshotName' not in self.config:
                raise NotConfiguredException(
                    'No snapshotName in configuration!')

            snapshot_name = self._jinja_expand_string(
                self.config['snapshotName'], 'snapshot_name')

            if self.config['mode'].lower() == 'disks.snapshots.create':
                if 'storageLocations' not in self.config:
                    raise NotConfiguredException(
                        'No storageLocations in configuration!')
                storage_locations = self._jinja_expand_list(
                    self.config['storageLocations'], 'storage_locations')

                request_body = {
                    'name': snapshot_name,
                    'sourceDisk': disk,
                    'storageLocations': storage_locations,
                }
                if 'snapshotParameters' in self.config:
                    snapshot_parameters = self._jinja_expand_dict_all(
                        self.config['snapshotParameters'],
                        'snapshot_parameters')
                    request_body = {**request_body, **snapshot_parameters}

                if 'labels' in self.config:
                    request_body['labels'] = self._jinja_expand_dict_all(
                        self.config['labels'], 'labels')

                snapshot_request = None
                if region is not None:
                    self.logger.info(
                        'Creating snapshot %s of disk %s in %s...' %
                        (snapshot_name, disk, region))
                    snapshot_request = compute_service.regionDisks(
                    ).createSnapshot(project=project,
                                     region=region,
                                     disk=disk,
                                     body=request_body)
                else:
                    self.logger.info(
                        'Creating snapshot %s of disk %s in %s...' %
                        (snapshot_name, disk, zone))
                    snapshot_request = compute_service.disks().createSnapshot(
                        project=project,
                        zone=zone,
                        disk=disk,
                        body=request_body)
                snapshot_response = snapshot_request.execute()
                if 'id' in snapshot_response:
                    ret = self.wait_for_operation_done(
                        compute_service, snapshot_response['id'],
                        snapshot_response['selfLink'], project, zone, region,
                        timeout)
                    return {output_var: ret}
                else:
                    raise ComputeengineOperationFailed(
                        'Failed to create snapshot %s of disk %s: %s' %
                        (snapshot_name, disk, str(snapshot_response)))

            if self.config['mode'].lower() == 'disks.snapshots.purge':
                max_snapshots = self._jinja_expand_int(
                    self.config['maxSnapshots'], 'max_snapshots')

                snapshot_request = None
                page_token = None
                matching_snapshots = []
                while True:
                    snapshot_request = compute_service.snapshots().list(
                        project=project, pageToken=page_token)
                    snapshot_response = snapshot_request.execute()
                    if 'items' in snapshot_response:
                        for snapshot in snapshot_response['items']:
                            if re.match(snapshot_name, snapshot['name']):
                                matching_snapshots.append(snapshot)
                    if 'nextPageToken' in snapshot_response:
                        page_token = snapshot_response['nextPageToken']
                    else:
                        break
                if len(matching_snapshots) > max_snapshots:
                    matching_snapshots.sort(
                        key=lambda item: item['creationTimestamp'],
                        reverse=True)
                    for snapshot in matching_snapshots[max_snapshots:]:
                        self.logger.info(
                            'Purging snapshot %s in project %s...' %
                            (snapshot['name'], project))
                        delete_request = compute_service.snapshots().delete(
                            project=project, snapshot=snapshot['name'])
                        delete_response = delete_request.execute()
                        if 'id' in delete_response:
                            self.wait_for_operation_done(
                                compute_service, delete_response['id'],
                                delete_response['selfLink'], project, zone,
                                region, timeout)
                    return {output_var: len(matching_snapshots)}

        if self.config['mode'].lower().startswith('disks.instantsnapshots.'):
            if 'snapshotName' not in self.config:
                raise NotConfiguredException(
                    'No snapshotName in configuration!')

            snapshot_name = self._jinja_expand_string(
                self.config['snapshotName'], 'snapshot_name')

            compute_service_beta = discovery.build(
                'compute',
                'beta',
                cache_discovery=False,
                discoveryServiceUrl=
                'https://www.googleapis.com/discovery/v1/apis/compute/beta/rest',
                http=self._get_branded_http(credentials))

            if self.config['mode'].lower() == 'disks.instantsnapshots.create':
                request_body = {
                    'name': snapshot_name,
                    'sourceDisk': disk,
                }
                if 'snapshotParameters' in self.config:
                    snapshot_parameters = self._jinja_expand_dict_all(
                        self.config['snapshotParameters'],
                        'snapshot_parameters')
                    request_body = {**request_body, **snapshot_parameters}

                if 'labels' in self.config:
                    request_body['labels'] = self._jinja_expand_dict_all(
                        self.config['labels'], 'labels')
                snapshot_request = None
                if '/regions/' in disk:
                    self.logger.info(
                        'Creating instant snapshot %s of disk %s in %s...' %
                        (snapshot_name, disk, region))
                    snapshot_request = compute_service_beta.regionInstantSnapshots(
                    ).insert(project=project, region=region, body=request_body)
                else:
                    self.logger.info(
                        'Creating instant snapshot %s of disk %s in %s...' %
                        (snapshot_name, disk, zone))
                    snapshot_request = compute_service_beta.instantSnapshots(
                    ).insert(project=project, zone=zone, body=request_body)
                snapshot_response = snapshot_request.execute()
                if 'id' in snapshot_response:
                    ret = self.wait_for_operation_done(
                        compute_service_beta, snapshot_response['id'],
                        snapshot_response['selfLink'], project, zone, region,
                        timeout)
                    return {output_var: ret}
                else:
                    raise ComputeengineOperationFailed(
                        'Failed to create instant snapshot %s of disk %s: %s' %
                        (snapshot_name, disk, str(snapshot_response)))

            if self.config['mode'].lower() == 'disks.instantsnapshots.purge':
                max_snapshots = self._jinja_expand_int(
                    self.config['maxSnapshots'], 'max_snapshots')

                snapshot_request = None
                page_token = None
                matching_snapshots = []
                while True:
                    if region is not None:
                        snapshot_request = compute_service_beta.regionInstantSnapshots(
                        ).list(project=project,
                               region=region,
                               pageToken=page_token)
                    else:
                        snapshot_request = compute_service_beta.instantSnapshots(
                        ).list(project=project, zone=zone, pageToken=page_token)
                    snapshot_response = snapshot_request.execute()
                    if 'items' in snapshot_response:
                        for snapshot in snapshot_response['items']:
                            if re.match(snapshot_name, snapshot['name']):
                                matching_snapshots.append(snapshot)
                    if 'nextPageToken' in snapshot_response:
                        page_token = snapshot_response['nextPageToken']
                    else:
                        break
                if len(matching_snapshots) > max_snapshots:
                    matching_snapshots.sort(
                        key=lambda item: item['creationTimestamp'],
                        reverse=True)
                    for snapshot in matching_snapshots[max_snapshots:]:
                        delete_request = None
                        self.logger.info(
                            'Purging snapshot %s in project %s...' %
                            (snapshot['name'], project))
                        if '/regions/' in snapshot['selfLink']:
                            delete_request = compute_service_beta.regionInstantSnapshots(
                            ).delete(project=project,
                                     region=region,
                                     instantSnapshot=snapshot['name'])
                        else:
                            delete_request = compute_service_beta.instantSnapshots(
                            ).delete(project=project,
                                     zone=zone,
                                     instantSnapshot=snapshot['name'])
                        delete_response = delete_request.execute()
                        if 'id' in delete_response:
                            self.wait_for_operation_done(
                                compute_service_beta, delete_response['id'],
                                delete_response['selfLink'], project, zone,
                                region, timeout)
                    return {output_var: len(matching_snapshots)}
        return {
            output_var: None,
        }

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


class LoadbalancingOperationFailed(Exception):
    pass


class LoadbalancingProcessor(Processor):
    """
    Perform actions on Cloud Load Balancers.

    Args:
        project (str, optional): Google Cloud project ID.
        backend_service (str): Backend service to operate on.
        timeout (int, optional): Timeout of waiting on operations.
        region (str, optional): Google Cloud region.
        mode (str): One of: backendservice.get, regionbackendservice.get, backendservice.patch, regionbackendservice.patch
    """

    def get_default_config_key():
        return 'loadbalancing'

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

    def get_backend(self, compute_service, project, backend_service):
        get_request = compute_service.backendServices().get(
            project=project, backendService=backend_service)
        get_response = get_request.execute()
        if 'id' in get_response:
            return get_response
        else:
            raise LoadbalancingOperationFailed(
                'Failed to get backend service: %s' % str(get_response))

    def get_region_backend(self, compute_service, project, region,
                           backend_service):
        get_request = compute_service.regionBackendServices().get(
            project=project, region=region, backendService=backend_service)
        get_response = get_request.execute()
        if 'id' in get_response:
            return get_response
        else:
            raise LoadbalancingOperationFailed(
                'Failed to get regional backend service: %s' %
                str(get_response))

    def process(self, output_var='loadbalancing'):
        if 'mode' not in self.config:
            raise NotConfiguredException(
                'No Cloud Load Balancing operation specified.')
        if 'backendService' not in self.config:
            raise NotConfiguredException(
                'No backend service name specified in the configuration.')

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
        backend_service = self._jinja_expand_string(
            self.config['backendService'], 'backend_service')

        if self.config['mode'] == 'backendservice.get':
            return {
                output_var:
                    self.get_backend(compute_service, project, backend_service)
            }

        if self.config['mode'] == 'regionbackendservice.get':
            region = self._jinja_expand_string(self.config['region'], 'region')
            return {
                output_var:
                    self.get_region_backend(compute_service, project, region,
                                            backend_service)
            }

        if 'patch' not in self.config:
            raise NotConfiguredException(
                'No backend service patch fields specified in the configuration.'
            )

        patches = self._jinja_expand_dict_all(self.config['patch'], 'patch')
        if self.config['mode'] == 'backendservice.patch':
            backend = self.get_backend(compute_service, project,
                                       backend_service)
            patch_request = compute_service.backendServices().patch(
                project=project, backendService=backend_service, body=patches)
            patch_response = patch_request.execute()
            if 'id' in patch_response:
                self.wait_for_operation_done(compute_service,
                                             patch_response['id'],
                                             patch_response['selfLink'],
                                             project, None, region, timeout)
                backend = self.get_backend(compute_service, project,
                                           backend_service)
            return {output_var: backend}

        if self.config['mode'] == 'regionbackendservice.patch':
            if 'region' not in self.config:
                raise NotConfiguredException(
                    'No backend service region specified in the configuration.')
            region = self._jinja_expand_string(self.config['region'], 'region')
            backend = self.get_region_backend(compute_service, project, region,
                                              backend_service)
            patch_request = compute_service.regionBackendServices().patch(
                project=project,
                region=region,
                backendService=backend_service,
                body=patches)
            patch_response = patch_request.execute()
            if 'id' in patch_response:
                self.wait_for_operation_done(compute_service,
                                             patch_response['id'],
                                             patch_response['selfLink'],
                                             project, None, region, timeout)
                backend = self.get_region_backend(compute_service, project,
                                                  region, backend_service)
            return {output_var: backend}

        return {
            output_var: None,
        }

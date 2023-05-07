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


class ClouddeployProcessor(Processor):
    """
    Operate Cloud Deploy applications, releases and other such things.

    Args:
        project (str, optional): Google Cloud project ID.
        name (str): Name of the delivery pipeline.
        region (str): Google Cloud Deploy reiog.n
        mode (str): One of: releases.get, releases.create, releases.rollouts.create, releases.rollouts.get, 
          releases.rollouts.approve, releases.rollouts.reject
    """

    def get_default_config_key():
        return 'clouddeploy'

    def wait_for_operation_done(self, deploy_service, operation_name):
        end_time = start_time = time.monotonic()
        while True and (end_time - start_time) < 60:
            op_request = deploy_service.projects().locations().operations().get(
                name=operation_name).execute()
            if op_request['done']:
                if 'error' in op_request:
                    self.logger.error(
                        'Error while waiting for long running operation %s to complete.'
                        % (operation_name),
                        extra={'error': op_request['error']})
                    return op_request['error']
                response = op_request['response']
                del response['@type']
                return response
            time.sleep(5)
            end_time = time.monotonic()

    def process(self, output_var='clouddeploy'):
        if 'region' not in self.config:
            raise NotConfiguredException('No Cloud Deploy region specified.')
        if 'name' not in self.config:
            raise NotConfiguredException(
                'No Cloud Deploy delivery pipeline name specified.')
        if 'mode' not in self.config:
            raise NotConfiguredException('No Cloud Deploy operation specified.')

        credentials, credentials_project_id = google.auth.default()
        project = self._jinja_expand_string(
            self.config['project'],
            'project') if 'project' in self.config else credentials_project_id
        if not project:
            project = credentials.quota_project_id

        region_name = self._jinja_expand_string(self.config['region'], 'region')
        pipeline_name = self._jinja_expand_string(self.config['name'], 'name')
        pipeline_full_name = "projects/%s/locations/%s/deliveryPipelines/%s" % (
            project, region_name, pipeline_name)

        deploy_service = discovery.build(
            'clouddeploy', 'v1', http=self._get_branded_http(credentials))
        deploy_base_request = deploy_service.projects().locations(
        ).deliveryPipelines()

        if self.config['mode'] == 'pipelines.get':
            deploy_response = deploy_base_request.get(
                name=pipeline_full_name).execute()
            return {
                output_var: deploy_response,
            }

        if self.config['mode'] == 'releases.get':
            deploy_response = deploy_base_request.releases().get(
                name=pipeline_full_name).execute()
            return {
                output_var: deploy_response,
            }

        if self.config['mode'] == 'releases.create':
            if 'releaseId' not in self.config:
                raise NotConfiguredException(
                    'No releaseId parameter configured for releases.create.')

            release_id = self._jinja_expand_string(self.config['releaseId'],
                                                   'release_id')

            if 'release' not in self.config:
                raise NotConfiguredException(
                    'No release parameter configured for releases.create.')

            body = self._jinja_expand_dict_all(self.config['release'],
                                               'release')
            deploy_response = deploy_base_request.releases().create(
                body=body, parent=pipeline_full_name,
                releaseId=release_id).execute()
            deploy_response = self.wait_for_operation_done(
                deploy_service, deploy_response['name'])
            return {
                output_var: deploy_response,
            }

        if self.config['mode'] == 'releases.rollouts.create':
            if 'releaseId' not in self.config:
                raise NotConfiguredException(
                    'No releaseId parameter configured for releases.rollouts.create.'
                )
            if 'rolloutId' not in self.config:
                raise NotConfiguredException(
                    'No rolloutId parameter configured for releases.rollouts.create.'
                )

            release_id = self._jinja_expand_string(self.config['releaseId'],
                                                   'release_id')
            rollout_id = self._jinja_expand_string(self.config['rolloutId'],
                                                   'rollout_id')

            if 'rollout' not in self.config:
                raise NotConfiguredException(
                    'No rollout parameter configured for releases.rollouts.create.'
                )

            body = self._jinja_expand_dict_all(self.config['rollout'],
                                               'rollout')

            if '/releases/' not in release_id:
                release_full_name = '%s/releases/%s' % (pipeline_full_name,
                                                        release_id)
            else:
                release_full_name = release_id
            deploy_response = deploy_base_request.releases().rollouts().create(
                body=body, parent=release_full_name,
                rolloutId=rollout_id).execute()
            deploy_response = self.wait_for_operation_done(
                deploy_service, deploy_response['name'])
            return {
                output_var: deploy_response,
            }

        if self.config['mode'] == 'releases.rollouts.approve' or self.config[
                'mode'] == 'releases.rollouts.reject':
            if 'releaseId' not in self.config:
                raise NotConfiguredException(
                    'No releaseId parameter configured for releases.rollouts.approve/reject.'
                )
            if 'rolloutId' not in self.config:
                raise NotConfiguredException(
                    'No rolloutId parameter configured for releases.rollouts.approve/reject.'
                )

            release_id = self._jinja_expand_string(self.config['releaseId'],
                                                   'release_id')
            rollout_id = self._jinja_expand_string(self.config['rolloutId'],
                                                   'rollout_id')

            if self.config['mode'] == 'releases.rollouts.approve':
                body = {'approved': True}
            else:
                body = {'approved': False}

            if '/releases/' not in release_id:
                release_full_name = '%s/releases/%s' % (pipeline_full_name,
                                                        release_id)
            else:
                release_full_name = release_id
            if '/rollouts/' in rollout_id:
                rollout_full_name = rollout_id
            else:
                rollout_full_name = '%s/rollouts/%s' % (release_full_name,
                                                        rollout_id)

            deploy_response = deploy_base_request.releases().rollouts().approve(
                body=body, name=rollout_full_name).execute()
            return {
                output_var: deploy_response,
            }

        return {
            output_var: None,
        }

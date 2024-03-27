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
from .base import Processor, NotConfiguredException
import google.auth
from googleapiclient import discovery
import time
from _vendor.python_docker.registry import Registry


class DockerProcessor(Processor):
    """
    Perform actions on Docker registries.

    Args:
        hostname (str): Docker registry hostname. 
        username (str, optional): Username for Docker registry. Defaults to SA authentication for Artifact Registry.
        password (str, optional): Password for Docker registry.
        image (str): Image to pull/push
        tag (str, optional): Tag to pull/push, defaults to latest.
        mode (str): image.copy, image.delete, image.deleteversion, images.list
        destination_hostname (str, optional): Docker registry hostname. (For copy)
        destination_username (str, optional): Username for Docker registry. Defaults to SA authentication for Artifact Registry. (For copy)
        destination_password (str, optional): Password for Docker registry. (For copy)
        destination_image (str): Image to pull/push
        destination_tag (str, optional): Tag to pull/push, defaults to latest.
    """

    def get_default_config_key():
        return 'docker'

    def wait_for_operation_done(self, ar_service, operation_name):
        end_time = start_time = time.monotonic()
        while True and (end_time - start_time) < 60:
            op_request = ar_service.projects().locations().operations().get(
                name=operation_name).execute()
            if 'done' in op_request and op_request['done']:
                if 'error' in op_request:
                    self.logger.error(
                        'Error while waiting for long running operation %s to complete.'
                        % (operation_name),
                        extra={'error': op_request['error']})
                    return op_request['error']
                response = op_request['response']
                del response['@type']
                return response
            time.sleep(2)
            end_time = time.monotonic()

    def process(self, output_var='docker'):
        if 'mode' not in self.config:
            raise NotConfiguredException('No Docker operation specified.')

        credentials, credentials_project_id = google.auth.default()

        mode = self._jinja_expand_string(self.config['mode'], 'mode')
        image = None
        tag = None
        if 'image' not in self.config and mode != 'images.list':
            raise NotConfiguredException('No Docker image specified.')
        elif mode != 'images.list':
            image = self._jinja_expand_string(self.config['image'], 'image')
            tag = self._jinja_expand_string(
                self.config['tag'], 'tag') if 'tag' in self.config else 'latest'

        hostname = self._jinja_expand_string(self.config['hostname'],
                                             'hostname')
        username = None
        password = None
        if '.pkg.dev' not in hostname and 'gcr.io' not in hostname:
            if 'username' not in self.config or 'password' not in self.config:
                raise NotConfiguredException(
                    'No Docker username or password specified.')

            username = self._jinja_expand_string(self.config['username'],
                                                 'username')
            password = self._jinja_expand_string(self.config['password'],
                                                 'password')
        else:
            username = "_dcgcr_2_0_0_token"
            auth_req = google.auth.transport.requests.Request()
            credentials.refresh(auth_req)
            password = credentials.token

        source_registry = Registry(hostname=hostname,
                                   username=username,
                                   password=password)
        destination_registry = None
        destination_hostname = None
        if 'destination_hostname' not in self.config:
            destination_registry = source_registry
            destination_hostname = hostname
        else:
            destination_hostname = self._jinja_expand_string(
                self.config['destination_hostname'], 'hostname')
            destination_username = username
            destination_password = password
            if '.pkg.dev' not in destination_hostname and 'gcr.io' not in destination_hostname:
                if 'destination_username' not in self.config or 'destination_password' not in self.config:
                    raise NotConfiguredException(
                        'No Docker username or password specified.')

                if 'destination_username' in self.config:
                    destination_username = self._jinja_expand_string(
                        self.config['destination_username'], 'username')
                if 'destination_password' in self.config:
                    destination_password = self._jinja_expand_string(
                        self.config['destination_password'], 'password')
            else:
                destination_username = "_dcgcr_2_0_0_token"
                auth_req = google.auth.transport.requests.Request()
                credentials.refresh(auth_req)
                destination_password = credentials.token

            destination_registry = Registry(hostname=destination_hostname,
                                            username=destination_username,
                                            password=destination_password)

        if mode == 'image.copy':
            destination_image = self._jinja_expand_string(
                self.config['destination_image'],
                'image') if 'destination_image' in self.config else image
            destination_tag = self._jinja_expand_string(
                self.config['destination_tag'],
                'tag') if 'destination_tag' in self.config else tag

            self.logger.info('Pulling image from: %s/%s:%s' %
                             (hostname, image, tag),
                             extra={
                                 'registry': hostname,
                                 'image': image,
                                 'tag': tag
                             })

            source_image = source_registry.pull_image(image, tag, lazy=True)

            self.logger.info(
                'Pushing image to: %s/%s:%s' %
                (destination_hostname, destination_image, destination_tag),
                extra={
                    'registry': destination_hostname,
                    'image': destination_image,
                    'tag': destination_tag
                })

            source_image.name = destination_image
            source_image.tag = destination_tag
            destination_registry.push_image(source_image)

            self.logger.info(
                'Pushed image to: %s/%s:%s' %
                (destination_hostname, destination_image, destination_tag),
                extra={
                    'registry': destination_hostname,
                    'image': destination_image,
                    'tag': destination_tag
                })
            return {
                output_var: {
                    'registry': destination_hostname,
                    'image': destination_image,
                    'tag': destination_tag
                }
            }

        if mode == 'image.delete' or mode == 'image.deleteversion':
            self.logger.info('Deleting image from: %s/%s:%s' %
                             (hostname, image, tag),
                             extra={
                                 'registry': hostname,
                                 'image': image,
                                 'tag': tag
                             })
            if '.pkg.dev' in hostname:
                ar_service = discovery.build(
                    'artifactregistry',
                    'v1',
                    http=self._get_branded_http(credentials))

                location = hostname.replace('https://',
                                            '').replace('-docker.pkg.dev', '')

                image_parts = image.split('/')
                project = image_parts[0]
                repository = image_parts[1]
                image = '/'.join(image_parts[2:])

                name = 'projects/%s/locations/%s/repositories/%s/packages/%s' % (
                    project, location, repository, image)
                ar_request = ar_service.projects().locations().repositories(
                ).packages().delete(name=name)
                if mode == 'image.deleteversion':
                    name = 'projects/%s/locations/%s/repositories/%s/packages/%s/tags/%s' % (
                        project, location, repository, image, tag)
                    ar_request = ar_service.projects().locations().repositories(
                    ).packages().tags().delete(name=name)
                ar_response = ar_request.execute()
                if 'name' in ar_response:
                    self.wait_for_operation_done(ar_service,
                                                 ar_response['name'])
            else:
                source_registry.delete_image(image, tag)

        if mode == 'images.list':
            self.logger.info('Listing images from: %s/%s:%s' %
                             (hostname, image, tag),
                             extra={
                                 'registry': hostname,
                                 'image': image,
                                 'tag': tag
                             })

            return {output_var: source_registry.list_images()}

        return {
            output_var: None,
        }

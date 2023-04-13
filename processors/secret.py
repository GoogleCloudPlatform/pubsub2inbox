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
from google.cloud import secretmanager
from helpers.base import get_grpc_client_info
import base64
import json
import yaml


class SecretProcessor(Processor):
    """
    Fetch secrets from Secret Manager API and store them in Jinja
    environment.

    Args:
        project (str, optional): Google Cloud project ID.
        secret (str): Secret name.
        version (str, optional): Secret version, defaults to "latest".
        mode (str, optional): Mode of operation, by default leaves data untouched. 
          Also supports "json" to parse JSON, "yaml" for YAML, "base64" for base64.
    """

    def get_default_config_key():
        return 'secret'

    def process(self, output_var='secret'):
        if 'secret' not in self.config:
            raise NotConfiguredException(
                'No Secret Manager secret config specified.')
        secret_name = self.config['secret']
        if 'version' in self.config:
            secret_version = self.config['version']

        credentials, credentials_project_id = google.auth.default()
        project = self.config[
            'project'] if 'project' in self.config else credentials_project_id
        if not project:
            project = credentials.quota_project_id

        secret_full_name = "projects/%s/secrets/%s/versions/%s" % (
            project, secret_name, secret_version)

        client = secretmanager.SecretManagerServiceClient(
            client_info=get_grpc_client_info())
        response = client.access_secret_version(name=secret_full_name)
        secret_contents = response.payload.data.decode('UTF-8')
        if 'mode' in self.config:
            if 'base64' in self.config['mode']:
                secret_contents = base64.b64decode(secret_contents).decode(
                    'UTF-8')
            if 'json' in self.config['mode']:
                secret_contents = json.loads(secret_contents)
            if 'yaml' in self.config['mode']:
                secret_contents = yaml.load(secret_contents,
                                            Loader=yaml.SafeLoader)
        return {
            output_var: secret_contents,
        }

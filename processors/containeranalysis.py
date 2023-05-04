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
from helpers.base import get_grpc_client_info
import base64
import json
import yaml
from googleapiclient import discovery


class ContaineranalysisProcessor(Processor):
    """
    Fetch occurrences and notes from Container Analysis API.

    Args:
        project (str, optional): Google Cloud project ID.
        name (str): Occurrence/note name (projects/.../occurrents/...).
    """

    def get_default_config_key():
        return 'containeranalysis'

    def process(self, output_var='containeranalysis'):
        if 'name' not in self.config:
            raise NotConfiguredException(
                'No occurrence/note name specified specified.')
        name = self._jinja_expand_string(self.config['name'])

        credentials, credentials_project_id = google.auth.default()
        project = self.config[
            'project'] if 'project' in self.config else credentials_project_id
        if not project:
            project = credentials.quota_project_id

        container_service = discovery.build(
            'containeranalysis', 'v1', http=self._get_branded_http(credentials))

        if '/occurrences/' in name:
            request = container_service.projects().occurrences().get(name=name)
            contents = request.execute()
        else:
            request = container_service.projects().notes().get(name=name)
            contents = request.execute()
        return {
            output_var: contents,
        }

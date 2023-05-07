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
from .base import Processor, NotConfiguredException
from googleapiclient import discovery
import google.auth


class DnsProcessor(Processor):
    """
    Submit changes to Cloud DNS API. For more information, see:
    https://cloud.google.com/dns/docs/reference/v1/changes

    Args:
        managedZone (str): Cloud DNS zone ID.
        project (str, optional): Google Cloud project ID.
        changes (dict): Changes to submit.
    """

    def get_default_config_key():
        return 'dns'

    def process(self, output_var='dns'):
        if 'managedZone' not in self.config:
            raise NotConfiguredException(
                'No DNS zone specified in configuration.')

        zone = self._jinja_expand_string(self.config['managedZone'], 'zone')

        credentials, credentials_project_id = google.auth.default()
        project = self.config[
            'project'] if 'project' in self.config else credentials_project_id
        if not project:
            project = credentials.quota_project_id

        # project_number = self.get_project_number(project)

        dns_changes = self._jinja_expand_dict_all(self.config['changes'],
                                                  'changes')
        dns_changes['kind'] = 'dns#change'

        dns_service = discovery.build('dns',
                                      'v1',
                                      http=self._get_branded_http(credentials))

        dns_request = dns_service.changes().create(project=project,
                                                   managedZone=zone,
                                                   body=dns_changes)
        dns_response = dns_request.execute()

        return {
            output_var: dns_response,
        }

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
from helpers.base import get_user_agent
import requests
import json


class OpsgenieProcessor(Processor):
    """
    Create OpsGenie alerts and incidents.

    Args:
        endpoint (str, optional): OpsGenie API endpoint (use https://api.eu.opsgenie.com/v2 for EU).
        token (str): OpsGenie authentication token.
        mode (str): One of: alert.create, incident.create
        data (dict): Body data for API call.
    """

    def get_default_config_key():
        return 'opsgenie'

    def process(self, output_var='opsgenie'):
        api_endpoint = 'https://api.opsgenie.com/v2/'
        if 'endpoint' in self.config:
            api_endpoint = self._jinja_expand_string(self.config['endpoint'],
                                                     'endpoint')
        if 'mode' not in self.config:
            raise NotConfiguredException('No OpsGenie operation specified.')
        if 'token' not in self.config:
            raise NotConfiguredException(
                'No OpsGenie authorization token specified.')
        if 'data' not in self.config:
            raise NotConfiguredException(
                'No OpsGenie API operation body specified.')
        if not api_endpoint.endswith('/'):
            api_endpoint += '/'

        api_method = 'POST'
        api_content_type = 'application/json; charset=utf-8'
        api_body = self._jinja_expand_dict_all(self.config['data'], 'data')
        api_token = self._jinja_expand_string(self.config['token'], 'token')
        api_headers = {
            'User-Agent': get_user_agent(),
            'Content-type': api_content_type,
            'Authorization': 'GenieKey %s' % (api_token),
        }
        if self.config['mode'] == 'alert.create':
            api_url = '%salerts' % (api_endpoint)
            api_response = requests.request(api_method,
                                            headers=api_headers,
                                            url=api_url,
                                            data=json.dumps(api_body))
            api_response.raise_for_status()
            return {
                output_var: {
                    'status_code': api_response.status_code,
                    'headers': dict(api_response.headers),
                    'response': api_response.json()
                },
            }

        if self.config['mode'] == 'incident.create':
            api_url = '%sincidents' % (api_endpoint)
            api_response = requests.request(api_method,
                                            headers=api_headers,
                                            url=api_url,
                                            data=json.dumps(api_body))
            return {
                output_var: {
                    'status_code': api_response.status_code,
                    'headers': dict(api_response.headers),
                    'response': api_response.json()
                },
            }

        return {
            output_var: None,
        }

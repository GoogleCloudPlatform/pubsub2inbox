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
from .base import Output, NotConfiguredException
from helpers.base import get_user_agent
import requests
import json


class SlackOutput(Output):
    """
    Sends messages to Slack and call other Slack APIs too.

    Args:
        token (str): A Slack Bot User OAuth Token.
        api (str): A Slack API call, such as chat.postMessage.
        request (dict): The API call body.
    """

    def output(self):
        if 'token' not in self.output_config:
            raise NotConfiguredException('No Slack token configured!')
        if 'api' not in self.output_config:
            raise NotConfiguredException('No Slack API call configured!')
        if 'request' not in self.output_config:
            raise NotConfiguredException('No Slack API call body configured!')

        token = self._jinja_expand_string(self.output_config['token'], 'token')
        api = self._jinja_expand_string(self.output_config['api'], 'api')
        request = self._jinja_expand_dict_all(self.output_config['request'],
                                              'request')

        self.logger.info('Calling Slack API: %s' % (api),
                         extra={
                             "slack_api": api,
                         })

        api_path = 'https://slack.com/api/%s' % (api)
        request_body = json.dumps(request)
        headers = {
            'User-Agent': get_user_agent(),
            'Content-type': 'application/json; charset=utf-8',
            'Authorization': 'Bearer %s' % (token)
        }

        response = requests.post(api_path, data=request_body, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        if 'error' in response_json:
            self.logger.error('Error when calling Slack API: %s',
                              response_json['error'],
                              extra={'slack_error': response_json['error']})

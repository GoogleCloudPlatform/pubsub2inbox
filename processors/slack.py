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


class SlackProcessor(Processor):
    """
    Slack processor for fetching messages.

    Args:
        token (str): A Slack Bot User OAuth Token.
        api (str): One of: conversations.list, conversations.history, conversations.replies,
        request (dict): The API call body.
    """

    def get_default_config_key():
        return 'slack'

    def call_slack(self, api, token, request, urlencoded=False):
        self.logger.info('Calling Slack API: %s' % (api),
                         extra={
                             "slack_api": api,
                         })

        api_path = 'https://slack.com/api/%s' % (api)
        if urlencoded:
            request_body = request
        else:
            request_body = json.dumps(request)
        headers = {
            'User-Agent': get_user_agent(),
            'Content-type': 'application/json; charset=utf-8',
            'Authorization': 'Bearer %s' % (token)
        }
        if urlencoded:
            headers[
                'Content-type'] = 'application/x-www-form-urlencoded; charset=utf-8'

        response = requests.post(api_path, data=request_body, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        return response_json

    def process(self, output_var='slack'):
        if 'api' not in self.config:
            raise NotConfiguredException('No Slack API call specified.')
        if 'token' not in self.config:
            raise NotConfiguredException('No Slack token specified.')
        if 'request' not in self.config:
            self.config['request'] = {}

        token = self._jinja_expand_string(self.config['token'], 'token')
        slack_api = self._jinja_expand_string(self.config['api'], 'api')
        request_params = self._jinja_expand_dict_all(self.config['request'],
                                                     'request')
        if slack_api == 'conversations.list':
            slack_response = self.call_slack(self.config['api'], token,
                                             request_params, True)
            self.logger.debug('Slack API %s responded.' % (slack_api),
                              extra={
                                  'slack_request': request_params,
                                  'slack_response': slack_response
                              })
            return {
                output_var: slack_response,
            }

        if slack_api == 'conversations.history':
            slack_response = self.call_slack(self.config['api'], token,
                                             request_params)
            self.logger.debug('Slack API %s responded.' % (slack_api),
                              extra={
                                  'slack_request': request_params,
                                  'slack_response': slack_response
                              })
            return {
                output_var: slack_response,
            }

        if slack_api == 'conversations.replies':
            slack_response = self.call_slack(self.config['api'], token,
                                             request_params, True)
            self.logger.debug('Slack API %s responded.' % (slack_api),
                              extra={
                                  'slack_request': request_params,
                                  'slack_response': slack_response
                              })
            return {
                output_var: slack_response,
            }

        return {
            output_var: None,
        }

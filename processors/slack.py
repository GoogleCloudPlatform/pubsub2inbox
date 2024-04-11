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
import base64


class SlackProcessor(Processor):
    """
    Slack processor for fetching messages.

    Args:
        token (str): A Slack Bot User OAuth Token.
        api (str): One of: conversations.list, conversations.history, conversations.replies
        mode (str, optional: api, processMessages or lastImage (default api)
        multimodal (bool, optional): Use multi-modal processing in processMessages.
        messages (list, optional): List of messages to process.
        appId (str, optional): The app ID to detect bot messages.
        prompt (str, optional): Initial message to append to the beginning of the conversation.
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
            headers['Content-type'] = 'application/x-www-form-urlencoded'

        response = requests.post(api_path, data=request_body, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        return response_json

    def download_slack(self, url, token):
        self.logger.info('Downloading from Slack: %s' % (url),
                         extra={
                             "slack_url": url,
                         })
        headers = {
            'User-Agent': get_user_agent(),
            'Authorization': 'Bearer %s' % (token)
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return base64.b64encode(response.content).decode('ascii')

    def _slack_message_to_parts(self, message, token, multi_modal, no_question):
        parts = []
        if 'files' in message and multi_modal:
            for file in message['files']:
                if file['size'] >= 20971520:  # 20MB limit
                    self.logger.debug(
                        'Attachment too large to download from Slack (%d bytes).'
                        % (file['size']),
                        extra={'file': file})
                    continue
                if file['mimetype'][0:6] == 'image/':
                    self.logger.info(
                        'Downloaded Slack image (720p version): %s (mime %s)' %
                        (file['thumb_720'], file['mimetype']),
                        extra={'mimetype': file['mimetype']})
                    if 'thumb_720' in file:
                        parts.append({
                            'inlineData': {
                                'mimeType':
                                    file['mimetype'],
                                'data':
                                    self.download_slack(file['thumb_720'],
                                                        token)
                            }
                        })
                    elif 'url_private_download' in file:
                        self.logger.info(
                            'Downloaded Slack image (full version): %s (mime %s)'
                            % (file['url_private_download'], file['mimetype']),
                            extra={'mimetype': file['mimetype']})
                        parts.append({
                            'inlineData': {
                                'mimeType':
                                    file['mimetype'],
                                'data':
                                    self.download_slack(
                                        file['url_private_download'], token)
                            }
                        })
                elif 'url_private_download' in file:
                    self.logger.info(
                        'Downloaded Slack file: %s (mime %s)' %
                        (file['url_private_download'], file['mimetype']),
                        extra={'mimetype': file['mimetype']})
                    parts.append({
                        'inlineData': {
                            'mimeType':
                                file['mimetype'],
                            'data':
                                self.download_slack(
                                    file['url_private_download'], token)
                        }
                    })
        if 'text' in message and message['text'] != '':
            parts.append({'text': message['text']})
        elif no_question != '':
            parts.append({'text': no_question})

        return parts

    def process(self, output_var='slack'):
        if 'api' not in self.config and 'mode' not in self.config:
            raise NotConfiguredException('No Slack API call specified.')
        if 'token' not in self.config:
            raise NotConfiguredException('No Slack token specified.')
        if 'request' not in self.config:
            self.config['request'] = {}

        mode = self._jinja_expand_string(
            self.config['mode'], 'mode') if 'mode' in self.config else 'api'

        token = self._jinja_expand_string(self.config['token'], 'token')
        slack_api = None
        if mode == 'api':
            slack_api = self._jinja_expand_string(self.config['api'], 'api')
        request_params = self._jinja_expand_dict_all(self.config['request'],
                                                     'request')

        mode = self._jinja_expand_string(
            self.config['mode'], 'mode') if 'mode' in self.config else 'api'

        if mode == 'processMessages' or mode == 'lastImage':
            if 'messages' not in self.config:
                raise NotConfiguredException('No Slack messages specified.')
            if 'appId' not in self.config:
                raise NotConfiguredException('No Slack app ID specified.')
            app_id = self._jinja_expand_string(self.config['appId'], 'app_id')
            multi_modal = self._jinja_expand_bool(
                self.config['multimodal'],
                'multimodal') if 'multimodal' in self.config else False
            messages = self._jinja_expand_expr(self.config['messages'],
                                               'messages')

            no_question = self._jinja_expand_string(
                self.config['noQuestionPrompt'], 'no_question_prompt'
            ) if 'noQuestionPrompt' in self.config else "Answer the question in this audio clip or image."

            processed = []
            if 'messages' in messages:
                messages = messages['messages']

            for message in messages:
                new_message = None
                if 'app_id' in message:
                    if message['app_id'] == app_id:
                        parts = self._slack_message_to_parts(
                            message, token, multi_modal, no_question)
                        if len(parts) > 0:
                            new_message = {'role': 'MODEL', 'parts': parts}
                else:
                    parts = self._slack_message_to_parts(
                        message, token, multi_modal, no_question)
                    if len(parts) > 0:
                        new_message = {'role': 'USER', 'parts': parts}
                if new_message:
                    processed.append(new_message)

            print('PROCESSED', processed)

            # Prepend an initial prompt that can be instructions or such
            if 'prompt' in self.config:
                prompt_added = False
                for msg_idx, msg in enumerate(processed):
                    if msg['role'] == 'USER':
                        for part_idx, part in enumerate(msg['parts']):
                            if 'text' in part:
                                processed[msg_idx]['parts'][part_idx][
                                    'text'] = self._jinja_expand_string(
                                        self.config['prompt'],
                                        'prompt') + " " + processed[msg_idx][
                                            'parts'][part_idx]['text']
                                prompt_added = True
                                break
                    if prompt_added:
                        break

            if mode == 'lastImage':
                if len(processed) > 0:
                    last_message = processed[len(processed) - 1]
                    for part in last_message['parts']:
                        if 'inlineData' in part:
                            if part['inlineData']['mimeType'][0:6] == 'image/':
                                return {output_var: part['inlineData']['data']}
                return {output_var: None}
            return {output_var: processed}

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

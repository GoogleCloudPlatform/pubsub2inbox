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
import json
import google.auth
from google.auth.transport.requests import AuthorizedSession


class VertexgenaiProcessor(Processor):
    """
    Vertex AI Generative AI processor.

    Args:
        region (str): Endpoint to use.
        modelId (str): Deployed model to use.
        project (str, optional): Google Cloud project ID.
        method (str, optional): Method to call, by default: "predict"
        returnErrors (bool, optional): Set to true to return errors
        request (dict): Request.
    """

    def get_default_config_key():
        return 'vertexgenai'

    def process(self, output_var='vertexgenai'):
        if 'location' not in self.config:
            raise NotConfiguredException('No location specified specified.')
        if 'modelId' not in self.config:
            raise NotConfiguredException('No model ID specified.')
        if 'request' not in self.config:
            raise NotConfiguredException('No request specified.')
        credentials, credentials_project_id = google.auth.default()
        project = self.config[
            'project'] if 'project' in self.config else credentials_project_id
        if not project:
            project = credentials.quota_project_id

        method = self._jinja_expand_string(
            self.config['method'],
            'method') if 'method' in self.config else 'predict'

        location = self._jinja_expand_string(self.config['location'],
                                             'location')
        model_id = self._jinja_expand_string(self.config['modelId'], 'modelId')

        api_path = 'https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/publishers/google/models/%s:%s' % (
            location, project, location, model_id, method)

        return_errors = False
        if 'returnErrors' in self.config:
            return_errors = self._jinja_expand_bool(self.config['returnErrors'],
                                                    'return_errors')

        request = self._jinja_expand_dict_all_expr(self.config['request'],
                                                   'request')
        headers = {
            'User-Agent': get_user_agent(),
            'Content-type': 'application/json; charset=utf-8',
        }

        if method == 'predict':
            # Messages must be USER, AI, USER, AI.. etc, so filter them
            # to make life easier.
            if 'instances' in request:
                new_instances = []
                for instance in request['instances']:
                    new_instance = instance
                    if 'messages' in instance:
                        new_messages = []
                        last_author = None
                        for message in reversed(instance['messages']):
                            if message['author'] != last_author:
                                new_messages.append(message)
                                last_author = message['author']
                        new_instance['messages'] = list(reversed(new_messages))
                    new_instances.append(new_instance)
                request['instances'] = new_instances
        else:
            # Messages must be USER, AI, USER, AI.. etc, so filter them
            # to make life easier.
            if 'contents' in request:
                new_contents = []
                last_role = None
                for content in list(reversed(request['contents'])):
                    if not last_role:
                        last_role = content['role']
                        new_contents.insert(0, content)
                    else:
                        if content['role'] != last_role:
                            new_contents.insert(0, content)
                        last_role = content['role']
                request['contents'] = new_contents

        self.logger.debug('Calling Vertex AI %s' % (method),
                          extra={
                              'request_body': request,
                              'api_url': api_path
                          })

        request_body = json.dumps(request)
        authed_session = AuthorizedSession(credentials)
        response = authed_session.post(api_path,
                                       data=request_body,
                                       headers=headers)
        try:
            response.raise_for_status()
        except Exception as e:
            if return_errors:
                response_json = response.json()
                for err in response_json:
                    if 'error' in err and 'message' in err['error']:
                        return {
                            output_var: {
                                'error': response_json['error']['message']
                            }
                        }
            self.logger.error('Error calling %s: %s' % (e.request.url, e),
                              extra={'response': e.response.text})
            raise e
        response_json = response.json()
        return {
            output_var: response_json,
        }

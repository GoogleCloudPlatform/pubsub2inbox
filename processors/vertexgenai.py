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
import google.oauth2.id_token
from google.auth.transport.requests import AuthorizedSession
import urllib


class VertexgenaiProcessor(Processor):
    """
    Vertex AI Generative AI processor.

    Args:
        region (str): Endpoint to use.
        modelId (str): Deployed model to use.
        project (str, optional): Google Cloud project ID.
        method (str, optional): Method to call, by default: "predict"
        returnErrors (bool, optional): Set to true to return errors
        callFunctions (dict, optional): URLs for functions.
        request (dict): Request.
    """

    def get_default_config_key():
        return 'vertexgenai'

    def call_function(self, name, params):
        method = 'GET'
        if 'method' in params:
            method = params['method'].upper()
        headers = {}
        if 'headers' in params:
            for header in params['headers']:
                headers[header['name'].lower()] = header['value']
        body = ''
        if 'body' in params:
            if isinstance(params['body'], dict):
                body = json.dumps(params['body'])
            else:
                body = params['body']
        loggable_headers = headers
        if 'authorization' in loggable_headers:
            del loggable_headers['authorization']
        if 'x-serverless-authorization' in loggable_headers:
            del loggable_headers['x-serverless-authorization']
        if 'api-key' in loggable_headers:
            del loggable_headers['api-key']
        if 'x-api-key' in loggable_headers:
            del loggable_headers['x-api-key']
        if 'proxy-authorization' in loggable_headers:
            del loggable_headers['proxy-authorization']

        self.logger.info('Calling function: %s' % (name),
                         extra={
                             'url': params['url'],
                             'method': method,
                             'body_length': len(body),
                             'headers': loggable_headers,
                             'id_token': True if 'idToken' in params else False
                         })

        id_token = None
        audience = None
        if 'idToken' in params and params['idToken']:
            if 'audience' in params:
                audience = params['audience']
            else:
                audience = params['url']
            auth_request = google.auth.transport.requests.Request()
            id_token = google.oauth2.id_token.fetch_id_token(
                auth_request, audience)
            headers['authorization'] = 'Bearer %s' % (id_token)

        req = urllib.request.Request(params['url'],
                                     headers=headers,
                                     method=method)
        response = urllib.request.urlopen(req, data=body.encode('utf-8'))
        if response.status < 200 or response.status >= 400:
            self.logger.error('Error calling function: %s' % (name),
                              extra={
                                  'status_code': response.status,
                                  'response': response.data.decode('utf-8')
                              })

        return (response.headers, json.loads(response.read().decode('utf-8')))

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
                        return {output_var: {'error': err['error']['message']}}
            self.logger.error('Error calling %s: %s' % (e.request.url, e),
                              extra={'response': e.response.text})
            raise e
        response_json = response.json()

        # Check if functions need to be called
        if 'callFunctions' in self.config:
            function_calls = {}
            function_contents = {}
            for response in response_json:
                if 'candidates' in response:
                    for candidate in response['candidates']:
                        if 'content' in candidate:
                            if 'parts' in candidate['content']:
                                parts = candidate['content']['parts']
                                for part in parts:
                                    if 'functionCall' in part:
                                        function_name = part['functionCall'][
                                            'name']
                                        function_contents[
                                            function_name] = candidate[
                                                'content']
                                        args = part['functionCall'][
                                            'args'] if 'args' in part[
                                                'functionCall'] else {}
                                        self.logger.info(
                                            'Vertex wants us to call function %s.'
                                            % (function_name),
                                            extra={'function_args': args})
                                        function_calls[function_name] = args
                            else:
                                self.logger.warn(
                                    'No parts in Vertex response candidate content.',
                                    extra={'candidate': candidate})
                        else:
                            self.logger.warn(
                                'No content in Vertex response candidate.',
                                extra={'candidate': candidate})
                else:
                    self.logger.warn('No candidates in Vertex response.',
                                     extra={'response_part': response})
            function_responses = {}
            jinja_globals = self.jinja_environment.globals
            for name, args in function_calls.items():
                for k, v in args.items():
                    self.jinja_environment.globals[k] = v
                    defined_functions = self._jinja_expand_dict_all(
                        self.config['callFunctions'], 'call_functions')
                    if name in defined_functions:
                        function_responses[name] = self.call_function(
                            name, defined_functions[name])
                    else:
                        self.logger.error(
                            'No function configuration specified for: %s' %
                            (name),
                            extra={'function_name': name})
            if len(function_responses) > 0:
                self.jinja_environment.globals = jinja_globals
                for name, result in function_responses.items():
                    request['contents'].append(function_contents[name])
                    request['contents'].append({
                        'role':
                            'MODEL',
                        'parts': [{
                            'functionResponse': {
                                'name': name,
                                'response': result[1],
                            }
                        }]
                    })

                self.logger.debug(
                    'Re-doing Vertex request after adding function responses.',
                    extra={'request': request})

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
                                        'error': err['error']['message']
                                    }
                                }
                    self.logger.error('Error calling %s: %s' %
                                      (e.request.url, e),
                                      extra={'response': e.response.text})
                    raise e
                response_json = response.json()

        return {
            output_var: response_json,
        }

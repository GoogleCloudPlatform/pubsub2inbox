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
from helpers.base import get_user_agent
import json
import google.auth
from google.auth.transport.requests import AuthorizedSession


class VertexaiProcessor(Processor):
    """
    Vertex AI processor.

    Args:
        region (str): Endpoint to use.
        mode (str): search (Vertex AI Search)
        method (str, optional): Method to call (defaults to "search").
        project (str, optional): Google Cloud project ID.
        location (str): Location for Vertex AI.
        collection (str, optional): Collection (defaults to "default_collection")
        engineId (str): Engine ID.
        datastoreId (str): Data store ID (either this or engineId).
        servingConfig (str, optional): Serving configuration (defaults to "default_config").
        returnErrors (bool, optional): Set to true to return errors
        apiVersion (str, optional): API version, defaults to "v1".
        request (dict): Request.
    """

    def get_default_config_key():
        return 'vertexai'

    def process(self, output_var='vertexai'):
        if 'location' not in self.config:
            raise NotConfiguredException('No location specified specified.')
        if 'mode' not in self.config:
            raise NotConfiguredException('No mode specified.')
        if 'request' not in self.config:
            raise NotConfiguredException('No request specified.')
        credentials, credentials_project_id = google.auth.default()
        project = self.config[
            'project'] if 'project' in self.config else credentials_project_id
        if not project:
            project = credentials.quota_project_id

        mode = self._jinja_expand_string(self.config['mode'], 'mode')
        location = self._jinja_expand_string(self.config['location'],
                                             'location')
        collection = self._jinja_expand_string(
            self.config['collection'], 'collection'
        ) if 'collection' in self.config else 'default_collection'
        engine_id = None
        datastore_id = None
        if 'engineId' in self.config:
            engine_id = self._jinja_expand_string(self.config['engineId'],
                                                  'engine_id')
        else:
            datastore_id = self._jinja_expand_string(self.config['datastoreId'],
                                                     'datastore_id')
        serving_config = self._jinja_expand_string(
            self.config['servingConfig'], 'serving_config'
        ) if 'servingConfig' in self.config else 'default_config'

        api_version = self._jinja_expand_string(self.config['apiVersion']) if 'apiVersion' in self.config else 'v1'

        method = self._jinja_expand_string(
            self.config['method'],
            'method') if 'method' in self.config else 'search'
        if mode == 'search':
            if engine_id:
                api_path = 'https://%s-discoveryengine.googleapis.com/%s/projects/%s/locations/%s/collections/%s/engineId/%s/servingConfigs/%s:%s' % (
                    api_version, location, project, location, collection, engine_id,
                    serving_config, method)
            else:
                api_path = 'https://%s-discoveryengine.googleapis.com/%s/projects/%s/locations/%s/collections/%s/dataStores/%s/servingConfigs/%s:%s' % (
                    location, api_version, project, location, collection, datastore_id,
                    serving_config, method)

            return_errors = False
            if 'returnErrors' in self.config:
                return_errors = self._jinja_expand_bool(
                    self.config['returnErrors'], 'return_errors')

            request = self._jinja_expand_dict_all_expr(self.config['request'],
                                                       'request')
            headers = {
                'User-Agent': get_user_agent(),
                'Content-type': 'application/json; charset=utf-8',
            }

            self.logger.debug('Calling Vertex AI %s:%s' % (mode, method),
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
                        if isinstance(
                                err, dict
                        ) and 'error' in err and 'message' in err['error']:
                            return {
                                output_var: {
                                    'error': err['error']['message']
                                }
                            }
                self.logger.error('Error calling %s: %s' % (e.request.url, e),
                                  extra={'response': e.response.text})
                raise e

            response_json = response.json()
        return {
            output_var: response_json,
        }

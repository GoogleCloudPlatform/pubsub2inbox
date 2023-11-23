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
from googleapiclient import discovery


class LoggingProcessor(Processor):
    """
    Fetch logging information from Cloud Logging.

    Args:
        project (str, optional): Google Cloud project ID.
        resourceNames (list): Parent resources to fetch logging entries from.
        filter (str, optional): Logging filter.
        orderBy (str, optional): How to order log entries.
        format (str, optional): One of: full, text-only, with-timestamps (default full)
        mode (str): One of: entries.list
    """

    def get_default_config_key():
        return 'logging'

    def process(self, output_var='logging'):
        if 'mode' not in self.config:
            raise NotConfiguredException(
                'No Cloud Logging operation specified.')
        if 'resourceNames' not in self.config:
            raise NotConfiguredException(
                'No Cloud Logging resource names specified.')

        credentials, credentials_project_id = google.auth.default()
        project = self._jinja_expand_string(
            self.config['project'],
            'project') if 'project' in self.config else credentials_project_id
        if not project:
            project = credentials.quota_project_id

        logging_service = discovery.build(
            'logging', 'v2', http=self._get_branded_http(credentials))

        resource_names = self._jinja_expand_list(self.config['resourceNames'])
        log_filter = self._jinja_expand_string(
            self.config['filter']) if 'filter' in self.config else ''
        order_by = self._jinja_expand_string(
            self.config['orderBy']
        ) if 'orderBy' in self.config else 'timestamp asc'

        if self.config['mode'] == 'logging.entries':
            request_params = {
                "resourceNames": resource_names,
                "filter": log_filter,
                "orderBy": order_by,
            }
            msg_format = self._jinja_expand_string(
                self.config['format']) if 'format' in self.config else 'full'
            ret = []
            while True:
                log_request = logging_service.entries().list(
                    body=request_params)
                log_response = log_request.execute()
                if 'entries' in log_response:
                    if msg_format == 'text-only' or msg_format == 'with-timestamps':
                        for entry in log_response['entries']:
                            if 'textPayload' in entry:
                                if msg_format == 'with-timestamps':
                                    ret.append('%s %s' %
                                               (entry['receiveTimestamp'],
                                                entry['textPayload']))
                                else:
                                    ret.append(entry['textPayload'])
                    else:
                        ret += log_response['entries']
                if 'nextPageToken' in log_response:
                    request_params['pageToken'] = log_response['nextPageToken']
                else:
                    break
            return {output_var: ret}

        return {output_var: None}

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
from .base import Output, NotConfiguredException


class HttpresponseOutput(Output):

    def output(self):
        if 'statusCode' not in self.output_config:
            raise NotConfiguredException(
                'No HTTP status code defined in configuration.')
        if 'headers' not in self.output_config:
            raise NotConfiguredException(
                'No HTTP response headers defined in configuration.')
        if 'body' not in self.output_config:
            raise NotConfiguredException(
                'No HTTP response body defined in configuration.')

        status_code = self._jinja_expand_int(self.config['statusCode'],
                                             'status_code')
        headers = self._jinja_expand_dict_all(self.config['headers'], 'headers')
        body = self._jinja_expand_string(self.config['body'], 'body')

        self.outputHttpResponse(status_code, headers, body)
        self.logger.info('HTTP response sent.',
                         extra={
                             'status': status_code,
                             'headers': headers,
                             'body_length': len(body)
                         })

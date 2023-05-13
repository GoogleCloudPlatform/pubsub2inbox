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
import json


class SetvariableProcessor(Processor):
    """
    Outputs the contents of value. Control the execution via `runIf` and 
    the variable set with output.

    Args:
        value (any): Value to set.
        fromJson (bool, optional): Convert value from JSON.
    """

    def get_default_config_key():
        return 'variable'

    def process(self, output_var='variable'):
        if 'value' not in self.config:
            raise NotConfiguredException('Value or expression not specified.')

        result_var = None
        if isinstance(self.config['value'], dict):
            result_var = self._jinja_expand_dict_all(self.config['value'],
                                                     'value')
        elif isinstance(self.config['value'], list):
            result_var = self._jinja_expand_list(self.config['value'], 'value')
        elif isinstance(self.config['value'], int):
            result_var = self._jinja_expand_int(self.config['value'], 'value')
        else:
            result_var = self._jinja_expand_string(self.config['value'],
                                                   'value')
        from_json = False
        if 'fromJson' in self.config:
            from_json = self._jinja_expand_bool(self.config['fromJson'],
                                                'from_json')
        if from_json:
            result_var = json.loads(result_var)
        self.logger.debug('Variable set by setvariable',
                          extra={
                              'output_variable': output_var,
                              'output_value': result_var
                          })
        return {
            output_var: result_var,
        }

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


class SetvariableProcessor(Processor):
    """
    Outputs the contents of value. Control the execution via `runIf` and 
    the variable set with output.

    Args:
        value (any): Value to set.
    """

    def get_default_config_key():
        return 'variable'

    def process(self, output_var='variable'):
        if 'value' not in self.config:
            raise NotConfiguredException('Value not specified.')

        if isinstance(self.config['value'], dict):
            return {
                output_var:
                    self._jinja_expand_dict_all(self.config['value'], 'value')
            }
        elif isinstance(self.config['value'], list):
            return {
                output_var:
                    self._jinja_expand_list(self.config['value'], 'value')
            }
        elif isinstance(self.config['value'], int):
            return {
                output_var:
                    self._jinja_expand_int(self.config['value'], 'value')
            }

        return {
            output_var: self._jinja_expand_string(self.config['value'], 'value')
        }

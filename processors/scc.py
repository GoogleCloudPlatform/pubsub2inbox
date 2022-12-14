#   Copyright 2021 Google LLC
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
from .base import Processor
import json


class SccProcessor(Processor):

    def get_default_config_key():
        return 'scc'

    def process(
        self,
        output_var={
            'organization': 'organization',
            'projects': 'projects',
            'finding': 'finding'
        }):
        data = json.loads(self.data)
        projects = []
        if 'sourceProperties' in data['finding'] and 'ResourcePath' in data[
                'finding']['sourceProperties']:
            projects = self.expand_projects(
                data['finding']['sourceProperties']['ResourcePath'])
        organization = data['notificationConfigName'].split('/')[1]
        return {
            output_var['organization']: organization,
            output_var['projects']: projects,
            output_var['finding']: data['finding'],
        }

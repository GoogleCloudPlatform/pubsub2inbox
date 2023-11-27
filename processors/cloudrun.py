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


class CloudrunProcessor(Processor):
    """
    Fetches information and performs actions on Cloud Run (mainly Cloud Run Jobs).

    Args:
        project (str, optional): Google Cloud project ID.
        location (str): Cloud Run location.
        job (str, optional): Cloud Run Job name.
        execution (str, optional): Cloud Run Job execution.
        task (str, optional): Cloud Run Job execution task.
        mode (str): One of: jobs.executions.list, jobs.executions.get, jobs.executions.cancel, 
            jobs.run
    """

    def get_default_config_key():
        return 'cloudrun'

    def process(self, output_var='cloudrun'):
        if 'mode' not in self.config:
            raise NotConfiguredException('No Cloud Run operation specified.')
        if 'location' not in self.config:
            raise NotConfiguredException('No Cloud Run location specified.')

        credentials, credentials_project_id = google.auth.default()
        project = self._jinja_expand_string(
            self.config['project'],
            'project') if 'project' in self.config else credentials_project_id
        if not project:
            project = credentials.quota_project_id

        run_service = discovery.build('run',
                                      'v2',
                                      http=self._get_branded_http(credentials))

        location = self._jinja_expand_string(self.config['location'])
        job = self._jinja_expand_string(self.config['job'])

        if self.config['mode'] == 'jobs.executions.list':
            parent = f"projects/{project}/locations/{location}/jobs/{job}"
            request_params = {"parent": parent}
            ret = []
            while True:
                run_request = run_service.projects().locations().jobs(
                ).executions().list(**request_params)
                run_response = run_request.execute()
                if 'executions' in run_response:
                    ret += run_response['executions']
                if 'nextPageToken' in run_response:
                    request_params['pageToken'] = run_response['nextPageToken']
                else:
                    break
            return {output_var: ret}

        if self.config['mode'] == 'jobs.executions.get':
            execution = self._jinja_expand_string(self.config['execution'])
            name = f"projects/{project}/locations/{location}/jobs/{job}/executions/{execution}"
            run_request = run_service.projects().locations().jobs().executions(
            ).get(name=name)
            run_response = run_request.execute()
            return {output_var: run_response}

        if self.config['mode'] == 'jobs.executions.cancel':
            execution = self._jinja_expand_string(self.config['execution'])
            name = f"projects/{project}/locations/{location}/jobs/{job}/executions/{execution}"
            run_request = run_service.projects().locations().jobs().executions(
            ).cancel(name=name, body={"validateOnly": False})
            run_response = run_request.execute()
            return {output_var: run_response}

        if self.config['mode'] == 'jobs.run':
            name = f"projects/{project}/locations/{location}/jobs/{job}"
            overrides = {}
            if 'overrides' in self.config:
                overrides = self._jinja_expand_dict_all(self.config['overrides'])
            request_body = {
                'validateOnly': False,
                'overrides': overrides,
            }
            run_request = run_service.projects().locations().jobs().run(name=name, body=request_body)
            run_response = run_request.execute()
            return {output_var: run_response}

        return {output_var: None}

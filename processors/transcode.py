#   Copyright 2022 Google LLC
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
from googleapiclient import discovery
import google.auth


class InvalidModeException(Exception):
    pass


class TranscodeProcessor(Processor):
    """
    Transcode media using Transcoder API. For more information, see: 
    https://cloud.google.com/transcoder/docs

    Args:
        mode (enum, optional): Select mode: create (creates a new job), get (gets existing job)
        project (str, optional): Google Cloud project ID.
        location (str): Processing location (eg. "europe-west4")
        job (dict): Transcoding job configuration.
    """

    def get_default_config_key():
        return 'transcode'

    def process(self, output_var='transcode'):
        mode = 'create'
        if 'mode' in self.config:
            if self.config['mode'] not in ['create', 'get']:
                raise InvalidModeException('Unknown transcoder mode: %s' %
                                           (self.config['mode']))
            mode = self.config['mode']

        if 'job' not in self.config:
            raise NotConfiguredException(
                'No transcode job configuration specified.')
        if 'location' not in self.config:
            raise NotConfiguredException(
                'No location specified for transcode job.')
        location = self._jinja_expand_string(self.config['location'],
                                             'location')

        credentials, credentials_project_id = google.auth.default()
        project = self.config[
            'project'] if 'project' in self.config else credentials_project_id
        if not project:
            project = credentials.quota_project_id

        project_number = self.get_project_number(project)

        job = self._jinja_expand_dict_all(self.config['job'], 'job')

        transcoder_service = discovery.build(
            'transcoder',
            'v1',
            discoveryServiceUrl=
            'https://transcoder.googleapis.com/$discovery/rest?version=v1',
            http=self._get_branded_http(credentials))
        job_response = None
        if mode == 'create':
            job_request = transcoder_service.projects().locations().jobs(
            ).create(parent="projects/%s/locations/%s" %
                     (project_number, location),
                     body=job)
            job_response = job_request.execute()
        elif mode == 'get':
            if 'name' not in job:
                raise NotConfiguredException(
                    'No job name specified in job configuration.')

            job_name = job['name'] if "projects/" in job[
                'name'] else "projects/%s/locations/%s/%s" % (
                    project_number, location, job['name'])
            job_request = transcoder_service.projects().locations().jobs().get(
                name=job_name)
            job_response = job_request.execute()

        return {
            output_var: job_response,
        }

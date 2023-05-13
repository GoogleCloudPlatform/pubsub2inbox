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
import logging
import os
import re
import json
from google.cloud.iam_credentials_v1 import IAMCredentialsClient
from google.api_core.gapic_v1 import client_info as grpc_client_info
import google_auth_httplib2
import google.auth
from googleapiclient import http
from google.cloud import resourcemanager_v3
import json_fix  # noqa: F401
import tempfile

PUBSUB2INBOX_VERSION = '1.7.0'
TEMPORARY_DIRECTORY = None


class NoCredentialsException(Exception):
    pass


class Context(object):

    def __init__(self, eventId="", timestamp="", eventType="", resource=""):
        self.event_id = eventId
        self.timestamp = timestamp
        self.event_type = eventType
        self.resource = resource

    def __json__(self):
        return "{\"event_id\": \"%s\", \"timestamp\": \"%s\", \"event_type\": \"%s\", \"resource\": \"%s\"}" % (
            self.event_id,
            self.timestamp,
            self.event_type,
            self.resource,
        )

    def __str__(self):
        return "{event_id: %s, timestamp: %s, event_type: %s, resource: %s}" % (
            self.event_id,
            self.timestamp,
            self.event_type,
            self.resource,
        )


def get_user_agent():
    return 'google-pso-tool/pubsub2inbox/%s' % (PUBSUB2INBOX_VERSION)


def get_branded_http(credentials=None):
    if not credentials:
        credentials, project_id = google.auth.default(
            ['https://www.googleapis.com/auth/cloud-platform'])
    branded_http = google_auth_httplib2.AuthorizedHttp(credentials)
    branded_http = http.set_user_agent(branded_http, get_user_agent())
    return branded_http


def get_grpc_client_info():
    client_info = grpc_client_info.ClientInfo(user_agent=get_user_agent())
    return client_info


class BaseHelper:
    logger = None
    jinja_environment = None
    project_number_cache = {}

    def __init__(self, jinja_environment):
        self.jinja_environment = jinja_environment
        self.logger = logging.getLogger('pubsub2inbox')

    def _init_tempdir(self):
        global TEMPORARY_DIRECTORY
        if not TEMPORARY_DIRECTORY:
            TEMPORARY_DIRECTORY = tempfile.TemporaryDirectory()
            self.logger.debug('Created temporary directory: %s' %
                              (TEMPORARY_DIRECTORY.name))
            os.chdir(TEMPORARY_DIRECTORY.name)

    def _clean_tempdir(self):
        global TEMPORARY_DIRECTORY
        if TEMPORARY_DIRECTORY:
            self.logger.debug('Cleaning temporary directory: %s' %
                              (TEMPORARY_DIRECTORY.name))
            TEMPORARY_DIRECTORY = None

    def _get_user_agent(self):
        return get_user_agent()

    def _get_branded_http(self, credentials=None):
        return get_branded_http(credentials)

    def _get_grpc_client_info(self):
        return get_grpc_client_info()

    def get_project_number(self, project_id, credentials=None):
        if project_id in self.project_number_cache:
            return self.project_number_cache[project_id]

        client = resourcemanager_v3.ProjectsClient(credentials=credentials)
        request = resourcemanager_v3.SearchProjectsRequest(
            query="projectId=%s" % (project_id),)
        response = client.search_projects(request=request)
        project = next(iter(response))
        if project:
            self.project_number_cache[project_id] = int(
                project.name.replace("projects/", ""))
            return self.project_number_cache[project_id]
        return None

    def get_token_for_scopes(self, scopes, service_account=None):
        if not service_account:
            service_account = os.getenv('SERVICE_ACCOUNT')

        if not service_account:
            raise NoCredentialsException(
                'You need to specify a service account for Directory API credentials, either through SERVICE_ACCOUNT environment variable or serviceAccountEmail parameter.'
            )

        client = IAMCredentialsClient()
        name = 'projects/-/serviceAccounts/%s' % service_account
        response = client.generate_access_token(name=name, scope=scopes)
        return response.access_token

    def _jinja_expand_expr(self, contents, _tpl='config'):
        expr = self.jinja_environment.compile_expression(contents,
                                                         undefined_to_none=True)
        return expr()

    def _jinja_expand_bool(self, contents, _tpl='config'):
        if isinstance(contents, bool):
            return contents
        var_template = self.jinja_environment.from_string(contents)
        var_template.name = _tpl
        val_str = var_template.render().lower()
        if val_str == 'true' or val_str == 't' or val_str == 'yes' or val_str == 'y' or val_str == '1':
            return True
        return False

    def _jinja_expand_string(self, contents, _tpl='config'):
        var_template = self.jinja_environment.from_string(contents)
        var_template.name = _tpl
        val_str = var_template.render()
        return val_str

    def _jinja_expand_int(self, contents, _tpl='config'):
        if isinstance(contents, int):
            return contents
        if isinstance(contents, float):
            return int(contents)
        var_template = self.jinja_environment.from_string(contents)
        var_template.name = _tpl
        val_str = var_template.render()
        return int(val_str)

    def _jinja_expand_float(self, contents, _tpl='config'):
        if isinstance(contents, float):
            return contents
        var_template = self.jinja_environment.from_string(contents)
        var_template.name = _tpl
        val_str = var_template.render()
        return float(val_str)

    def _jinja_var_to_list(self, _var, _tpl='config'):
        if isinstance(_var, list):
            return _var
        else:
            var_template = self.jinja_environment.from_string(_var)
            var_template.name = _tpl
            val_str = var_template.render()
            try:
                return json.loads(val_str)
            except Exception:
                self.logger.debug(
                    'Error parsing variable to list, trying command or CR separated.',
                    extra={
                        'template': _var,
                        'value': val_str
                    })
                vals = list(
                    filter(
                        lambda x: x.strip() != "",
                        re.split('[\n,]', val_str),
                    ))
                return list(map(lambda x: x.strip(), vals))

    def _jinja_var_to_list_all(self, _var, _tpl='config'):
        if isinstance(_var, list):
            return self._jinja_expand_list(_var, _tpl)
        else:
            var_template = self.jinja_environment.from_string(_var)
            var_template.name = _tpl
            val_str = var_template.render()
            try:
                return json.loads(val_str)
            except Exception:
                self.logger.debug(
                    'Error parsing variable to list, trying command or CR separated.',
                    extra={
                        'template': _var,
                        'value': val_str
                    })
                vals = list(
                    filter(
                        lambda x: x.strip() != "",
                        re.split('[\n,]', val_str),
                    ))
                return list(map(lambda x: x.strip(), vals))

    def _jinja_expand_dict(self, _var, _tpl='config'):
        for k, v in _var.items():
            if not isinstance(v, dict):
                if isinstance(v, str):
                    _var[k] = self._jinja_expand_string(v)
            else:
                _var[k] = self._jinja_expand_dict(_var[k])
        return _var

    def _jinja_expand_dict_all(self, _var, _tpl='config'):
        if not isinstance(_var, dict):
            return _var
        for k, v in _var.items():
            if not isinstance(v, dict):
                if isinstance(v, str):
                    _var[k] = self._jinja_expand_string(v)
                if isinstance(v, list):
                    for idx, lv in enumerate(_var[k]):
                        if isinstance(lv, dict):
                            _var[k][idx] = self._jinja_expand_dict_all(lv)
                        if isinstance(lv, str):
                            _var[k][idx] = self._jinja_expand_string(lv)
            else:
                _var[k] = self._jinja_expand_dict_all(_var[k])
        return _var

    def _jinja_expand_dict_all_expr(self, _var, _tpl='config'):
        _new_var = {}
        if not isinstance(_var, dict):
            return _var
        for k, v in _var.items():
            if not isinstance(v, dict):
                if isinstance(v, str):
                    if k.endswith('Expr'):
                        _new_var[k[0:len(k) - 4]] = self._jinja_expand_expr(v)
                    else:
                        _new_var[k] = self._jinja_expand_string(v)
                if isinstance(v, int):
                    _new_var[k] = self._jinja_expand_int(v)
                if isinstance(v, float):
                    _new_var[k] = self._jinja_expand_float(v)
                if isinstance(v, list):
                    _new_var[k] = []
                    for idx, lv in enumerate(_var[k]):
                        if isinstance(lv, dict):
                            _new_var[k].append(
                                self._jinja_expand_dict_all_expr(lv))
                        if isinstance(lv, str):
                            _new_var[k].append(self._jinja_expand_string(lv))
            else:
                _new_var[k] = self._jinja_expand_dict_all_expr(_var[k])
        return _new_var

    def _jinja_expand_list(self, _var, _tpl='config'):
        if not isinstance(_var, list):
            return _var
        for idx, v in enumerate(_var):
            if isinstance(v, str):
                _var[idx] = self._jinja_expand_string(v)
        return _var

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
from .base import Output, NotConfiguredException
from googleapiclient import discovery
from google.oauth2.credentials import Credentials


class ChatOutput(Output):
    """
    Sends message to a Google Chat space.

    Args:
        serviceAccountEmail (str): A service account email for which a scoped token will be requested. 
          You should invite this service account to the space. The Cloud Functions has to has Service 
          Account Token Creator to this service account. Can also be specified via SERVICE_ACCOUNT 
          environment variable.
        parent (str): A Google Chat space (spaces/XYZ).
        message (dict): A Message object (see: https://developers.google.com/chat/api/reference/rest/v1/spaces.messages#Message).
        project (str, optional): Google Cloud project to issue Chat API calls against.
    """

    def output(self):
        if 'parent' not in self.output_config:
            raise NotConfiguredException('No target space configured!')

        chat_parent = self._jinja_expand_string(self.output_config['parent'],
                                                'parent')

        chat_body = self._jinja_expand_dict_all(self.output_config['message'],
                                                'message')

        service_account = self._jinja_expand_string(
            self.output_config['serviceAccountEmail'], 'service_account'
        ) if 'serviceAccountEmail' in self.output_config else None

        scope = 'https://www.googleapis.com/auth/chat.messages'
        credentials = Credentials(
            self.get_token_for_scopes([scope], service_account=service_account))
        branded_http = self._get_branded_http(credentials)

        chat_service = discovery.build('chat', 'v1', http=branded_http)
        chat_response = chat_service.spaces().messages().create(
            parent=chat_parent, body=chat_body).execute()

        self.logger.debug('Chat message sent to: %s' % (chat_parent),
                          extra={
                              "response": chat_response,
                              "chat_message": chat_body
                          })

        # Redact message contents from response for logging
        if 'argumentText' in chat_response:
            del chat_response['argumentText']
        if 'text' in chat_response:
            del chat_response['text']
        if 'cardsV2' in chat_response:
            del chat_response['cardsV2']

        self.logger.info('Chat message sent to: %s' % (chat_parent),
                         extra={
                             "response": chat_response,
                         })

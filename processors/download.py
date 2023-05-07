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
import urllib
import os
import paramiko
from io import StringIO
import base64


class DownloadProcessor(Processor):
    """
    Downloads files to "local filesystem". Supports: HTTP, HTTPS, FTP, SFTP.

    Args:
        url (str): URL to download.
        filename (str, optional): Filename to save.
        strip (int, optional): Strip N components from the save path.
        body (str, optional): Specify request body to issue a POST call.
        headers (dict, optional): Specify request headers.
        privateKey (dict, optional): Private key for SFTP (keys: key, type (rsa, ecdsa, ed25519), passphrase (optional))
        hostKey (dict, optional): Remote host public key, otherwise auto-accept (keys: hostname, keytype, key)
    """

    def get_default_config_key():
        return 'download'

    def process(self, output_var='download'):
        if 'url' not in self.config:
            raise NotConfiguredException('No URL configured!')

        url = self._jinja_expand_string(self.config['url'], 'url')
        parsed_url = urllib.parse.urlparse(url)
        if 'filename' not in self.config:
            filename = urllib.parse.unquote_plus(parsed_url.path).lstrip('/')
        else:
            filename = self._jinja_expand_string(self.config['filename'],
                                                 'filename').lstrip('/')

        self._init_tempdir()
        directory = os.path.dirname(filename)
        if 'strip' in self.config:
            strip_components = self._jinja_expand_int(self.config['strip'],
                                                      'strip')
            path_parts = os.path.split(filename)
            path_components = path_parts[0].split(os.sep)
            directory = os.sep.join(path_components[strip_components:])
            filename = path_parts[1]
            self.logger.debug('Removed %d path parts, saving file to: %s/%s' %
                              (strip_components, directory, filename))

        if directory and not os.path.exists(directory):
            self.logger.debug(
                'Creating directory under temporary directory: %s' %
                (directory))
            os.makedirs(directory, exist_ok=True)

        self.logger.info('Downloading from %s to %s' % (url, filename),
                         extra={
                             'url': url,
                             'file_name': filename
                         })

        if parsed_url.scheme != 'sftp':
            request_body = None
            if 'body' in self.config:
                request_body = self._jinja_expand_string(
                    self.config['body'], 'body')

            if 'headers' in self.config:
                request_headers = self._jinja_expand_dict(
                    self.config['headers'], 'headers')
                opener = urllib.request.build_opener()
                for k, v in request_headers.items():
                    opener.addheaders.append((k, v))
                urllib.request.install_opener(opener)

            local_filename, headers = urllib.request.urlretrieve(
                url,
                filename=filename,
                data=request_body,
            )

            response_headers = {}
            for k, v in headers.items():
                if k.lower() != 'set-cookie':
                    response_headers[k] = v
            file_stats = os.stat(local_filename)
            output = {
                'filename': local_filename,
                'headers': response_headers,
                'size': file_stats.st_size,
            }
        else:
            ssh_client = paramiko.SSHClient()
            if 'hostKey' not in self.config:
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            else:
                host_key = self._jinja_expand_dict(self.config['hostKey'],
                                                   'host_key')

                self.logger.debug('Enforcing host key.', extra=host_key)

                if host_key['keytype'] == 'rsa':
                    host_key_obj = paramiko.RSAKey(
                        data=base64.b64decode(host_key['key']))
                elif host_key['keytype'] == 'ed25519':
                    host_key_obj = paramiko.Ed25519Key(
                        data=base64.b64decode(host_key['key']))
                elif host_key['keytype'] == 'ecdsa':
                    host_key_obj = paramiko.ECDSAKey(
                        data=base64.b64decode(host_key['key']))

                ssh_client.get_host_keys().add(hostname=host_key['host'],
                                               keytype=host_key['keytype'],
                                               key=host_key_obj)
            if parsed_url.username and parsed_url.password:
                ssh_client.connect(parsed_url.hostname,
                                   parsed_url.port,
                                   username=parsed_url.username,
                                   password=parsed_url.password)
            else:
                if 'privateKey' not in self.config:
                    raise NotConfiguredException('No private key configured')

                private_key = self._jinja_expand_dict(self.config['privateKey'],
                                                      'private_key')
                ssh_key = None
                if 'passphrase' not in private_key:
                    private_key['passphrase'] = None
                if private_key['type'] == 'rsa':
                    ssh_key = paramiko.RSAKey.from_private_key(
                        StringIO(private_key['key']),
                        password=private_key['passphrase'])
                elif private_key['type'] == 'ecdsa':
                    ssh_key = paramiko.ECDSAKey.from_private_key(
                        StringIO(private_key['key']),
                        password=private_key['passphrase'])
                elif private_key['type'] == 'ed25519':
                    ssh_key = paramiko.Ed25519Key.from_private_key(
                        StringIO(private_key['key']),
                        password=private_key['passphrase'])
                if not ssh_key:
                    raise NotConfiguredException('Unknown SSH key type.')

                self.logger.debug(
                    'Connecting to %s:%s with username %s' %
                    (parsed_url.hostname, parsed_url.port, parsed_url.username),
                    extra={
                        'host': parsed_url.hostname,
                        'port': parsed_url.port,
                        'username': parsed_url.username
                    })

                ssh_client.connect(parsed_url.hostname,
                                   parsed_url.port,
                                   username=parsed_url.username,
                                   pkey=ssh_key,
                                   look_for_keys=False,
                                   allow_agent=False)

            sftp = paramiko.SFTPClient.from_transport(
                ssh_client.get_transport())

            sftp.get(filename, filename)

            sftp.close()
            ssh_client.close()

            file_stats = os.stat(filename)
            output = {
                'filename': filename,
                'headers': {},
                'size': file_stats.st_size,
            }

        return {
            output_var: output,
        }

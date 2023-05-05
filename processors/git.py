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
from git import Git, Repo
import os
import tempfile


class GitProcessor(Processor):
    """
    Clones Git repositories via HTTPS or SSH.

    Args:
        url (str): Repository URL to download.
        branch (str, optional): Branch to check out.
        directory (str, optional): Directory to clone into.
        depth (int, optional): Depth to check out.
    """

    def get_default_config_key():
        return 'git'

    def process(self, output_var='git'):
        if 'url' not in self.config:
            raise NotConfiguredException('No URL configured!')

        url = self._jinja_expand_string(self.config['url'], 'url')

        self._init_tempdir()

        if 'directory' in self.config:
            directory = self._jinja_expand_string(self.config['directory'],
                                                  'url')
            if directory and not os.path.exists(directory):
                self.logger.debug(
                    'Creating directory under temporary directory: %s' %
                    (directory))
                os.makedirs(directory, exist_ok=True)
        else:
            directory = './'

        clone_args = {}
        if 'depth' in self.config:
            clone_args['depth'] = self._jinja_expand_int(
                self.config['depth'], 'depth')
        self.logger.info('Cloning %s to %s' % (url, directory),
                         extra={
                             **{
                                 'url': url,
                                 'directory': directory
                             },
                             **clone_args
                         })

        if 'privateKey' in self.config:
            private_key = self._jinja_expand_dict(self.config['privateKey'],
                                                  'private_key')
            key_file = tempfile.TemporaryFile()
            key_file.write(private_key['key'].encode('utf-8'))
            git_ssh_cmd = 'ssh -i %s' % (key_file.name)
            with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
                repo = Repo.clone_from(url, directory, **clone_args)
        else:
            repo = Repo.clone_from(url, directory, **clone_args)

        if 'branch' in self.config:
            branch = self._jinja_expand_string(self.config['branch'], 'branch')
            repo.git.checkout(branch)

        output = {
            'branch': repo.active_branch.name,
            'commit': {
                'id':
                    repo.head.commit.hexsha,
                'author':
                    "%s <%s>" % (repo.head.commit.author.name,
                                 repo.head.commit.author.email),
                'timestamp':
                    repo.head.commit.committed_datetime.isoformat(),
                'message':
                    repo.head.commit.message,
            },
            'directory': directory,
        }

        return {
            output_var: output,
        }

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
from github import Github


class GithubProcessor(Processor):
    """
    Creates GitHub issues or comments.

    Args:
        githubToken (str): A token for accessing GitHub (note: you can use the secret processor to retrieve it from Secrets Manager).
        baseUrl (str, optional): GitHub URL (defaults to https://github.com)
        repository (str): GitHub repository to use.
        mode (str): One of: issues.list, issues.get, issues.create, comments.list, comments.get, comments.create.
        issueId (int, optional): Issue ID.
        commentId (int, optional): Comment ID.
        state (str, optional): Issue state.
    """

    def get_default_config_key():
        return 'github'

    def process(self, output_var='github'):
        if 'githubToken' not in self.config:
            raise NotConfiguredException('No GitHub token configured!')
        if 'mode' not in self.config:
            raise NotConfiguredException('No GitHub mode configured!')
        if 'repository' not in self.config:
            raise NotConfiguredException('No GitHub repository configured!')

        mode = self._jinja_expand_string(self.config['mode'], 'mode')

        github_token = self._jinja_expand_string(self.config['githubToken'],
                                                 'token')

        if 'baseUrl' in self.config:
            g = Github(self._jinja_expand_string(self.config['baseUrl'],
                                                 'base_url'),
                       login_or_token=github_token)
        else:
            g = Github(github_token)

        repository_name = self._jinja_expand_string(self.config['repository'],
                                                    'repository')

        repository = g.get_repo(repository_name)
        if not repository:
            self.logger.error('Failed to get repository %s!' %
                              (repository_name),
                              extra={'repository': repository_name})
            return

        github_output = None
        item_id = None
        if mode == 'issues.list':
            issue_state = 'open'
            if 'state' in self.config:
                issue_state = self._jinja_expand_string(self.config['state'],
                                                        'state')

            issues = repository.get_issues(state=issue_state)
            github_output = []
            for issue in issues:
                github_output.append(issue.raw_data)

        if mode == 'issues.get':
            item_id = self._jinja_expand_int(self.config['issueId'], 'id')
            issue = repository.get_issue(number=item_id)
            github_output = issue.raw_data

        if mode == 'issues.create':
            if 'issue' not in self.config:
                raise NotConfiguredException('No GitHub issue configured!')

            issue = self._jinja_expand_dict_all(self.config['issue'])
            created_issue = repository.create_issue(**issue)
            github_output = created_issue.raw_data

        if mode == 'comments.list':
            item_id = self._jinja_expand_int(self.config['issueId'], 'id')
            issue = repository.get_issue(number=item_id)
            comments = issue.get_comments()
            github_output = []
            for comment in comments:
                github_output.append(comment.raw_data)

        if mode == 'comments.get':
            item_id = self._jinja_expand_int(self.config['issueId'], 'id')
            comment_id = self._jinja_expand_int(self.config['commentId'], 'id')
            issue = repository.get_issue(number=item_id)
            comment = issue.get_comment(comment_id)
            github_output = comment.raw_data

        if mode == 'comments.create':
            item_id = self._jinja_expand_int(self.config['issueId'], 'id')
            issue = repository.get_issue(number=item_id)
            comment_body = self._jinja_expand_string(self.config['comment'],
                                                     'comment')
            comment = issue.create_comment(comment_body)
            github_output = comment.raw_data

        return {
            output_var: github_output,
        }

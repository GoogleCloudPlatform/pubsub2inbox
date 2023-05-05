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
import json
import yaml
import os
import subprocess
from io import StringIO
import csv


class CommandFailedException(Exception):
    pass


class ShellscriptProcessor(Processor):
    """
    Runs any shellscript as a command and exposes the output in Jinja.

    Args:
        command (str): Command to execute.
        args (list, optional): List of arguments.
        enviroment (dict, optional): Additional environment variables to set.
        stdin (str, optional): Contents to pass via stdin to the process.
        json (bool, optional): Interpret the output as JSON.
        jsonMultiline (bool, optional): Interpret the output as multiline JSON.
        yaml (bool, optional): Interpret the output as YAML.
        csv (bool, optional): Interpret the output as CSV.
        tsv (bool, optional): Interpret the output as TSV.
        exitcodes (list, optional): List of allowed exit codes that are interpreted as successful run.
    """

    def get_default_config_key():
        return 'shellscript'

    def process(self, output_var='shellscript'):
        shell_config = self.config
        if 'command' not in shell_config:
            raise NotConfiguredException('No executable command found!')

        if 'output' in shell_config:
            output_var = self._jinja_expand_string(shell_config['output'],
                                                   'output')

        command = self._jinja_expand_string(shell_config['command'], 'command')

        full_args = [command]
        if 'args' in shell_config:
            full_args.extend(
                self._jinja_var_to_list_all(shell_config['args'], 'args'))

        environment = {}
        if 'environment' in shell_config:
            environment = self._jinja_expand_dict(shell_config['environment'],
                                                  'env')

        stdin = None
        if 'stdin' in shell_config:
            stdin = self._jinja_expand_string(shell_config['stdin'], 'stdin')

        self.logger.info('Running shell script: %s' % (command),
                         extra={'arguments': full_args[1:]})

        result = subprocess.run(
            full_args,
            capture_output=True,
            input=stdin,
            text=True,
            env={
                **os.environ,
                **environment
            },
        )
        if ('exitcodes' in shell_config and
                result.returncode not in shell_config['exitcodes']) or (
                    'exitcodes' not in shell_config and result.returncode != 0):
            raise CommandFailedException(
                'Command %s failed with return code: %d, stderr=%s' %
                (command, result.returncode, result.stderr))
        data = None
        if 'jsonMultiline' in shell_config and shell_config['jsonMultiline']:
            data = []
            for result_line in result.stdout.split("\n"):
                if result_line != "":
                    try:
                        line_data = json.loads(result_line)
                    except Exception as e:
                        self.logger.error(
                            'Error parsing multiline JSON from stdout: %s' %
                            (result_line))
                        raise e
                    data.append(line_data)
        elif 'json' in shell_config and shell_config['json']:
            try:
                data = json.loads(result.stdout)
            except Exception as e:
                self.logger.error('Error parsing JSON from stdout: %s' %
                                  (result.stdout))
                raise e
        elif 'yaml' in shell_config and shell_config['yaml']:
            data = yaml.load(result.stdout, Loader=yaml.SafeLoader)
        elif ('csv' in shell_config and
              shell_config['csv']) or ('tsv' in shell_config and
                                       shell_config['tsv']):
            sf = StringIO(result.stdout)
            reader = csv.reader(sf,
                                delimiter=',' if 'csv' in shell_config and
                                shell_config['csv'] else "\t")
            data = []
            for row in reader:
                data.append(row)

        ret = {}
        ret[output_var] = {
            'parsed': data,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode,
        }
        return ret

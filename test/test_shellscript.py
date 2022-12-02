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
import main
import io
from contextlib import redirect_stdout
from .helpers import fixture_to_pubsub, load_config
import unittest
import logging
from processors import shellscript


class TestShellscript(unittest.TestCase):

    def test_shellscript_succeed(self):
        logger = logging.getLogger('test')
        logger.setLevel(logging.DEBUG)
        config = load_config('shellscript-success')
        data, context = fixture_to_pubsub('generic')

        buf = io.StringIO()
        with redirect_stdout(buf):
            main.decode_and_process(logger, config, data, context)

    def test_shellscript_fail(self):
        logger = logging.getLogger('test')
        logger.setLevel(logging.DEBUG)
        config = load_config('shellscript-fail')
        data, context = fixture_to_pubsub('generic')

        buf = io.StringIO()
        with redirect_stdout(buf):
            with self.assertRaises(shellscript.CommandFailedException):
                main.decode_and_process(logger, config, data, context)


if __name__ == '__main__':
    unittest.main()

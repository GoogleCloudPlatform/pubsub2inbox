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
import io
from contextlib import redirect_stdout
from .helpers import fixture_to_pubsub, load_config
import unittest
import logging
from gcp_storage_emulator.server import create_server
import os
import time


class TestResend(unittest.TestCase):

    def test_resend(self):
        logger = logging.getLogger('test')
        logger.setLevel(logging.DEBUG)

        # Start fake GCS server
        server = create_server("localhost",
                               9023,
                               in_memory=True,
                               default_bucket="resend-test-bucket")
        server.start()
        os.environ["STORAGE_EMULATOR_HOST"] = "http://localhost:9023"
        os.environ["GOOGLE_CLOUD_PROJECT"] = "fictional"

        config = load_config('resend')
        data, context = fixture_to_pubsub('generic')

        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                import main
                main.decode_and_process(logger, config, data, context)
                main.decode_and_process(logger, config, data, context)
                time.sleep(10)
                main.decode_and_process(logger, config, data, context)

            self.assertEqual("RUN\nRUN", buf.getvalue().rstrip())
        finally:
            server.stop()


if __name__ == '__main__':
    unittest.main()

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

all: requirements docs fmt

PIP_COMPILE ?= pip-compile
PYTHON ?= python3
YAPF ?= yapf
RUFF ?= ruff

.PHONY: docs test fmt check

requirements: requirements.txt

requirements.txt: requirements.txt.in
	$(PIP_COMPILE) --allow-unsafe --generate-hashes --output-file=requirements.txt --resolver=backtracking --unsafe-package=distribute --unsafe-package=pip --unsafe-package=setuptools requirements.txt.in

docs:
	cd docs && make markdown

check: lint test
	true

test: pytest gotest

pytest:
	$(PYTHON) -m unittest discover

gotest:
	cd cmd/json2pubsub && go test

fmt: 
	$(YAPF) --style google --recursive -i .

lint:
	$(RUFF) check --ignore E501,E741 --exclude '.*' --exclude '*.pyi' .

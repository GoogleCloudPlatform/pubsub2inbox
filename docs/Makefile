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
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SPHINXAPIDOC  ?= sphinx-apidoc
SOURCEDIR     = ..
BUILDDIR      = build
PIP           ?= pip

apidocs:
	$(SPHINXAPIDOC) -f --ext-autodoc "$(SOURCEDIR)" -o . $(SPHINXOPTS) $(O)

markdown: apidocs
	$(SPHINXBUILD) -b markdown -c . "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) 

.PHONY: apidocs markdown Makefile deps

all: markdown

deps:
	$(PIP) install Sphinx sphinx-markdown-builder sphinx-autodoc-typehints

%: Makefile
	$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

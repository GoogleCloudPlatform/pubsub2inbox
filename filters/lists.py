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
def split(s, sep, maxsplit=-1):
    return s.split(sep, maxsplit)


def index(l, from_index, to_index=None):
    if not to_index:
        return l[from_index]
    return l[from_index:to_index]


def merge_dict(d1, d2):
    return {**d1, **d2}

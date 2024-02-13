import json


def sorted_json_dumps(d):
    return json.dumps(d, sort_keys=True).encode("utf-8")

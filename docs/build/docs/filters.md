# filters package

## Submodules

## filters.date module


### _exception_ filters.date.InvalidDatetimeException()
Bases: `Exception`


### _exception_ filters.date.InvalidRecurringDateException()
Bases: `Exception`


### filters.date.recurring_date(event, now_date=None, strftime_format='%Y-%m-%d')

### filters.date.strftime(timestamp_string, strftime_format)

### filters.date.utc_strftime(timestamp_string, strftime_format)
## filters.gcp module


### filters.gcp.format_cost(cost, decimals=2)

### filters.gcp.get_cost(cost)

### filters.gcp.get_gcp_resource(resource, api_domain, api_endpoint, api_version='v1')
## filters.lists module


### filters.lists.index(l, from_index, to_index=None)

### filters.lists.merge_dict(d1, d2)

### filters.lists.split(s, sep, maxsplit=-1)
## filters.regex module


### filters.regex.regex_match(s, find)

### filters.regex.regex_replace(s, find, replace)

### filters.regex.regex_search(s, find)
## filters.strings module


### _exception_ filters.strings.InvalidSchemeSignedURLException()
Bases: `Exception`


### _exception_ filters.strings.InvalidSchemeURLException()
Bases: `Exception`


### _exception_ filters.strings.ObjectNotFoundException()
Bases: `Exception`


### filters.strings.add_links(s)

### filters.strings.b64decode(v)

### filters.strings.csv_encode(v, \*\*kwargs)

### filters.strings.filemagic(contents)

### filters.strings.generate_signed_url(url, expiration, \*\*kwargs)
Returns a signed URL to a GCS object. URL should be in format “gs://bucket/file”.


### filters.strings.hash_string(v, hash_type='md5')

### filters.strings.html_table_to_xlsx(s)

### filters.strings.json_decode(v)

### filters.strings.json_encode(v)

### filters.strings.ltrim(v)

### filters.strings.make_list(s)

### filters.strings.parse_string(v, spec)

### filters.strings.parse_url(v)

### filters.strings.re_escape(s)

### filters.strings.read_file(filename)

### filters.strings.read_file_b64(filename)

### filters.strings.read_gcs_object(url, start=None, end=None)

### filters.strings.rtrim(v)

### filters.strings.trim(v)

### filters.strings.urlencode(s)

### filters.strings.yaml_decode(v)

### filters.strings.yaml_encode(v)
## filters.tests module


### filters.tests.test_contains(l, i)
## Module contents


### filters.get_jinja_filters()

### filters.get_jinja_tests()

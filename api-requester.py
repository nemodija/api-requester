import os, sys, re, itertools, datetime, json
import requests
import yaml
import urllib.parse

"""
Read configuration
"""
if os.path.exists('config.yaml'):
    with open('config.yaml') as file:
        config = yaml.safe_load(file.read()) or {}
else:
    config = {}

"""
DEFINE
"""
protocol = config.get('protocol', 'http')
hostname = config.get('hostname', 'localhost')
base_url = "{}://{}".format(protocol, hostname)

result_parent_dir_path = config.get('result', {}).get('parent_dir_path', '.')
result_dir_prefix = config.get('result', {}).get('dir_prefix', 'result')
result_dir_suffix = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
result_dir_name = '{}_{}'.format(result_dir_prefix, result_dir_suffix)
result_dir_path = os.path.join(result_parent_dir_path, result_dir_name)

placeholder = config.get('placeholder', r'(:\w+)')

"""
Read request path
"""
request_path_file = config.get('request_path_file', './request_path.yaml')
if os.path.exists(request_path_file):
    with open(request_path_file) as file:
        request_path = yaml.safe_load(file.read()) or {}
else:
    request_path = {}

"""
Request
"""
for key in request_path.keys():
    for request_path in request_path.get(key):
        print(request_path)

        # Extraction of placeholders
        var_keys = re.findall(placeholder, request_path)
        variables = []
        for var_key in var_keys:
            variables.append(config.get('variables', {}).get(key, {}).get(var_key, []))
        print(variables)

        for val in list(itertools.product(*variables)):
            # Placeholder replacement
            replaced_request_path = request_path
            for i, var_key in enumerate(var_keys):
                replaced_request_path = replaced_request_path.replace(var_key, str(val[i]))
            url = urllib.parse.urljoin(base_url, replaced_request_path)

            # Create Resut Directory
            response_dir = os.path.join(result_dir_path, re.sub('^/', '', replaced_request_path))
            os.makedirs(response_dir, exist_ok=True)

            # Request
            response = requests.get(url)
            print('[{}] {}'.format(response.status_code, url))

            # Output for result
            with open(os.path.join(response_dir, str(response.status_code)), mode='w') as rt:
                try:
                    json.dump(json.loads(response.text), rt, ensure_ascii=False, indent=2, sort_keys=True)
                except json.JSONDecodeError as e:
                    rt.write(response.text)

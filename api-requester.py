import os, sys, re, itertools, datetime, json
import requests
import yaml
import urllib.parse
import argparse

"""
CommandLine Options
"""
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
args = parser.parse_args()

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
        request_paths = yaml.safe_load(file.read()) or {}
else:
    request_paths = {}

"""
Request
"""
for key in request_paths.keys():
    print("# {}".format(key))
    for request_path in request_paths.get(key):
        if args.verbose:
            print(request_path)

        # Extraction of placeholders
        var_keys = re.findall(placeholder, request_path)
        variables = {}
        for var_key in var_keys:
            variables[var_key] = (config.get('variables', {}).get(key, {}).get(var_key, []))
        if args.verbose:
            print(variables)

        if not list(itertools.product(*variables.values())):
            print('[{}] ({:>8.4f}) {}'.format('---', 0, request_path))

        for val in [dict(zip(variables.keys(), r)) for r in list(itertools.product(*variables.values()))]:
            # Placeholder replacement
            replaced_request_path = request_path
            for var_key in var_keys:
                replaced_request_path = replaced_request_path.replace(var_key, str(val[var_key]))
            url = urllib.parse.urljoin(base_url, replaced_request_path)

            # Create Resut Directory
            response_dir = os.path.join(result_dir_path, re.sub('^/', '', replaced_request_path))
            os.makedirs(response_dir, exist_ok=True)

            # Request
            response = requests.get(url)
            print('[{}] ({:>8.4f}) {}'.format(response.status_code, response.elapsed.total_seconds(), url))

            # Output for result
            with open(os.path.join(response_dir, str(response.status_code)), mode='w') as rt:
                try:
                    json.dump(json.loads(response.text), rt, ensure_ascii=False, indent=2, sort_keys=True)
                except json.JSONDecodeError as e:
                    rt.write(response.text)

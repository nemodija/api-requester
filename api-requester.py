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
Read request path list
"""
request_path_list = config.get('request_path_list', './request_path_list')
if not os.path.exists(request_path_list):
    sys.exit()

with open(request_path_list, 'r') as f:
    request_path = f.readline()
    while request_path:
        if re.match('^#', request_path):
            request_path = f.readline()
            continue
        
        print(request_path.strip())

        # プレースホルダ抽出
        var_keys = re.findall(placeholder, request_path.strip())
        variables = []
        for var_key in var_keys:
            variables.append(config.get('variables', {}).get(var_key, []))

        for val in list(itertools.product(*variables)):
            # プレースホルダ置換
            replaced_path = request_path.strip()
            for i, var_key in enumerate(var_keys):
                replaced_path = replaced_path.replace(var_key, str(val[i]))
            url = urllib.parse.urljoin(base_url, replaced_path)
            print(url)

            # Create Resut Directory
            response_dir = os.path.join(result_dir_path, re.sub('^/', '', replaced_path))
            #print(response_dir)
            os.makedirs(response_dir, exist_ok=True)

            # Request
            response = requests.get(url)
            
            # 結果出力
            with open(os.path.join(response_dir, str(response.status_code)), mode='w') as rt:
                try:
                    json.dump(json.loads(response.text), rt, ensure_ascii=False, indent=2, sort_keys=True)
                except json.JSONDecodeError as e:
                    rt.write(response.text)

        request_path = f.readline()

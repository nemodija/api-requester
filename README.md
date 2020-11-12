# api-requester

api一覧からリクエストを送信し、レスポンスコードとテキストを結果として保持する

## Environment

```sh
python --version
  # Python 3.8.6
```

## Configuration

**config.yaml**

|Key|Description|Default|
|--|--|--|
|protocol|接続するプロトコル|`HTTP`|
|hostname|接続先のホスト名|`localhost`|
|request_path_file|APIのURLパス一覧を記述したファイルパス|`./request_path.yaml`|
|result/parent_dir_path|結果出力先のディレクトリ|`.`|
|result/dir_prefix|結果出力ディレクトリのプレフィックス|`result`|
|placeholder|APIのURLパス一覧のプレースホルダーの正規表現|`(:\w+)`|
|variables|プレースホルダーの置換一覧<br>request_list.yml| *None* |

例)
```yaml
protocol: https
hostname: example.com
request_path_file: './request_list.yml'
result:
  parent_dir_path: '.'
  dir_prefix: 'EXAMPLE'
placeholder: '(:\w+)'
variables:
  'group-a':
    ':prefCode':
      - 1
      - 2
    ':cityCode':
      - '01100'
      - '02203'
    ':year':
      - 2005
      - 2010
      - 2015
```

**request_list.yml**

例)

```
group-a:
- /api/v1/cities/:prefCode
- /api/v1/cities/:year/:prefCode/:cityCode
```

## Run

ライブラリをダウンロード

```sh
pip install -r requirements.txt
```

実行

```sh
python api-requester.py
```

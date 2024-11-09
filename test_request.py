import json
import requests
import uuid
import websocket  # pip install websocket-client

### 外部APIの接続確認（天気予報）
# jma_url = "https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json"

# response = requests.get(jma_url)
# jma_json = response.json()

# jma_weather = jma_json[0]["timeSeries"][0]["areas"][0]["weathers"][0].replace(' ', '')

# print(jma_weather)

### ALBの接続確認
# プロキシ設定
# proxies = {
#     'http':'http://proxygate20.nic.nec.co.jp:8080',
#     'https':'http://proxygate20.nic.nec.co.jp:8080',
# }

# base_url = "https://demo-alb-main-ec2-01-912669911.ap-northeast-1.elb.amazon.com"
# response = requests.get(url, verify=False)
# response = requests.get(url, proxies=proxies, verify=False)
# print(response.status_code)
# print(response.url)
# print(response.text)

### ノートブック実行のテスト
base_url = "http://localhost:8888"
api_url = base_url + "/api"
# ノートブックへのアクセス
notebook_path = "/test.ipynb"
nb_url = api_url + "/contents" + notebook_path
token = "191eae2479bf3a615d4c0ab1efa90fb11c013d2621bb951b"
headers =  {'Authorization': 'token ' + token}
# response = requests.get(nb_url)
response = requests.get(nb_url, headers=headers)
notebook = json.loads(response.text)
# カーネルの起動
kernel_url = api_url + '/kernels'
# response = requests.post(kernel_url)  # getでカーネルのリストを取得できます
response = requests.post(kernel_url, headers=headers)  # getでカーネルのリストを取得できます
kernel = json.loads(response.text)
print(kernel)

# ノートブックファイルのコードのみを取得して、実行
codes = [c['source'] for c in notebook['content']['cells'] if c['cell_type'] == 'code']
codes.append('print("' + kernel['id'] + '", end="")')  # 改行しないようにendを空文字で指定

# WebSocketで接続
ws_url = 'ws://localhost:8888/api/kernels/' + kernel['id'] + '/channels'
# socket = websocket.create_connection(ws_url)
socket = websocket.create_connection(ws_url, header=headers)
print(socket.status)  # 101

# コードを実行
for code in codes:
    header = {
        'msg_type': 'execute_request',
        'msg_id': uuid.uuid1().hex,
        'session': uuid.uuid1().hex
    }
    
    message = json.dumps({
        'header': header,
        'parent_header': header,
        'metadata': {},
        'content': {
            'code': code,
            'silent': False
        }
    })
    
    # 送信
    socket.send(message)

# 結果の保持
outputs = []
output = ''

while True:
    response = json.loads(socket.recv())
    msg_type = response['msg_type']

    if msg_type == 'stream':
        output = response['content']['text']
        
        if output == kernel['id']:
            socket.close()  # 最後に追加した出力と一致したらクローズ
            break
        else:
            outputs.append(output)

print(codes)

# カーネルのシャットダウン
# url = base_url + '/api/kernels/' + kernel['id']
# response = requests.delete(url, headers=headers)
# print(response.status_code)  # 204
import json
import requests
import uuid
import websocket  # pip install websocket-client

# トークンを含めたヘッダー
headers = {}

### ノートブック実行のテスト
url = "http://localhost:8888"
api_url = url + "/api"
# response = requests.get(api_url, verify=False)

session = requests.Session()
# サーバーから_xsrfトークンを取得
response = session.get(url, verify=False)
xsrf_token = session.cookies.get('_xsrf')
# カーネル起動リクエストに_xsrfトークンを追加
headers['X-XSRFToken'] = xsrf_token
headers['Content-Type'] = 'application/json'
# カーネルを起動
kernel_url = url + "/api/kernels"
response = session.post(kernel_url, verify=False, headers=headers, json={"name": "python3"})
# # カーネルを起動
# kernel_url = url + "/api/kernels"
# response = requests.post(kernel_url, verify=False, json={"name": "python3"})
# print(response.status_code)
# print(response.url)
# print(response.text)

# カーネルを起動
response = session.post(kernel_url, verify=False, headers=headers, json={"name": "python3"})
kernel = json.loads(response.text)
# print(kernel)

# ノートブックファイルの取得
file_path = 'test.ipynb' # 実行するノートブックファイル
nb_url = url + '/api/contents/' + file_path
response = requests.get(nb_url, verify=False, headers=headers)
notebook = json.loads(response.text)
# print(notebook)
### ノートブックファイルのコードのみを取得
codes = [c['source'] for c in notebook['content']['cells'] if c['cell_type'] == 'code']
codes.append('print("' + kernel['id'] + '", end="")')  # 改行しないようにendを空文字で指定

# WebSocketで接続
ws_url = 'ws://localhost:8888/api/kernels/' + kernel['id'] + '/channels'
socket = websocket.create_connection(ws_url, verify=False, header=headers)
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

print(outputs)

# カーネルのシャットダウン
kernel_shutdown_url = url + '/api/kernels/' + kernel['id']
response = session.delete(kernel_shutdown_url, verify=False, headers=headers, json={"name": "python3"})
print(response.status_code)  # 204
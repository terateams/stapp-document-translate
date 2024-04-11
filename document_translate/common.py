import os
import requests
import jwt

def check_apptoken_from_apikey(apikey: str):
    if not apikey:
        return None
    apisecret = os.environ.get('APP_SECRET')
    if apikey:
        try:
            payload = jwt.decode(apikey, apisecret, algorithms=['HS256'])
            uid = payload.get('uid')
            if uid :
                return uid
        except Exception as e:
            return None
    return None

def get_global_datadir(subpath: str = None):
    """
    获取全局数据目录。

    Args:
        subpath (str, optional): 子路径。默认为None。

    Returns:
        str: 数据目录路径。
    """
    datadir = os.environ.get("DATA_DIR", "/tmp/teamsgpt")
    if subpath:
        datadir = os.path.join(datadir, subpath)
    if not os.path.exists(datadir):
        os.makedirs(datadir)
    return datadir


def remote_file_to_localfile(dir: str, new_filename: str = None, file_url: str = None, headers: dict = None):
    """Save file to temp folder synchronously using requests"""
    filename = os.path.join(dir, os.path.basename(file_url))
    if new_filename:
        filename = os.path.join(dir, new_filename)
    
    response = requests.get(file_url, headers=headers)
    
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
    else:
        raise Exception(f"Failed to download file. Status code: {response.status_code}")

    return filename


import requests
import json

def translate_document(file_path, target_lang="zh-CN", apikey=None):
    url = os.getenv("TEAMSGPT_APISITE", "https://api.teamsgpt.net") + "/api/document/translate"
    # Prepare headers and data
    headers = {"Authorization": f"Bearer {apikey}"}
    # 准备文件和目标语言数据
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        data = {'target_lang': target_lang}
        
        # 发送请求
        response = requests.post(url, files=files, data=data, headers=headers)
    
        # 检查响应状态码
        if response.status_code == 200:
            # 解析 JSON 响应
            response_json = response.json()
            return response_json["data"]
        else:
            raise Exception(f"Failed to translate document. Status code: {response.status_code}")



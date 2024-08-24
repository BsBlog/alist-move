import requests
import time
import os
from datetime import datetime, timedelta, timezone

base_url = os.environ["Alist_Base_Url"]
username = os.environ["Alist_Username"]
password = os.environ["Alist_Password"]
max_retries = 3  # 最大重试次数
retry_delay = 5  # 每次重试间隔（秒）


def get_token(username, password):
    url = f"{base_url}/api/auth/login"
    data = {"username": username, "password": password}
    response_data = make_request("post", url, json=data)
    return response_data["data"]["token"]


def list_folders(token, dir_path):
    url = f"{base_url}/api/fs/list"
    headers = {"Authorization": f"{token}"}
    data = {"path": dir_path}
    response_data = make_request("post", url, headers=headers, json=data)
    items = response_data["data"]["content"]

    if not items:
        return []

    # 当前时间（UTC时区感知的时间）
    now = datetime.now(timezone.utc)
    cutoff_time = now - timedelta(minutes=5)

    # 过滤出修改时间在5分钟以外的文件夹
    folders = []
    for item in items:
        modified_time = datetime.fromisoformat(item["modified"].replace("Z", "+00:00")).astimezone(timezone.utc)
        if modified_time < cutoff_time:
            folders.append(item["name"])

    return folders


def copy_folders(token, src_dir, dst_dir, names):
    url = f"{base_url}/api/fs/copy"
    headers = {"Authorization": f"{token}"}
    data = {
        "src_dir": src_dir,
        "dst_dir": dst_dir,
        "names": names
    }
    response_data = make_request("post", url, headers=headers, json=data)
    return response_data


def get_pending_tasks(token):
    url = f"{base_url}/api/admin/task/copy/undone"
    headers = {"Authorization": f"{token}"}
    response_data = make_request("get", url, headers=headers)

    try:
        data = response_data["data"]
    except ValueError:
        data = []
    return data


def delete_folder(token, dir_path, names):
    url = f"{base_url}/api/fs/remove"
    headers = {"Authorization": f"{token}"}
    data = {
        "dir": dir_path,
        "names": names
    }
    response_data = make_request("post", url, headers=headers, json=data)
    return response_data


def make_request(method, url, headers=None, json=None):
    for attempt in range(max_retries):
        response = requests.request(method, url, headers=headers, json=json)
        if response.status_code == 200:
            response_data = response.json()
            if response_data["code"] == 200:
                return response_data
            else:
                print(f"API returned an error code {response_data['code']}: {response_data.get('message', '')}")
        else:
            print(f"Request failed with status code {response.status_code}. Retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)
    raise Exception(f"Failed to get a successful response after {max_retries} attempts.")


# 主函数
def main():
    token = get_token(username, password)

    movies_src_dir = os.environ["Movies_Path"]
    movies_dst_dir = os.environ["Target_Movies_Path"]
    movie_folders = list_folders(token, movies_src_dir)
    if movie_folders:
        copy_folders(token, movies_src_dir, movies_dst_dir, movie_folders)

    tv_src_dir = os.environ["TV_Path"]
    tv_dst_dir = os.environ["Target_TV_Path"]
    tv_folders = list_folders(token, tv_src_dir)
    if tv_folders:
        copy_folders(token, tv_src_dir, tv_dst_dir, tv_folders)
    time.sleep(3)

    while True:
        pending_tasks = get_pending_tasks(token)
        if not pending_tasks:
            break
        time.sleep(1)

    if movie_folders:
        delete_folder(token, movies_src_dir, movie_folders)
    if tv_folders:
        delete_folder(token, tv_src_dir, tv_folders)


if __name__ == "__main__":
    main()

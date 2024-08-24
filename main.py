import requests
import time
import os
from datetime import datetime, timedelta

base_url = os.environ["Alist_Base_Url"]
username = os.environ["Alist_Username"]
password = os.environ["Alist_Password"]


def get_token(username, password):
    url = f"{base_url}/api/auth/login"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()["data"]["token"]


def list_folders(token, dir_path):
    url = f"{base_url}/api/fs/list"
    headers = {"Authorization": f"{token}"}
    data = {"path": dir_path}
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    items = response.json()["data"]["content"]

    if not items:
        return []

    # 当前时间
    now = datetime.now()
    cutoff_time = now - timedelta(minutes=3)

    # 过滤出修改时间在3分钟以外的文件夹
    folders = [
        item["name"] for item in items
        if datetime.fromtimestamp(item["modified"]) < cutoff_time
    ]

    return folders


def copy_folders(token, src_dir, dst_dir, names):
    url = f"{base_url}/api/fs/copy"
    headers = {"Authorization": f"{token}"}
    data = {
        "src_dir": src_dir,
        "dst_dir": dst_dir,
        "names": names
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()


def get_pending_tasks(token):
    url = f"{base_url}/api/admin/task/copy/undone"
    headers = {"Authorization": f"{token}"}
    response = requests.get(url, headers=headers)

    # 处理可能的JSONDecodeError
    try:
        data = response.json()["data"]
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
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()


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

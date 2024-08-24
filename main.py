import requests
import time
import os

# 配置
base_url = os.environ["Alist_Base_Url"]
username = os.environ["Alist_Username"]
password = os.environ["Alist_Password"]


# 获取Token
def get_token(username, password):
    url = f"{base_url}/api/auth/login"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()["data"]["token"]


# 列出目录中的子文件夹
def list_folders(token, dir_path):
    url = f"{base_url}/api/fs/list"
    headers = {"Authorization": f"{token}"}
    data = {"path": dir_path}
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    items = response.json()["data"]["content"]

    # 如果items为None或为空，返回空列表
    if not items:
        return []

    folders = [item["name"] for item in items]
    return folders


# 复制文件夹
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


# 获取未完成任务
def get_pending_tasks(token):
    url = f"{base_url}/api/fs/tasks"
    headers = {"Authorization": f"{token}"}  # 直接使用token
    response = requests.get(url, headers=headers)

    # 处理可能的JSONDecodeError
    try:
        data = response.json()["data"]
    except ValueError:
        data = []
    return data


# 删除文件夹
def delete_folder(token, dir_path, names):
    url = f"{base_url}/api/fs/remove"
    headers = {"Authorization": f"{token}"}  # 直接使用token
    data = {
        "dir": dir_path,
        "names": names
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()


# 主函数
def main():
    token = get_token(username, password)

    # 获取/movies下的所有子文件夹
    movies_src_dir = os.environ["Movies_Path"]
    movies_dst_dir = os.environ["Target_Movies_Path"]
    movie_folders = list_folders(token, movies_src_dir)
    if movie_folders:
        copy_folders(token, movies_src_dir, movies_dst_dir, movie_folders)

    # 获取/tv下的所有子文件夹
    tv_src_dir = os.environ["TV_Path"]
    tv_dst_dir = os.environ["Target_TV_Path"]
    tv_folders = list_folders(token, tv_src_dir)
    if tv_folders:
        copy_folders(token, tv_src_dir, tv_dst_dir, tv_folders)

    # 等待所有复制任务完成
    while True:
        time.sleep(5)
        pending_tasks = get_pending_tasks(token)
        if not pending_tasks:
            break
        time.sleep(5)  # 每5秒检查一次

    # 删除源文件夹
    if movie_folders:
        delete_folder(token, movies_src_dir, movie_folders)
    if tv_folders:
        delete_folder(token, tv_src_dir, tv_folders)


if __name__ == "__main__":
    main()

import os
import sys

# 获取当前文件的绝对路径
current_file_abspath = os.path.abspath(__file__)
# 查找文件夹下所有文件
def find_file(path, file_type) -> list:
    if not os.path.exists(path):
        os.makedirs(path)
    data_list = []
    for root, dirs, files in os.walk(path):
        if root != path:
            break
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.find(file_type) != -1:
                data_list.append(file_path)
    return data_list

def find_cookie(folder_name):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_directory, folder_name)
    return find_file(path, "json")

def find_article(type):
    father_path = os.path.abspath("")
    path = os.path.join(father_path, f'origin_data/{type}')
    return find_file(path, "json")
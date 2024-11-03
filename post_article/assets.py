import os
import sys

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
    current_directory = os.path.dirname(sys.argv[0])
    path = os.path.join(current_directory, folder_name)
    return find_file(path, "json")

def find_article():
    father_path = os.path.abspath("")
    path = os.path.join(father_path, 'json')
    return find_file(path, "json")
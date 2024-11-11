import os
import shutil
import json
from datetime import datetime

def delete_all_files(folder_path):
    # 获取文件夹中所有文件的列表
    try:
        file_list = os.listdir(folder_path)
        for file_name in file_list:
            file_path = os.path.join(folder_path, file_name)
            # 判断是否为文件
            if os.path.isfile(file_path):
                # 删除文件
                os.remove(file_path)
    except:
        print("delete_all_files except")

def delete_all_folders_and_files(folder_path):
    # 获取文件夹中所有子文件夹的列表
    try:
        file_list = os.listdir(folder_path)
        for file_name in file_list:
            file_path = os.path.join(folder_path, file_name)
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            else:
                os.remove(file_path)
    except Exception as e:
        print('Error deleting files:', e)


def write_to_txt(data, filename, second_folder_name = '', url_filter = '',max_num = -1): 
    # 打开文件 today.json, 如果不存在则创建
    base_path = os.path.abspath("")
    today_json_path = os.path.join(base_path, 'today.json')
    today = None
    
    if not os.path.exists(today_json_path):
        # 获取当前日期和时间
        formatted_date = datetime.now().strftime("%Y-%m-%d")
        today = {
            'time' : formatted_date,
            'hrefs' : []
        }
    else:
        with open(today_json_path, 'r', encoding='utf-8') as f:
            today = json.load(f)
            if today is None:
                formatted_date = datetime.now().strftime("%Y-%m-%d")
                today = {
                    'time' : formatted_date,
                    'hrefs' : []
                }
            else:
                if today['time'] == datetime.now().strftime("%Y-%m-%d"):
                    pass
                else:
                    today = {
                        'time' : datetime.now().strftime("%Y-%m-%d"),
                        'hrefs' : []
                    }

    # 只保留max_num个数据，data格式 [{'title':'','href':''}] 中的href和today中的hrefs 格式 ['',''] 数据比较，不要data中存在的数据
    new_data = []
    for item in data:
        if item['href'] not in today['hrefs']:
            new_data.append(item)
    # 去重数据，得到new_data
    if max_num > 0 and len(new_data) > max_num:
        new_data = new_data[:max_num]
    path = os.path.join(base_path, 'origin_data')
    if second_folder_name != '':
        path = os.path.join(path, second_folder_name)
    # 写入txt文件
    if not os.path.exists(path):
        os.makedirs(path)
    with open(f'{path}/{filename}', 'w', encoding='utf-8') as file:  
        for item in new_data:  
            if url_filter in item['href'] :
                file.write(f"{item['title']}\t{item['href']}\n")  
    print(f'抓取数据已写入:{filename}')
    # 将新的数据添加到today['hrefs']中
    for item in new_data:
        today['hrefs'].append(item['href'])
    with open(today_json_path, 'w', encoding='utf-8') as f:
        json.dump(today, f, ensure_ascii=False)

def delete_all_origin_datas():
    # 删除文件夹下所有文件或文件夹
    folder_path = os.path.join(os.path.abspath("") , 'origin_data')
    delete_all_folders_and_files(folder_path)
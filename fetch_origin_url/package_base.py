import os
import shutil

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


def write_to_txt(data, filename, second_folder_name = '', url_filter = ''):  
    path = os.path.join(os.path.abspath("") , 'origin_data')
    if second_folder_name != '':
        path = os.path.join(path, second_folder_name)

    if not os.path.exists(path):
        os.makedirs(path)

    with open(f'{path}/{filename}', 'w', encoding='utf-8') as file:  
        for item in data:  
            if url_filter in item['href'] :
                file.write(f"{item['title']}\t{item['href']}\n")  
    print(f'抓取数据已写入:{filename}')

def delete_all_origin_datas():
    # 删除文件夹下所有文件或文件夹
    folder_path = os.path.join(os.path.abspath("") , 'origin_data')
    delete_all_folders_and_files(folder_path)
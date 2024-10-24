import os

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


def write_to_txt(data, filename, url_filter = ''):  
    path = os.path.join(os.path.abspath("") , 'origin_data')
    delete_all_files(path)
    print(f'删掉老数据:{path}')
    if not os.path.exists(path):
        os.makedirs(path)
    with open(f'{path}/{filename}', 'w', encoding='utf-8') as file:  
        for item in data:  
            if url_filter in item['href'] :
                file.write(f"{item['title']}\t{item['href']}\n")  
    print(f'抓取数据已写入:{filename}')
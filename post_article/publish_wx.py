import asyncio
from check_login_wx import *
import os
import json
import random
from assets import *
from create_article import *

def check_has_article():
    article_list = find_article()
    if len(article_list) == 0:
        main()
        return False
    else:
        return True

async def main():
    # 调用check_log_state函数检查登录状态
    await check_log_state()

    cookie_list = find_cookie('wx_cookie')
    article_list = find_article()
    
    # 生成整数商
    average = len(article_list) // len(cookie_list)
    x = 0
    for cookie_path in cookie_list:
        x += 1
        cookie_name: str = os.path.basename(cookie_path)
        author = cookie_name.split("_")[1][:-5]
        article_list = find_article()
        print("正在使用[%s]发布作品，当前账号排序[%s]" % (author, str(x)))
        n = 1
        for index, article_path in enumerate(article_list):
            target_time = get_target_time(n)
            if target_time == '':
                print("发布时间到了次日，结束执行")
                break
            try:
                article = json.load(open(article_path, encoding='utf8'))
            except UnicodeDecodeError:
                continue
            img = article["img"]
            # 判断图片是否存在，不存在则跳过。顺便把json文件删掉
            if not os.path.isfile(img):
                # 指定包含图片的文件夹路径
                folder_path = os.path.join(os.path.abspath(""), 'default_img')
                # 获取文件夹中所有文件的列表
                files = os.listdir(folder_path)
                # 过滤出图片文件，这里假设图片文件是以.jpg或.png结尾
                image_files = [f for f in files if f.endswith('.jpg') or f.endswith('.png')]
                # 确保至少有一张图片
                if image_files:
                    # 从图片列表中随机选择一张图片
                    random_image = random.choice(image_files)
                    # 构建完整的图片路径
                    random_image_path = os.path.join(folder_path, random_image)
                    img = random_image_path
                    # 打印或处理随机选择的图片路径
                    print("配图不存在，随机选择的图片是:", random_image_path)
                else:
                    print("配图不存在，文件夹中没有找到图片文件。")
                    continue
            dialog = {
                "title": article["title"],
                "author": author,
                "content": article["content"],
                "img": img,
                "time": target_time
            }
            upload_result = ''
            try:
                app = login_wx(60, cookie_path, dialog)
                upload_result = asyncio.run(app.main())
            except Exception as e:
                upload_result = 'other error'
                print(f'上传报错：{e}')

            if upload_result == 'error':
                os.remove(cookie_path)
                print("账号未登录")
                break
            elif upload_result == 'success':
                print("第%s个作品已成功发布" % str(n))
                
            # 删除article里的图片和article_path文件
            try:
                if 'default_img' not in dialog["img"]:
                    os.remove(dialog["img"])
                file_exists = True
            except FileNotFoundError:
                file_exists = False

            try:
                os.remove(article_path)
                file_exists = file_exists and True
            except FileNotFoundError:
                file_exists = False

            if not file_exists:
                n -= 1
            
            n += 1
            if n > average:
                break

asyncio.run(main())

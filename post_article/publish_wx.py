import asyncio
from check_login_wx import *
import os
import json
import random
from assets import *
from create_article import *
from datetime import datetime, timedelta
    
def get_target_time(n):
    # 获取当前时间
    current_time = datetime.now()
    # 计算时间增量，n个30分钟
    time_delta = timedelta(minutes=30 * n)
    # 计算目标时间
    target_time = current_time + time_delta
    # 格式化目标时间为 HH:MM
    formatted_target_time = target_time.strftime("%H:%M")
    # 如果目标时间到了次日，返回''
    if target_time.date() > current_time.date():
        return ''
    return formatted_target_time

def get_valid_image(article):
    img = article["img"]
    # 判断图片是否存在，不存在则跳过。顺便把json文件删掉（这部分逻辑未在函数中实现）
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
            # 打印或处理随机选择的图片路径（可以根据需要选择是否保留打印语句）
            print("配图不存在，随机选择的图片是:", random_image_path)
        else:
            print("配图不存在，文件夹中没有找到图片文件。")
            # 注意：这里返回了None，调用方需要检查返回值是否为None来处理这种情况
            return None
    return img

def delete_article(article_path):
    try:
        os.remove(article_path)
    except FileNotFoundError:
        print("文章删除失败")

def delete_img(img_path):
    try:
        if 'default_img' not in img_path:
            os.remove(img_path)
    except FileNotFoundError:
        print("配图删除失败")

async def publish(cookie_file,dialogs) -> str:
    async with async_playwright() as playwright:
        browser =  await playwright.chromium.launch(headless=False,
                                        chromium_sandbox=False,
                                        ignore_default_args=["--enable-automation"],
                                        channel="chrome")
        context = await browser.new_context(storage_state=cookie_file, user_agent=UA["web"])
        page = await context.new_page()
        await page.add_init_script(path="stealth.min.js")
        await page.goto("https://mp.weixin.qq.com/")
        if "token" not in page.url:
            print("账号未登录")
            return 'error'
        print("账号已登录")
        # --------------------------------开始发布流程-------------------------------------------
        element = await page.wait_for_selector('//*[@id="app"]/div[2]/div[3]/div[2]/div/div[2]')  
        await element.click()

        # 监听新页面打开事件（异步方式）  
        async with page.expect_event('popup') as event_info:  
            new_page = await event_info.value  # 在这里，value 是可用的，因为它是异步上下文管理器的结果  
        for index,dialog in enumerate(dialogs):
            print(f"正在保存第{index}篇文章")
            if index != 0:
                # 新建一条消息
                new_article_btn = await page.wait_for_selector('#add_appmsg_container > div')
                await new_article_btn.hover()
                time.sleep(1)
                # 点击 写新文章 按钮
                write_new_article_btn = await new_page.wait_for_selector('body > div.preview_media_add_panel_wrp.js_article_panel > div > ul > li:nth-child(1)')
                await write_new_article_btn.click()
                time.sleep(1)
            # 填写标题
            await new_page.click('//*[@id="title"]')  # 使用正确的ID选择器  
            await new_page.keyboard.type(dialog['title'])
            time.sleep(1)
            # 填写作者
            await new_page.keyboard.press('Tab')  
            await new_page.keyboard.type(dialog['author'])
            time.sleep(1)
            # 填写正文（光标focus在正文部分）
            await new_page.keyboard.press('Tab') 
            #   在开头插入图片 上传
            upload_pic = await new_page.wait_for_selector('#js_editor_insertimage')
            await upload_pic.click()
            time.sleep(1)
            # 等待并点击触发文件选择器的按钮  
            new_page.on("filechooser", lambda file_chooser: file_chooser.set_files(dialog['img']))
            # 点击触发文件选择器的按钮  
            upload_icon = await new_page.wait_for_selector('#js_editor_insertimage > ul > li:nth-child(1)')   
            await upload_icon.click()          
            await asyncio.sleep(1)
            #    写入正文  
            await new_page.keyboard.type('')
            time.sleep(5)
            await new_page.keyboard.type('')
            time.sleep(5)
            await new_page.keyboard.type(dialog['content'])
            time.sleep(1)
            # 滚动到页面底部  
            await new_page.evaluate('window.scrollTo(0, document.body.scrollHeight);')  
            time.sleep(1)
            # 选择第一张图片做封面
            pic = await new_page.wait_for_selector('//*[@id="js_cover_area"]/div[1]')
            await pic.hover()
            time.sleep(1)
            pick_from_article = await new_page.wait_for_selector('//*[@id="js_cover_null"]/ul/li[1]/a')
            await pick_from_article.click()
            time.sleep(1) 
            first_pic = await new_page.wait_for_selector('//*[@id="vue_app"]/div[2]/div[1]/div/div[2]/div[1]/div/ul/li/div')
            await first_pic.click()
            time.sleep(1)
            next_btn = await new_page.wait_for_selector('//*[@id="vue_app"]/div[2]/div[1]/div/div[3]/div[1]/button')
            await next_btn.click()
            time.sleep(1)
            finish_btn = await new_page.wait_for_selector('//*[@id="vue_app"]/div[2]/div[1]/div/div[3]/div[2]/button')
            await finish_btn.click()
            time.sleep(5)
        # 文章生成完毕，进入发布流程
        publish_btn = await new_page.wait_for_selector('//*[@id="js_send"]/button')
        await publish_btn.click()
        time.sleep(1)
        # 原定时发布代码，勿删，有用
        # if dialog['time'] != '':            
        #     try:
        #         set_publish_time = await new_page.wait_for_selector('#vue_app > div:nth-child(5) > div.new_mass_send_dialog > div.weui-desktop-dialog__wrp > div > div.weui-desktop-dialog__bd > div > div > form > div.mass-send__td-setting > div > div > div.mass-send__timer-wrp > label > div')
        #         await set_publish_time.click()
        #     except Exception as e:
        #         print(f'点击定时异常：{e}')
        #     try:    
        #         set_publish_time1 = await new_page.wait_for_selector('#vue_app > div:nth-child(5) > div.new_mass_send_dialog > div.weui-desktop-dialog__wrp > div > div.weui-desktop-dialog__bd > div > div > form > div.mass-send__td-setting.timer_setting > div > div > div.mass-send__timer-wrp > label',timeout=5000)
        #         await set_publish_time1.click()
        #     except Exception as e:
        #         print(f'点击定时异常1：{e}')
        #     time.sleep(1)
        #     # 找到输入框并输入发布时间
        #     input_time_icon = await new_page.wait_for_selector('#vue_app > div:nth-child(5) > div.new_mass_send_dialog > div.weui-desktop-dialog__wrp > div > div.weui-desktop-dialog__bd > div > div > form > div.mass-send__td-setting > div.mass-send__timer-container > div > dl:nth-child(2) > dt > span')  
        #     await input_time_icon.click()
        #     time.sleep(1)
        #     await new_page.fill('#vue_app > div:nth-child(5) > div.new_mass_send_dialog > div.weui-desktop-dialog__wrp > div > div.weui-desktop-dialog__bd > div > div > form > div.mass-send__td-setting > div.mass-send__timer-container > div > dl.weui-desktop-picker__time.weui-desktop-picker__focus > dt > span > div > span > input', '') 
        #     await new_page.keyboard.type(dialog['time'])
        #     time.sleep(1)
        #     await new_page.click('#vue_app > div:nth-child(5) > div.new_mass_send_dialog > div.weui-desktop-dialog__wrp > div > div.weui-desktop-dialog__hd > h3')  # 这是一个伪代码示例，实际选择器可能需要根据页面结构进行调整
        #     time.sleep(1)
        
        publish_again = await new_page.wait_for_selector('//*[@id="vue_app"]/div[2]/div[1]/div[1]/div/div[3]/div/div/div[1]/button')
        await publish_again.click()
        time.sleep(1)
        publish_3 = await new_page.wait_for_selector('//*[@id="vue_app"]/div[2]/div[2]/div[1]/div/div[3]/div/div[1]/button')
        await publish_3.click()
        time.sleep(10)#等待返回发表状态
        # ------------------------------------发布流程结束-------------------------------------------------------
        # 关掉浏览器
        await browser.close()
        return 'success'


async def main():
    # 调用check_log_state函数检查登录状态
    await check_log_state()

    cookie_list = find_cookie('wx_cookie')
    
    for index,cookie_path in enumerate(cookie_list):
        cookie_name: str = os.path.basename(cookie_path)
        author = cookie_name.split("_")[1][:-5]
        article_list = find_article(author_and_type[author])
        print("-->正在使用[%s]发布作品，当前账号排序[%s]" % (author, str(index)))
        if len(article_list) == 0:
            print("[%s]所属分类[%s]下没有可发表的文章，继续下一账号"% (author, author_and_type[author]))
            continue
        dialogs = []
        for index, article_path in enumerate(article_list):
            try:
                article = json.load(open(article_path, encoding='utf8'))
            except UnicodeDecodeError:
                delete_article(article_path)
                continue
            img = get_valid_image(article)
            if img is None:
                delete_article(article_path)
                continue
            dialog = {
                "title": article["title"],
                "author": author,
                "content": article["content"],
                "img": img,
                "time": ''
            }
            dialogs.append(dialog)
            
        publish_result = await publish(cookie_path,dialogs)
        
        # 删除article里的图片和article_path文件
        delete_article(article_path)
        delete_img(img)

        print("-->账号[%s]作品已成功发布" % author)

asyncio.run(main())

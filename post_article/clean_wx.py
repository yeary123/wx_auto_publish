from playwright.async_api import async_playwright
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # 添加项目根目录到sys.path
import const
import check_login_wx as self
import asyncio
from assets import *


async def do_clean(page):
     # 点击 内容管理
     management = await page.wait_for_selector('#js_index_menu > ul > li.weui-desktop-menu__item.weui-desktop-menu_create > span')
     await management.click()
     # 点击 发表记录
     publish_history = await page.wait_for_selector('#js_level2_title > li > ul > li:nth-child(3) > a')
     await publish_history.click()
     
     index = 1
     while index <= 5:
          print(f'开始处理第{index}页')
          # 在记录列表中处理数据
          list_element = await page.wait_for_selector('#app > div > div.publish_content.publish_record_history > div:nth-child(1) > div:nth-child(1)')
          child_elements = await list_element.query_selector_all(' > div') if list else []
          for child in child_elements:
               # 今天发表的内容不删除
               date_element = await child.query_selector('.weui-desktop-mass__time')
               date = await date_element.inner_text()
               if '今天' in date:
                    continue
               # 已删除的内容跳过
               has_delete = await child.query_selector('.more_icon')
               if has_delete is None:
                    continue
               read_count_parent_element = await child.query_selector('.weui-desktop-mass-media__data.appmsg-view')
               read_count_element = await read_count_parent_element.query_selector('.weui-desktop-mass-media__data__inner')
               read_count = await read_count_element.inner_text()
               if int(read_count) == 0 :
                    await child.hover()
                    more_icon = await child.query_selector('.more_icon')
                    await more_icon.click()
                    select_option = await more_icon.query_selector('.select_option')
                    delete_li_elements = await select_option.query_selector_all('li')
                    delete_li_handle = None
                    for li in delete_li_elements:
                         if (await li.inner_text()).strip() == '删除':
                              delete_li_handle = li
                              break
                    if delete_li_handle:  
                         await delete_li_handle.click()
                         confirm_button = await more_icon.query_selector('.weui-desktop-btn.weui-desktop-btn_primary')
                         await confirm_button.click()
                         await page.wait_for_timeout(5000)
               
          page_input_selector = '#app > div > div.publish_content.publish_record_history > div.weui-desktop-pagination > span.weui-desktop-pagination__form > input'
          # 跳转到下一页
          index += 1
          await page.fill(page_input_selector, str(index))
          await page.keyboard.press('Enter')
          print(f'跳转第{index}页')
          await page.wait_for_timeout(5000)
          

async def clean_history(cookie_path):
      async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=False,
                                          chromium_sandbox=False,
                                          ignore_default_args=["--enable-automation"],
                                          channel="chrome"
                                          )
            context = await browser.new_context(storage_state=cookie_path, user_agent=const.UA["web"])
            page = await context.new_page()
            await page.add_init_script(path="stealth.min.js")
            await page.goto("https://mp.weixin.qq.com/")
            await do_clean(page)
            # 关掉浏览器
            await browser.close()

def clean():
#     asyncio.run(self.check_log_state())
    cookie_list = find_cookie('wx_cookie')
    for cookie_path in cookie_list:
        asyncio.run(clean_history(cookie_path))

clean()

    
            
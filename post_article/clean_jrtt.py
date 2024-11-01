from playwright.async_api import async_playwright
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # 添加项目根目录到sys.path
import const
import check_login_jrtt as self
import asyncio

# 滚动页面的函数
async def scroll_page(page):
    await page.evaluate("""
        () => {
            window.scrollTo(0, document.body.scrollHeight);
        }
    """)

async def do_clean(page):
     # 滚动页面获取更多数据
    for _ in range(10):
        await scroll_page(page)
        # 等待数据加载，根据需要调整等待时间或使用其他等待策略
        await page.wait_for_timeout(2000)
    # 获取记录列表
    list_element = await page.wait_for_selector('#root > div > div.main-wrapper > div.main-l > div > div:nth-child(2) > div > div')
    child_elements = await list_element.query_selector_all('.profile-wtt-card-wrapper')
    for child_element in child_elements:
        # 展现数据
        show_num = await child_element.query_selector('.profile-feed-card-tools-text')
        show_num_text = await show_num.inner_text()
        # "345展现"，去掉 展现 两个字，只保留数字
        try:
            show_count = int(show_num_text[:-2])
        except ValueError:
            continue
        # 时间
        time = await child_element.query_selector('.time')
        time_text = await time.inner_text()
        # 今天的不用删，都是 n分钟前，n小时前，不包含 天 
        if "天" not in time_text:
            continue
        async def delete():
            right_tools = await child_element.query_selector('.right-tools')
            more_action = await right_tools.query_selector(':last-child')
            await more_action.hover()
            more_list = await more_action.query_selector('.actions-list')
            delete_btn = await more_list.query_selector(':first-child')
            page.on("dialog", lambda dialog: dialog.accept())
            await delete_btn.click()
            await page.wait_for_timeout(2000)
          
        # 昨天的数据，展现 < 100 的删除
        if "昨天" in time_text:
            if show_count < 100:
                await delete()
            continue
        # 昨天以前的数据，展现 < 1000 的删除
        if show_count < 1000:
            await delete()
          

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
            await page.goto("https://www.toutiao.com/")
            avatar = await page.query_selector('#root > div > div.toutiao-header > div.header-right.common-component-wrapper > div.user-icon > a')
            await avatar.click()
            # 进入个人中心  
            async with page.expect_event('popup') as event_info:  
                new_page = await event_info.value  # 在这里，value 是可用的，因为它是异步上下文管理器的结果 
            await do_clean(new_page)
            # 关掉浏览器
            await browser.close()

def clean():
    asyncio.run(self.check_log_state())
    cookie_list = self.find_cookie()
    for index,cookie_path in enumerate(cookie_list):
        cookie_name: str = os.path.basename(cookie_path)
        author = cookie_name.split("_")[1][:-5]
        print("正在删除[%s]账号数据，当前序号[%s]" % (author, str(index)))
        asyncio.run(clean_history(cookie_path))

clean()

    
            
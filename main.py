from fetch_origin_url import fetch_data
from create_article import start_create_article
import asyncio
from post_article import publish_wx

if __name__ == '__main__':
    # 获取数据链接
    # fetch_data.fetch_data()
    # 数据处理
    # start_create_article()
    # 上传
    asyncio.run(publish_wx.upload())




from from_jrrb import *
import asyncio
from package_base import *
def fetch_data():
    print("-->删掉所有旧数据")
    delete_all_origin_datas()
    # 获取热点数据
    # 从网易新闻接口获取热点数据
    print("-->开始获取数据")
    print("从网易新闻获取数据")
    asyncio.run(from_netease())
    # 从36氪获取热点数据
    print("从36氪获取数据")
    asyncio.run(from_36ke())
    print("从it之家数据")
    asyncio.run(from_itzhijia())
    print("从澎湃获取数据")
    asyncio.run(from_pengpai())
    print("-->获取数据完成")
    
fetch_data()
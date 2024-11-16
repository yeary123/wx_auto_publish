from . import from_jrrb
from .from_jrrb import *
import asyncio
from . import package_base
from .package_base import *
from . import from_jrtt
from .from_jrtt import *
def fetch_data():
    print("-->删掉所有旧数据")
    delete_all_origin_datas()
    # 获取热点数据
    # 从网易新闻接口获取热点数据
    print("-->开始获取数据")
    print("从网易新闻获取数据")
    asyncio.run(from_netease())
    # 从36氪获取热点数据
    # print("从36氪获取数据")
    # asyncio.run(from_36ke())
    # print("从it之家数据")
    # asyncio.run(from_itzhijia())
    # print("从澎湃获取数据")
    # asyncio.run(from_pengpai())
    # print("从今日头条获取数据")
    # categories = [MILITARY, FINANCE, TECH, SPORTS, HISTORY, FOOD, TRAVEL, HOT, ENTERTAINMENT]
    # categories = [HISTORY,SPORTS]
    # asyncio.run(from_jrtt(categories))
    print("-->获取数据完成")
    
# fetch_data()
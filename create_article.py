from openai import OpenAI
import requests  
from bs4 import BeautifulSoup  
import time
import json  
import os 
from PIL import Image
from playwright.sync_api import sync_playwright
from const import *

data_folder = 'origin_data'

# 获取当前文件的完整路径  
current_file_path = __file__ 

def deal_img(img_folder,img_name):
    img_path = os.path.join(img_folder, f'{img_name}.jpg')
    if not os.path.exists(img_path):
        print(f"图片 {img_path} 不存在")
        return ''
        
    over_img_name = f"over_{img_name}.jpg"
    over_img_path = os.path.join(img_folder, over_img_name)
    # 打开图像文件
    img = Image.open(img_path)
    # 获取图像的宽度和高度
    width, height = img.size
    img.close()
    x = width - 250
    y = height - 45
    os.system(f"ffmpeg -i {img_path} -vf \"drawbox=x={x}:y={y}:w=350:h=60:color=white@0.8:t=fill\" -c:a copy {over_img_path}")
    path = os.path.join(os.path.dirname(current_file_path) , f'{img_folder}/{over_img_name}')
    os.remove(img_path)
    return path

def download_image(url, img_folder ,img_name):
    try:
        # 发送GET请求获取图片内容
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        os.makedirs(img_folder,exist_ok=True)
        # 将图片内容写入文件
        save_path = os.path.join(img_folder, f"{img_name}.jpg")
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"图片已成功下载并保存到 {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
    except IOError as e:
        print(f"文件操作失败: {e}")

def read_txt_to_dict(file_path):  
    result = []  
      
    with open(file_path, 'r', encoding='utf-8') as file:  
        for line in file:  
            # 去除每行末尾的换行符  
            line = line.strip()  
              
            # 分割标题和URL，假设它们之间由制表符（\t）分隔  
            parts = line.split('\t')  
              
            if len(parts) == 2:  
                title = parts[0]  
                url = parts[1]  
                result.append({  
                    'title': title,  
                    'url': url  
                })  
            else:  
                # 如果格式不正确，可以选择跳过或记录日志  
                print(f"格式不正确的行: {line}")  
      
    return result  

        

def get_article_txt_img(url):
    try:
        with sync_playwright() as p:  
            browser = p.chromium.launch(headless=True,
                                        chromium_sandbox=False,
                                            ignore_default_args=["--enable-automation"],
                                            channel="chrome")  # 你可以设置为 headless=True 以在无头模式下运行  
            context = browser.new_context(user_agent = UA["web"])
            page = context.new_page() 
            page.add_init_script(path="stealth.min.js")
            page.goto(url)  # 替换为目标 URL  
            page.wait_for_timeout(5000)
            # 获取网页的html文本
            try:
                html = page.content()
            except Exception as e:
                print(e)
            
            # 如果url包含 www.163.com，则需要playwright找到特定元素
            toutiao_content_selector = '#root > div.article-detail-container > div.main > div:nth-child(1) > div > div > div > div > article'
            if 'www.163.com' in url:
                parent_element_handle = page.wait_for_selector('#content > div.post_body')                  
            elif 'www.toutiao.com' in url:
                parent_element_handle = page.wait_for_selector(toutiao_content_selector)  
            elif 'www.36kr.com' in url:
                parent_element_handle = page.wait_for_selector('#app > div > div.box-kr-article-new-y > div > div.kr-layout-main.clearfloat > div.main-right > div > div > div > div.article-detail-wrapper-box > div > div.article-left-container > div.article-content > div > div > div.common-width.margin-bottom-20 > div')  
            
            if parent_element_handle is not None:
                html = parent_element_handle.inner_html()

            # 关闭浏览器  
            browser.close()  
                
            # 使用BeautifulSoup解析网页内容  
            soup = BeautifulSoup(html, 'html.parser')  
            
            # 获取网页中的所有文字内容  
            text = soup.get_text()  
            # 查找所有 img 标签
            img_tags = soup.find_all('img')
            # 提取所有 img 标签的 data-src 或 src 属性值，如果都为空则不添加到列表中
            img_srcs = [
                img.get('data-src') or img.get('src')
                for img in img_tags
                if img.get('data-src') or img.get('src')
            ]
            print("已获取原文")
            return (text,img_srcs)
    except Exception as e:
        print(f'获取原文失败：{e}')
        return ("ERROR",[])

    
def create_article(txt,api_key): 
    content = f'''请阅读这篇文字：${txt} 
请根据下面的提示进行改写。
这篇文字是从一个网页上摘录下来的，有一篇文章的主体内容，还有一些无关内容。请甄别并删除无关内容。
明白文章表达的意思，抓住其主旨，将文章改写成200字左右短文，每个段落不要超过50字。
使用平易近人的语言，使文章更加亲切和易于理解；使用简单和通俗易懂的词汇，不要使用专业术语。
要使用短句，不要使用长句，不要冗长描述，便于阅读和理解。
使用口语化、接地气、人情味、富有情感等等语气。
段落过度要自然、逻辑清晰。不要使用“首先、其次、再次、然后、最后”这些副词和过渡词。
文章中要加入更多具体的例子、生动的描述和感官细节等。
不要出现作者表达了、文章主旨是之类的表述。我们的读者是不知道有原文章的。'''

    client = OpenAI(
        api_key = api_key, # 在这里将 MOONSHOT_API_KEY 替换为你从 Kimi 开放平台申请的 API Key
        base_url = "https://api.moonshot.cn/v1",
    )
    try:
        completion = client.chat.completions.create(
            model = "moonshot-v1-8k",
            messages = [
                {"role": "system", "content": "你是资深文字编辑。擅长改写文章。"},
                {"role": "user", "content": content}
            ],
            temperature = 0.3,
        )
        # 通过 API 我们获得了 Kimi 大模型给予我们的回复消息（role=assistant）
        content = completion.choices[0].message.content
        return content
    except Exception as e:
        print(f'调用大模型出问题:{e}')
        return None

def find_txt_files(path):
    txt_files = []

    # 遍历指定路径下的所有文件和子目录
    for root, dirs, files in os.walk(path):
        for file in files:
            # 检查文件是否是.txt文件
            if file.endswith('.txt'):
                # 拼接文件完整路径
                full_path = os.path.join(root, file)
                # 添加到结果列表
                txt_files.append(full_path)

    return txt_files

def deal_urls(dir_path):
    # 获取当前文件夹下的所有文件  
    files_path = find_txt_files(dir_path)  
    
    if len(files_path) == 0:
        print("没有txt文件数据，请先获取文章链接")
        exit()
    
    result = []
    # 遍历并读取每个 .txt 文件  
    for path in files_path: 
        # 获取path对应的文件夹名
        folder_name = os.path.dirname(path)
        result = read_txt_to_dict(path)
        # 遍历结果        
        for index,item in enumerate(result):
            title = item['title']  
            url = item['url']  
            print(f'-->开始处理文章：{title}')
            # 获取文章内容和图片
            (txt,imgs) = get_article_txt_img(url)
            if txt == "ERROR":
                print("获取文章失败")
                continue
            # 从constants.py中获取API_KEY
            count = len(API_KEY)
            api_key = API_KEY[index % count]
            article = create_article(txt,api_key)
            if article is None or article == "":
                continue
            # 下载文章图片
            dealt_img_path = ''
            if len(imgs) > 0:
                print("下载文章配图")
                index = int(len(imgs)/2)
                img = imgs[index]
                download_image(img, folder_name,title)
                dealt_img_path = deal_img(folder_name,title)
            # 创建字典来存储要写入 JSON 文件的数据  
            data = {  
                'title': title,  
                'content': article,
                'img': dealt_img_path  
            }   
            os.makedirs(data_folder, exist_ok=True)  
            # 将字典写入 JSON 文件  
            with open(f'{folder_name}/{title}.json', 'w', encoding='utf-8') as json_file:  
                json.dump(data, json_file, ensure_ascii=False, indent=4)  
            print(f"-->文章处理完成，已写入json文件：{title}.json")
            # 大模型限制，不能过于频繁调用
            time.sleep(30/count)

def start_create_article():
    deal_urls(data_folder)

if __name__ == '__main__':
    start_create_article()
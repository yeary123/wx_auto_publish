from openai import OpenAI
import requests  
from bs4 import BeautifulSoup  
import time
import json  
import os 
from PIL import Image

# 指定输出文件夹名称  
output_folder = 'json'  
img_folder = 'img'
input_folder = 'origin_data'
# 获取当前文件的完整路径  
current_file_path = __file__ 

def deal_img(img_folder,img_name):
    img_path = os.path.join(img_folder, f'{img_name}.jpg')
    over_img_name = f"over_{img_name}.jpg"
    over_img_path = os.path.join(img_folder, over_img_name)
    # 打开图像文件
    img = Image.open(img_path)
    # 获取图像的宽度和高度
    width, height = img.size
    img.close()
    x = width - 250
    y = height - 45
    print(f"Width: {width}, Height: {height}")
    os.system(f"ffmpeg -i {img_path} -vf \"drawbox=x={x}:y={y}:w=250:h=45:color=white@1:t=fill\" -c:a copy {over_img_path}")
    path = os.path.join(os.path.dirname(current_file_path) , f'{img_folder}/{over_img_name}')
    return path

def download_image(url, img_folder ,img_name):
    try:
        # 发送GET请求获取图片内容
        response = requests.get(url)
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
    # 发送HTTP GET请求获取网页内容  
    response = requests.get(url)  
    
    # 检查请求是否成功  
    if response.status_code == 200:  
        # 使用BeautifulSoup解析网页内容  
        soup = BeautifulSoup(response.text, 'html.parser')  
        
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
    else:  
        print(f"ERROE: {response.status_code}")
        return ("error",[])
    
def create_article(title,url): 
    # 获取文章内容和图片
    (txt,imgs) = get_article_txt_img(url)
    if txt == "ERROR":
        return ''
    
    content = f'请阅读这篇文字， ${txt}   这篇文字是从一个网页上摘录下来的，有一篇文章的主体内容，还有一些无关内容。请甄别并删除无关内容。明白文章表达的意思，抓住其主旨，将文章改写成200字左右短文，注意分段，语言风格生动活泼。不要出现作者表达了、文章主旨是之类的表述。我们的读者是不知道有原文章的。'

    client = OpenAI(
        api_key="sk-61TKoPC9JDizDvfptKSNvvj5VerE8TX2WSL4EJMyYtPriAXV", # 在这里将 MOONSHOT_API_KEY 替换为你从 Kimi 开放平台申请的 API Key
        base_url="https://api.moonshot.cn/v1",
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
        print("已获取改写文章")
        # 下载文章图片
        index = int(len(imgs)/2)
        img = imgs[index]
        download_image(img, img_folder,title)
        dealt_img_path = deal_img(img_folder,title)
        # 创建字典来存储要写入 JSON 文件的数据  
        data = {  
            'title': title,  
            'content': content,
            'img': dealt_img_path  
        }   
        os.makedirs(output_folder, exist_ok=True)  
        # 将字典写入 JSON 文件  
        with open(f'{output_folder}/{title}.json', 'w', encoding='utf-8') as json_file:  
            json.dump(data, json_file, ensure_ascii=False, indent=4)  
        print("已写入json")
    except Exception as e:
        print(f'调用大模型 or 写入json 出问题:{e}')

    # 大模型限制，不能过于频繁调用
    time.sleep(31)

def deal_urls(dir_path):
    # 获取当前文件夹下的所有文件  
    files = os.listdir(dir_path)  
    
    # 筛选以 .txt 结尾的文件  
    txt_files = [f for f in files if f.endswith('.txt')]  
    
    result = []
    # 遍历并读取每个 .txt 文件  
    for txt_file in txt_files:  
        # 构建文件的完整路径  
        file_path = os.path.join(dir_path, txt_file)  
        # 读取文件内容（这里以打印为例）  
        with open(file_path, 'r', encoding='utf-8') as txt_file:  
            result = read_txt_to_dict(file_path)
    # 遍历结果        
    for item in result:
        title = item['title']  
        url = item['url']  
        print(f'开始处理文章：{title}')
        create_article(title,url)

deal_urls(input_folder)
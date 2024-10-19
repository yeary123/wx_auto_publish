from openai import OpenAI
import requests  
from bs4 import BeautifulSoup  

def get_article_txt(url):
    # 发送HTTP GET请求获取网页内容  
    response = requests.get(url)  
    
    # 检查请求是否成功  
    if response.status_code == 200:  
        # 使用BeautifulSoup解析网页内容  
        soup = BeautifulSoup(response.text, 'html.parser')  
        
        # 获取网页中的所有文字内容  
        text = soup.get_text()  
        
        return text
    else:  
        print(f"ERROE: {response.status_code}")
        return "error"
    
def create_article(url): 
    txt = get_article_txt(url)
    if txt == "ERROR":
        return ''
    content = f'请阅读这篇文字， ${txt}   这篇文字是从一个网页上摘录下来的，有一篇文章的主体内容，还有一些无关内容。请甄别并删除无关内容。明白文章表达的意思，抓住其主旨，将文章改写成200字左右短文，注意分段，语言风格生动活泼。'

    client = OpenAI(
        api_key="sk-61TKoPC9JDizDvfptKSNvvj5VerE8TX2WSL4EJMyYtPriAXV", # 在这里将 MOONSHOT_API_KEY 替换为你从 Kimi 开放平台申请的 API Key
        base_url="https://api.moonshot.cn/v1",
    )
    
    completion = client.chat.completions.create(
        model = "moonshot-v1-8k",
        messages = [
            {"role": "system", "content": "你是资深文字编辑。"},
            {"role": "user", "content": content}
        ],
        temperature = 0.3,
    )
    
    # 通过 API 我们获得了 Kimi 大模型给予我们的回复消息（role=assistant）
    return completion.choices[0].message.content

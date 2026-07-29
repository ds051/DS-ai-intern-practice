import os  # 导入操作系统接口模块，用于读取环境变量
from dotenv import load_dotenv  # 从 dotenv 库中导入加载环境变量的函数
import requests  # 导入 requests 库，用于发送 HTTP 网络请求
import json  # 导入 json 模块，用于处理 API 返回的 JSON 格式数据

# 调用函数，自动读取当前目录下的 .env 文件，将里面的键值对加载到环境变量中
load_dotenv()

# 从环境变量中获取 DeepSeek 的 API 密钥，这样密钥就不会硬编码在代码里
api_key = os.getenv("DEEPSEEK_API_KEY")

# 定义 DeepSeek API 的请求地址（这里使用的是兼容 OpenAI 格式的接口地址）
url = "https://api.deepseek.com/v1/chat/completions"

# 构建 HTTP 请求头，告诉服务器我们要发送 JSON 数据，并带上身份验证的密钥
headers = {
    "Content-Type": "application/json",  # 声明请求体的数据格式为 JSON
    "Authorization": f"Bearer {api_key}"  # 使用 Bearer Token 方式进行 API 鉴权
}

# 构建请求体（Payload），按照 DeepSeek API 的要求组装发送的消息内容
payload = {
    "model": "deepseek-chat",  # 指定调用的模型名称，这里使用默认的对话模型
    "messages": [  # 消息列表，包含对话的历史记录
        {
            "role": "user",  # 角色设定为 user，表示这是用户发送的消息
            "content": "你好"  # 实际发送的消息内容
        }
    ],
    "stream": False  # 设置为 False 表示非流式输出，等待完整回复后一次性返回
}

# 使用 try-except 结构进行异常捕获，防止程序因为网络或接口问题直接崩溃
try:
    # 使用 requests 库向 DeepSeek API 发送 POST 请求，并设置超时时间为 30 秒
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    
    # 检查 HTTP 状态码，如果状态码不是 200（成功），则主动抛出异常
    response.raise_for_status()
    
    # 将服务器返回的 JSON 字符串解析为 Python 字典对象
    result = response.json()
    
    # 从解析后的字典中，提取 AI 回复的具体文本内容并打印到控制台
    print("AI 回复内容：", result["choices"][0]["message"]["content"])

# 捕获 requests 库抛出的网络相关异常（如超时、连接失败、DNS解析错误等）
except requests.exceptions.RequestException as e:
    # 打印友好的网络错误提示信息
    print("发生网络请求错误，详情如下：")
    # 打印具体的异常报错详情，方便排查问题
    print(e)

# 捕获 JSON 解析异常（当服务器返回的不是合法 JSON 格式时触发）
except json.JSONDecodeError as e:
    # 打印 JSON 解析失败的提示信息
    print("API 返回的数据不是有效的 JSON 格式，解析失败：")
    # 打印具体的解析错误详情
    print(e)

# 捕获 KeyError 异常（当 API 返回的 JSON 结构不符合预期，找不到对应字段时触发）
except KeyError as e:
    # 打印字段缺失的提示信息
    print(f"返回的数据结构中缺少预期的字段: {e}，请检查 API 返回内容：")
    # 打印完整的返回结果，方便对比官方文档排查
    print(result)

# 捕获所有其他未被上面 except 块捕获的未知异常
except Exception as e:
    # 打印未知错误的提示信息
    print("发生未知错误，详情如下：")
    # 打印具体的异常类型和报错详情
    print(type(e).__name__, e)
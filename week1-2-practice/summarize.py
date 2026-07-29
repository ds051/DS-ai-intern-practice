import os
import sys
import argparse
from openai import OpenAI
from dotenv import load_dotenv  # 1. 导入加载库

# 2. 自动加载当前目录下的 .env 文件
load_dotenv()

def summarize_text(file_path):
    """读取文件内容并调用 DeepSeek API 生成摘要"""
    
    # 3. 从环境变量获取 API Key (不再硬编码)
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("❌ 错误：未找到 DEEPSEEK_API_KEY 环境变量。")
        print("请检查你的 .env 文件是否在当前目录下，且格式正确。")
        return

    # 4. 初始化 DeepSeek 客户端
    client = OpenAI(
        api_key=api_key, 
        base_url="https://api.deepseek.com"
    )

    # 5. 安全检查：确认文件是否存在
    if not os.path.exists(file_path):
        print(f"❌ 错误：找不到文件 -> {file_path}")
        return

    # 6. 读取文件内容
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return

    if not content.strip():
        print("❌ 错误：文件内容为空。")
        return

    print(f"📖 已读取文件: {file_path} (长度: {len(content)} 字符)")
    print("⏳ 正在生成摘要，请稍候...")

    # 7. 调用 API
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的文本摘要助手。"},
                {"role": "user", "content": f"请对以下内容进行总结，字数控制在200字以内：\n\n{content}"}
            ],
            temperature=0.7
        )
        
        summary = response.choices[0].message.content
        
        # 8. 打印结果
        print("\n" + "="*30)
        print("📝 摘要内容如下：")
        print("="*30)
        print(summary)
        print("="*30 + "\n")
        
        # 9. 保存结果到文件
        output_file = "summary_result.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"✅ 摘要已保存到: {output_file}")

    except Exception as e:
        print(f"❌ API 调用失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DeepSeek 文本摘要工具")
    parser.add_argument('file', type=str, help='要处理的 txt 文件路径')
    args = parser.parse_args()
    
    summarize_text(args.file) 
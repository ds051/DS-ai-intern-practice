import os
import jieba
import jieba.analyse
from datetime import datetime

def analyze_text_files(folder_path):
    """
    读取文件夹内的所有txt文件，统计字数和关键词
    """
    results = []
    # 获取文件夹下所有的txt文件
    txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    
    if not txt_files:
        print("⚠️ 该文件夹下没有找到任何 .txt 文件。")
        return results

    print(f"🔍 正在扫描文件夹: {folder_path}，共发现 {len(txt_files)} 个文本文件...")
    
    for filename in txt_files:
        file_path = os.path.join(folder_path, filename)
        try:
            # 尝试读取文件 (兼容 utf-8 和 gbk 编码)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()

            # 1. 统计字数 (去除空白字符)
            char_count = len(content.replace(" ", "").replace("\n", ""))
            
            # 2. 提取关键词 (TF-IDF算法，提取前5个)
            # jieba.analyse.extract_tags 返回的是列表
            keywords = jieba.analyse.extract_tags(content, topK=5, withWeight=False)
            keywords_str = ", ".join(keywords) if keywords else "无"
            
            results.append({
                "文件名": filename,
                "字数": char_count,
                "关键词": keywords_str
            })
            print(f"  ✅ 已处理: {filename} ({char_count}字)")
            
        except Exception as e:
            print(f"  ❌ 处理 {filename} 时出错: {e}")
            
    return results

def generate_report(results, output_file="汇总报告.txt"):
    """
    生成并保存汇总报告
    """
    if not results:
        return

    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("📊 文本文件分析汇总报告")
    report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 60)
    report_lines.append(f"{'文件名':<20} | {'字数':<8} | {'核心关键词'}")
    report_lines.append("-" * 60)
    
    for res in results:
        # 格式化输出，保证对齐
        line = f"{res['文件名']:<20} | {res['字数']:<8} | {res['关键词']}"
        report_lines.append(line)
        
    report_lines.append("=" * 60)
    report_lines.append(f"共计分析文件: {len(results)} 个")
    
    # 打印到控制台
    print("\n" + "\n".join(report_lines))
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
    print(f"\n📁 汇总报告已成功保存至: {output_file}")

# === 执行入口 ===
if __name__ == "__main__":
    # 设置你要扫描的文件夹路径
    # 如果脚本和txt文件在同一目录，可以直接用 '.'
    target_folder = "."  
    
    # 确保 jieba 的日志不会干扰控制台输出
    jieba.setLogLevel(20) 
    
    # 1. 执行分析
    data = analyze_text_files(target_folder)
    
    # 2. 生成报告
    generate_report(data)
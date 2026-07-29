# main.py
import os
import sys
import pandas as pd
from datetime import datetime

# 导入我们写好的模块
try:
    from data_clean import DataCleaner
    from data_analysis import DataAnalyzer
    from ai_report import AIReportGenerator      # 【新增】导入 AI 模块
    from export_output import OutputExporter      # 【新增】导入导出模块
    import config
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    sys.exit(1)

def process_single_file(file_path, cleaner, analyzer, output_clean_dir):
    """
    处理单个文件的完整流水线：清洗 -> 保存清洗结果 -> 分析
    """
    filename = os.path.basename(file_path)
    print(f"\n{'='*40}")
    print(f"🚀 正在处理: {filename}")
    
    # 1. 执行清洗
    cleaned_df = cleaner.clean(file_path)
    
    if cleaned_df is None or cleaned_df.empty:
        print(f"⚠️ 跳过: {filename} (清洗后无数据)")
        return None, None, None

    # 2. 保存清洗后的数据
    try:
        save_name = f"cleaned_{os.path.splitext(filename)[0]}.csv"
        save_path = os.path.join(output_clean_dir, save_name)
        cleaned_df.to_csv(save_path, index=False, encoding='utf-8-sig')
        print(f"💾 清洗数据已保存至: {save_path}")
    except Exception as e:
        print(f"⚠️ 保存清洗数据失败: {e}")

    # 3. 执行分析
    stats = None
    fault_info = None
    
    try:
        # 【修改】从 config 读取额定转速并传入
        target_speed = getattr(config, 'TARGET_SPEED', 3000)
        result = analyzer.analyze(cleaned_df, filename, target_speed=target_speed)
        
        # 安全解包返回值
        if isinstance(result, tuple) and len(result) == 2:
            stats, fault_info = result
        elif isinstance(result, dict):
            stats = result
            
        # 只有当 stats 存在且是字典时，才打印详细信息
        if stats and isinstance(stats, dict):
            motor_id = stats.get('电机编号', 'Unknown')
            status = fault_info.get('故障原因', '正常') if fault_info else "正常"
            print(f"✅ 分析完成: {motor_id} | 状态: {status}")
            return stats, fault_info, cleaned_df  # 【修改】返回清洗后的 df
        else:
            print(f"⚠️ 分析模块未返回有效统计数据。")
            return None, None, None

    except Exception as e:
        print(f"❌ 分析阶段出错: {e}")
        import traceback
        traceback.print_exc() 
        return None, None, None

def main():
    # 1. 初始化组件
    cleaner = DataCleaner()
    analyzer = DataAnalyzer()
    ai_generator = AIReportGenerator()    # 【新增】初始化 AI 生成器
    exporter = OutputExporter()           # 【新增】初始化导出器

    # 获取输入路径
    input_dir = getattr(config, 'INPUT_FOLDER', './test_data')
    if not os.path.exists(input_dir):
        print(f"❌ 找不到输入文件夹: {input_dir}")
        return

    # 创建专门存放清洗数据的文件夹
    output_clean_dir = "./output_cleaned_data"
    if not os.path.exists(output_clean_dir):
        os.makedirs(output_clean_dir)
        print(f"📂 已创建清洗数据文件夹: {output_clean_dir}")

    # 遍历文件
    all_stats = []
    all_faults = []
    cleaned_dfs = {}  # 【新增】收集清洗后的 DataFrame，用于最终导出
    
    file_list = [f for f in os.listdir(input_dir) if f.endswith(('.csv', '.xlsx'))]
    
    if not file_list:
        print("⚠️ 文件夹内没有找到 CSV 或 Excel 文件。")
        return

    print(f"🔍 发现 {len(file_list)} 个文件待处理...")

    for file_name in file_list:
        file_path = os.path.join(input_dir, file_name)
        # 【修改】接收三个返回值
        stats, fault_info, cleaned_df = process_single_file(file_path, cleaner, analyzer, output_clean_dir)
        
        if stats:
            all_stats.append(stats)
        if fault_info:
            all_faults.append(fault_info)
        if cleaned_df is not None:
            cleaned_dfs[file_name] = cleaned_df

    # 4. 【新增】调用 AI 生成分析报告
    print("\n🤖 正在调用 AI 生成智能分析报告...")
    ai_report_text = ai_generator.generate(all_stats, all_faults)

    # 5. 【修改】统一导出最终结果 (Excel + Markdown)
    exporter.export(all_stats, cleaned_dfs, ai_report_text)

if __name__ == "__main__":
    main()
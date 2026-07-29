# batch_process.py
import os
import pandas as pd
from data_clean import DataCleaner
import config  # 导入配置

def run_batch_process():
    print("=" * 50)
    print("🚀 开始批量处理电机测试数据...")
    print(f"📂 输入路径: {config.INPUT_FOLDER}")
    print(f"💾 输出路径: {config.OUTPUT_FOLDER}")
    print("=" * 50)

    # 1. 检查输入文件夹是否存在
    if not os.path.exists(config.INPUT_FOLDER):
        print(f"❌ 错误：找不到输入文件夹 {config.INPUT_FOLDER}")
        return

    # 2. 获取所有CSV文件
    file_list = [f for f in os.listdir(config.INPUT_FOLDER) if f.endswith('.csv')]
    
    if not file_list:
        print("⚠️ 警告：输入文件夹内没有找到 .csv 文件！")
        return

    print(f"🔍 发现 {len(file_list)} 个待处理文件\n")

    # 3. 初始化清洗器
    cleaner = DataCleaner()
    success_count = 0
    fail_count = 0

    # 4. 遍历处理
    for filename in file_list:
        input_path = os.path.join(config.INPUT_FOLDER, filename)
        output_path = os.path.join(config.OUTPUT_FOLDER, f"clean_{filename}")
        
        try:
            # A. 调用清洗方法 (返回 DataFrame)
            df = cleaner.clean(input_path)
            
            # B. 校验返回值：必须是 DataFrame 且不为空
            if df is not None and isinstance(df, pd.DataFrame) and not df.empty:
                # C. 保存到输出文件夹
                # index=False 避免保存多余的索引列
                df.to_csv(output_path, index=False, encoding='utf-8-sig') 
                print(f"✅ 成功: {filename} -> {output_path}")
                success_count += 1
            else:
                print(f"⚠️ 跳过: {filename} (清洗结果为空或无效)")
                fail_count += 1
                
        except Exception as e:
            print(f"💥 失败: {filename} - 错误详情: {e}")
            fail_count += 1

    # 5. 打印总结
    print("\n" + "=" * 50)
    print(f"🏁 处理完成！成功: {success_count}, 失败: {fail_count}")
    print("=" * 50)

if __name__ == "__main__":
    run_batch_process()
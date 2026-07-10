import pandas as pd
import numpy as np
from datetime import datetime
import re

def clean_motor_test_data(input_file, output_file):
    """
    清洗电机测试脏数据脚本 (最终修正版)
    修改重点：
    1. 缺失值处理：使用“均值填充”策略，而非删除行。
    2. 精度控制：转速/温度 -> 整数；电流 -> 两位小数。
    3. 序号修复：强制重置为连续自然数。
    4. 格式统一：电机编号全大写，日期标准化。
    """
    
    # 1. 读取 CSV 文件
    try:
        # 保持用户要求的 read_csv 格式
        df = pd.read_csv(input_file)
        print(f"✅ 成功读取数据，原始数据量: {len(df)} 条")
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return
    
    # --- 数据清洗核心逻辑 ---

        # 2. 统一电机编号格式 (解决大小写和连字符问题)
    if '电机编号' in df.columns:
        # 定义一个安全的处理函数
        def fix_motor_id(x):
            # 1. 强制转为字符串并去除首尾空格
            s = str(x).strip()
            # 2. 统一转大写 (解决 m-03 -> M-03)
            s = s.upper()
            # 3. 正则补全连字符 (解决 M02 -> M-02)
            # 逻辑：在 M 和 数字之间插入横杠
            s = re.sub(r'(?<=M)(\d)', r'-\1', s)
            return s
        
        # 应用函数
        df['电机编号'] = df['电机编号'].apply(fix_motor_id)
        print("✅ 电机编号已统一格式 (大写+连字符)")

    # 3. 统一日期格式
    def standardize_date(date_str):
        if pd.isna(date_str): return None
        date_str = str(date_str).strip()
        formats = ["%Y/%m/%d", "%Y-%m-%d", "%m/%d/%Y", "%Y年%m月%d日", "%m月%d日"]
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                if "%Y" not in fmt: dt = dt.replace(year=datetime.now().year)
                return dt.strftime("%Y-%m-%d")
            except ValueError: continue
        return None
    df['测试日期'] = df['测试日期'].apply(standardize_date)

    # 4. 提取数值 (去除单位符号)
    def extract_number(val):
        if pd.isna(val): return np.nan
        val = str(val).replace('℃', '').replace('度', '').replace('A', '').replace('rpm', '').strip()
        try: return float(val)
        except ValueError: return np.nan

    numeric_cols = ['实测转速rpm', '温度', '电流A']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(extract_number)

    # 5. 【核心修改】缺失值均值填充 + 精度控制
    # 计算各列均值（忽略NaN）
    mean_rpm = df['实测转速rpm'].mean()
    mean_temp = df['温度'].mean()
    mean_curr = df['电流A'].mean()

    # 填充并格式化：转速/温度取整，电流保留两位
    if '实测转速rpm' in df.columns:
        df['实测转速rpm'] = df['实测转速rpm'].fillna(mean_rpm).round(0).astype(int)
        
    if '温度' in df.columns:
        df['温度'] = df['温度'].fillna(mean_temp).round(0).astype(int)
        
    if '电流A' in df.columns:
        df['电流A'] = df['电流A'].fillna(mean_curr).round(2)

    # 6. 【核心修改】序号重置
    # 不管原来序号是多少，现在从1开始重新排序
    df.reset_index(drop=True, inplace=True)
    # 如果原表有“序号”列，更新它；如果没有，插入到第一列
    if '序号' in df.columns:
        df['序号'] = df.index + 1
    else:
        df.insert(0, '序号', df.index + 1)

    # 7. 保存结果
    try:
        # index=False 防止 pandas 自动生成一列 0,1,2... 的索引
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ 清洗完成！最终数据量: {len(df)} 条")
        print(f"📊 统计信息：")
        print(f"   - 转速平均值(已填充): {int(mean_rpm)} rpm")
        print(f"   - 温度平均值(已填充): {int(mean_temp)} ℃")
        print(f"   - 电流平均值(已填充): {mean_curr:.2f} A")
        print(f"📁 已保存至: {output_file}")
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")

# 执行清洗
if __name__ == "__main__":
    input_csv = "实习练习-电机测试脏数据.csv"
    output_csv = "实习练习-电机测试脏数据cleaned.csv"
    clean_motor_test_data(input_csv, output_csv)
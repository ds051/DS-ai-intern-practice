import pandas as pd
import numpy as np
from datetime import datetime

def clean_motor_test_data(input_file, output_file):
    """
    清洗电机测试脏数据脚本
    清洗目标：
    1. 统一日期格式为 YYYY-MM-DD
    2. 统一温度单位为 ℃，电流单位为 A
    3. 去除完全重复的行
    4. 处理缺失值（关键列缺失则删除，非关键列缺失则标记或填充）
    """
    
    # 1. 读取CSV文件
    try:
        df = pd.read_csv(input_file)
        print(f"✅ 成功读取数据，原始数据量: {len(df)} 条")
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return
    
    # 2. 去除完全重复的行
    df.drop_duplicates(inplace=True)
    print(f"🔄 去重后数据量: {len(df)} 条")
    
    # 3. 统一日期格式为 YYYY-MM-DD
    def standardize_date(date_str):
        if pd.isna(date_str):
            return None
        date_str = str(date_str).strip()
        formats = [
            "%Y/%m/%d",
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%Y年%m月%d日",
            "%m月%d日"
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                # 处理只有月日的情况，补充当前年份
                if "%Y" not in fmt:
                    dt = dt.replace(year=datetime.now().year)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        print(f"⚠️ 无法解析的日期格式: {date_str}")
        return None
    
    df['测试日期'] = df['测试日期'].apply(standardize_date)
    
    # 4. 统一温度单位，去除 '℃' 和 '度' 等字符，保留数值
    def standardize_temperature(temp_str):
        if pd.isna(temp_str):
            return np.nan
        temp_str = str(temp_str).strip().replace('℃', '').replace('度', '').strip()
        try:
            return float(temp_str)
        except ValueError:
            return np.nan
            
    df['温度'] = df['温度'].apply(standardize_temperature)
    
    # 5. 统一电流单位，去除 'A' 等字符，保留数值
    def standardize_current(current_str):
        if pd.isna(current_str):
            return np.nan
        current_str = str(current_str).strip().replace('A', '').strip()
        try:
            return float(current_str)
        except ValueError:
            return np.nan
            
    df['电流A'] = df['电流A'].apply(standardize_current)
    
    # 6. 处理实测转速中的异常值（如 '异常' 等文本），转为NaN
    def standardize_rpm(rpm_str):
        if pd.isna(rpm_str):
            return np.nan
        rpm_str = str(rpm_str).strip()
        try:
            return float(rpm_str)
        except ValueError:
            return np.nan
            
    df['实测转速rpm'] = df['实测转速rpm'].apply(standardize_rpm)
    
    # 7. 处理缺失值
    # 关键列：测试日期、电机编号、额定转速rpm、实测转速rpm
    # 如果关键列缺失，直接删除该行
    key_columns = ['测试日期', '电机编号', '额定转速rpm', '实测转速rpm']
    before_drop = len(df)
    df.dropna(subset=key_columns, inplace=True)
    print(f"🗑️ 删除关键列缺失的记录数: {before_drop - len(df)} 条")
    
    # 非关键列（温度、电流A、测试员、备注）缺失，保留记录
    # 可以在这里选择填充，例如温度缺失填充为均值，这里保留NaN以便后续分析
    # df['温度'].fillna(df['温度'].mean(), inplace=True)
    
    # 8. 保存清洗后的数据
    try:
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ 清洗完成！最终数据量: {len(df)} 条")
        print(f"📁 已保存至: {output_file}")
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")

# 执行清洗
if __name__ == "__main__":
    input_csv = "实习练习-电机测试脏数据(2).csv"
    output_csv = "实习练习-电机测试脏数据(2)_cleaned.csv"
    clean_motor_test_data(input_csv, output_csv)

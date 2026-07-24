import pandas as pd
import numpy as np
from datetime import datetime
import re
import os

# 【关键修复】显式导入配置文件
try:
    import config
except ImportError:
    print("⚠️ 警告：未找到 config.py，将使用默认硬编码参数运行。")
    class DefaultConfig:
        UNITS_TO_REMOVE = ['℃', '度', 'A', 'rpm', ' ']
        DATE_FORMATS = ["%Y/%m/%d", "%Y-%m-%d", "%Y年%m月%d日"]
        PRECISION_CONFIG = {'转速': 0, '温度': 0, '电流': 2}
    config = DefaultConfig()

class DataCleaner:
    """
    电机测试数据清洗器
    职责：负责单份CSV文件的读取、清洗、格式化，并返回清洗后的DataFrame
    """

    def __init__(self):
        self.units_to_remove = getattr(config, 'UNITS_TO_REMOVE', ['℃', '度', 'A', 'rpm', ' '])
        self.date_formats = getattr(config, 'DATE_FORMATS', ["%Y/%m/%d", "%Y-%m-%d"])
        self.precision_config = getattr(config, 'PRECISION_CONFIG', {'转速': 0, '温度': 0, '电流': 2})

    def clean(self, file_path):
        """执行清洗流程：输入文件路径，输出清洗后的DataFrame"""
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return None

        try:
            # 尝试多种编码读取
            df = None
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
            for enc in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=enc)
                    break 
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise ValueError("无法识别文件编码")

            # 核心清洗步骤
            df = self._fix_motor_ids(df)
            df = self._standardize_dates(df)
            df = self._extract_and_fill_numerics(df)
            df = self._reset_index(df)

            return df

        except Exception as e:
            print(f"💥 清洗失败 [{os.path.basename(file_path)}]: {e}")
            return None

    # ... (以下私有方法 _fix_motor_ids, _standardize_dates 等保持不变) ...
    def _fix_motor_ids(self, df):
        if '电机编号' not in df.columns: return df
        def fix_id(x):
            s = str(x).strip().upper()
            return re.sub(r'(?<=M)(\d)', r'-\1', s) if 'M' in s else s
        df['电机编号'] = df['电机编号'].apply(fix_id)
        return df

    def _standardize_dates(self, df):
        if '测试日期' not in df.columns: return df
        def parse_date(date_str):
            if pd.isna(date_str): return None
            s = str(date_str).strip()
            for fmt in self.date_formats:
                try:
                    return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
                except ValueError:
                    continue
            return s 
        df['测试日期'] = df['测试日期'].apply(parse_date)
        return df

    def _extract_and_fill_numerics(self, df):
        target_cols = ['实测转速rpm', '温度', '电流A']
        for col in target_cols:
            if col not in df.columns: continue
            
            def to_num(val):
                if pd.isna(val): return np.nan
                s = str(val)
                for unit in self.units_to_remove:
                    s = s.replace(unit, '')
                try: return float(s)
                except: return np.nan
                
            df[col] = df[col].apply(to_num)
            
            # 均值填充
            mean_val = df[col].mean()
            df[col] = df[col].fillna(mean_val)
            
            # 精度控制
            for key, precision in self.precision_config.items():
                if key in col:
                    df[col] = df[col].round(precision)
                    if precision == 0: df[col] = df[col].astype(int)
                    break
        return df

    def _reset_index(self, df):
        df.reset_index(drop=True, inplace=True)
        if '序号' in df.columns:
            df['序号'] = df.index + 1
        else:
            df.insert(0, '序号', df.index + 1)
        return df
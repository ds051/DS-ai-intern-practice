import pandas as pd
import numpy as np
import config

class DataAnalyzer:
    """
    统计分析模块
    职责：接收【单个】清洗后的DataFrame，计算关键指标，识别故障电机。
    注意：此模块不负责遍历文件夹，只负责处理传入的数据。
    """

    def __init__(self):
        # 从 config.py 读取业务阈值，实现配置与逻辑分离
        self.thresholds = getattr(config, 'ANALYSIS_THRESHOLDS', {
            'max_temp_limit': 85,            # 最高温度报警阈值 (摄氏度)
            'current_spike_limit': 15,       # 电流突变/峰值报警阈值 (安培)
            'speed_deviation_limit': 50,     # 平均转速偏差报警阈值 (rpm)
            'speed_std_limit': 30,           # 转速标准差(波动)报警阈值 (rpm)
            'stall_speed_limit': 10,         # 堵转判定：转速低于此值 (rpm)
            'stall_current_limit': 10        # 堵转判定：电流高于此值 (安培)
        })

    def analyze(self, df: pd.DataFrame, filename: str, target_speed: float = 0.0):
        """
        执行单文件分析
        :param df: 清洗后的 DataFrame
        :param filename: 原始文件名（用于标记数据来源）
        :param target_speed: 目标转速/额定转速，用于计算转速偏差
        :return: dict (统计指标), dict or None (故障信息)
        """
        if df is None or df.empty:
            return None, None

        # 1. 计算单台电机的统计指标
        stats = self._calculate_metrics(df, target_speed)
        
        # 将文件名注入到统计结果中，方便后续导出时知道是哪份文件
        stats['文件名'] = filename

        # 2. 判定是否为故障电机
        is_fault, fault_reason = self._check_fault(stats)
        
        fault_info = None
        if is_fault:
            fault_info = {
                '文件名': filename,
                '电机编号': stats.get('电机编号', 'Unknown'),
                '故障原因': fault_reason,
                '最高温度': stats['最高温度'],
                '最大电流': stats['最大电流'],
                '平均转速偏差': stats['平均转速偏差']
            }

        return stats, fault_info

    def _calculate_metrics(self, df, target_speed):
        """计算具体的统计指标"""
        # 【防御性编程】确保数值列是数字类型，防止因为Excel里的文本格式导致计算报错
        numeric_cols = ['实测转速rpm', '温度', '电流A']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 提取有效数据
        speed_series = df['实测转速rpm'] if '实测转速rpm' in df.columns else pd.Series([0])
        temp_series = df['温度'] if '温度' in df.columns else pd.Series([0])
        current_series = df['电流A'] if '电流A' in df.columns else pd.Series([0])

        # 1. 计算平均转速偏差 (实际平均值 - 目标值)
        avg_speed = speed_series.mean()
        speed_deviation = round(avg_speed - target_speed, 2)

        # 2. 计算温度区间 (最低温, 最高温)
        min_temp = round(temp_series.min(), 2)
        max_temp = round(temp_series.max(), 2)
        temp_range = f"{min_temp}℃ ~ {max_temp}℃"

        # 3. 其他基础指标
        std_speed = round(speed_series.std(), 2)
        max_current = round(current_series.max(), 2)
        
        # 异常条数：包含空值的行数（作为数据质量监控）
        anomaly_count = int(df[numeric_cols].isnull().any(axis=1).sum()) 

        # 获取电机编号（假设同一文件内编号一致，取第一个）
        motor_id = df['电机编号'].iloc[0] if '电机编号' in df.columns and not df.empty else "未知"

        return {
            '电机编号': motor_id,
            '样本数': len(df),
            '平均转速': round(avg_speed, 2),
            '平均转速偏差': speed_deviation,
            '转速标准差': std_speed,
            '温度区间': temp_range,
            '最高温度': max_temp,
            '最大电流': max_current,
            '异常条数': anomaly_count
        }

    def _check_fault(self, stats):
        """
        故障判定逻辑
        :return: (是否故障, 故障原因字符串)
        """
        reasons = []
        
        # 规则1：温度过高
        if stats['最高温度'] > self.thresholds['max_temp_limit']:
            reasons.append(f"温度过高({stats['最高温度']}℃)")
            
        # 规则2：电流过大
        if stats['最大电流'] > self.thresholds['current_spike_limit']:
            reasons.append(f"电流过大({stats['最大电流']}A)")
            
        # 规则3：平均转速偏差过大
        if abs(stats['平均转速偏差']) > self.thresholds['speed_deviation_limit']:
            reasons.append(f"转速偏差过大(Δ={stats['平均转速偏差']}rpm)")

        # 规则4：转速波动剧烈 (标准差过大)
        if stats['转速标准差'] > self.thresholds['speed_std_limit']:
            reasons.append(f"转速波动大(σ={stats['转速标准差']})")

        # 规则5：堵转判定 (转速极低 + 电流过大)
        if (stats['平均转速'] < self.thresholds['stall_speed_limit'] and 
            stats['最大电流'] > self.thresholds['stall_current_limit']):
            reasons.append(f"疑似堵转(转速={stats['平均转速']}rpm, 电流={stats['最大电流']}A)")

        if reasons:
            return True, "; ".join(reasons)
        else:
            return False, "正常"

if __name__ == "__main__":
    print("⚠️ 这是一个工具模块，请通过 main.py 调用。")
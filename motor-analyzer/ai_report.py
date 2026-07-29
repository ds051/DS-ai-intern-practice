import json
import os
from openai import OpenAI
import config

class AIReportGenerator:
    def __init__(self):
        # 从 config 获取配置，如果 config 没配好，这里会报错，请确保 config.py 已更新
        self.api_key = getattr(config, 'DEEPSEEK_API_KEY', None)
        self.base_url = getattr(config, 'DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
        
        if not self.api_key:
            print("⚠️ 警告: 未找到 DEEPSEEK_API_KEY，请检查 .env 文件或 config.py")

    def _sanitize_data(self, obj):
        """
        【核心修复】递归转换数据类型，解决 pandas/numpy 类型无法 JSON 序列化的问题
        """
        if isinstance(obj, dict):
            return {k: self._sanitize_data(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._sanitize_data(i) for i in obj]
        elif hasattr(obj, 'item'): 
            # 这是 numpy/pandas 类型的特征，转为 python 原生类型
            return obj.item()
        else:
            return obj

    def generate(self, all_stats, all_faults):
        """
        调用 AI 生成报告
        """
        if not self.api_key:
            return "❌ 错误：API Key 未配置，无法生成 AI 报告。"

        if not all_faults:
            return "🟢 **系统状态：一切正常**\n\n所有电机运行数据均在正常阈值范围内，未发现异常，无需检修。"

        # 1. 构造发给 AI 的上下文数据
        prompt_data = {
            "total_motors": len(all_stats),
            "fault_motors": all_faults,
            "analysis_thresholds": getattr(config, 'ANALYSIS_THRESHOLDS', {})
        }

        # 【关键修复】在这里进行数据清洗，把 int64 转为 int
        safe_prompt_data = self._sanitize_data(prompt_data)

        # 2. 构造 Prompt
        system_prompt = (
            "你是一个专业的电机故障诊断专家。请根据提供的JSON数据生成一份简报。\n"
            "要求：\n"
            "1. 列出所有有问题的电机编号。\n"
            "2. 针对每个故障（如温度高、电流大、转速偏差），结合工程经验推测可能的物理原因（如轴承磨损、负载过大、散热风扇损坏等）。\n"
            "3. 给出具体的复测或检修建议。\n"
            "4. 语气专业、客观。"
        )

        user_prompt = f"以下是电机监测数据摘要：\n{json.dumps(safe_prompt_data, indent=2, ensure_ascii=False)}"

        try:
            # 3. 调用 DeepSeek API (兼容 OpenAI SDK)
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            
            response = client.chat.completions.create(
                model="deepseek-chat",  # DeepSeek 的标准模型名称
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content

        except Exception as e:
            return f"❌ AI 报告生成失败: {str(e)}"
import os
from dotenv import load_dotenv

# 自动加载 .env 文件中的环境变量
load_dotenv()

# 获取当前文件的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ================= 1. 路径配置 =================
# 输入文件夹：存放原始CSV文件的地方
INPUT_FOLDER = os.path.join(BASE_DIR, "test_data") 

# 输出文件夹：清洗后文件保存的地方
OUTPUT_FOLDER = os.path.join(BASE_DIR, "cleaned_data")

# ================= 2. 业务规则配置 =================
# 需要去除的单位符号
UNITS_TO_REMOVE = ['℃', '度', 'A', 'rpm', ' '] 

# 支持的日期格式列表
DATE_FORMATS = [
    "%Y/%m/%d", 
    "%Y-%m-%d", 
    "%Y年%m月%d日",
    "%Y.%m.%d"
]

# 数值列的精度控制 (保留几位小数)
PRECISION_CONFIG = {
    '转速': 0,   # 0表示取整
    '温度': 0,   # 0表示取整
    '电流': 2    # 2表示保留两位小数
}

# ================= 3. 分析阈值与参数配置 =================
# 电机额定转速 (用于计算转速偏差)
TARGET_SPEED = 3000 

# 这些数值决定了什么样的电机被判定为“可疑”
ANALYSIS_THRESHOLDS = {
    'max_temp_limit': 85,            # 最高温度超过 85度 报警
    'current_spike_limit': 15,       # 电流超过 15A 报警
    'speed_deviation_limit': 50,     # 平均转速偏差超过 50 报警
    'speed_std_limit': 30,           # 转速标准差超过 30 报警（代表运行不稳定）
    'stall_speed_limit': 10,         # 堵转判定：转速低于此值 (rpm)
    'stall_current_limit': 10        # 堵转判定：电流高于此值 (安培)
}

# ================= 4. AI 报告生成配置 (适配 DeepSeek) =================
# 从环境变量中读取 DeepSeek 的 API Key
# 注意：请确保你的 .env 文件里写的是 DEEPSEEK_API_KEY=sk-...
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# DeepSeek 的官方 API 地址
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# 使用的模型名称 (DeepSeek 通常使用 deepseek-chat 或 deepseek-reasoner)
DEEPSEEK_MODEL = "deepseek-chat"
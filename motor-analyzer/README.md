motor-analyzer 电机测试数据分析工具
 
项目介绍
 
本工具模拟产线工程师日常工作，自动批量处理电机测试CSV原始脏数据。
实现数据清洗、指标统计、异常电机筛查，调用DeepSeek API自动生成专业分析报告，替代人工整理数据、撰写日报。
 
  安装依赖库
  
pip install pandas openpyxl python-dotenv requests
 
在项目根目录新建  .env  文件，填入DeepSeek密钥
  
DEEPSEEK_API_KEY=你的API密钥
  
 
运行命令
  
python main.py ./test_data
 
 ./test_data  存放所有原始CSV测试文件，可修改为任意文件夹路径
 
输入规范
 
- 输入：文件夹，内部包含多份电机测试  .csv  原始数据
- 数据特点：产线导出脏数据，存在空行、异常字符、格式混乱，程序自带清洗逻辑
 
程序功能
 
1. 批量读取文件夹内全部CSV文件
2. 统一清洗原始脏数据（封装可复用清洗函数）
3. 统计指标：平均转速偏差、温度区间、异常记录数量
4. 自动标记可疑电机：转速偏差超标、高温、堵转设备
5. 请求DeepSeek API（原生JSON Output模式）生成分析报告
6. 汇总所有结果导出Excel
 
输出内容
 
运行结束后自动生成：
 
1.  result_summary.xlsx ：全部电机统计数据、异常标记
2.  final_reports ：AI生成的文字分析报告（故障推测、复测/检修建议）
 
项目目录结构
 
plaintext
  
motor-analyzer/
├── main.py                # 程序入口，串联完整流程
├── config.py              # 全局配置读取
├── data_clean.py          # 数据清洗函数
├── analyzer.py            # 指标统计、异常判断
├── llm_api.py             # DeepSeek API调用
├── exporter.py            # 结果导出Excel
├── .env                   # 密钥配置（不上传git）
├── README.md
└── test_data/             # CSV原始数据目录
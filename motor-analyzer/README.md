电机测试数据分析工具
 
项目简介
 
自动化批量处理产线电机测试原始CSV脏数据，完成数据清洗、指标统计、异常电机识别，并调用DeepSeek API自动生成故障分析报告，替代人工整理数据、编写日报。
 
功能列表
 
1. 批量读取文件夹内所有CSV测试文件
2. 原始数据清洗（封装可复用清洗函数）
3. 统计转速偏差、温度范围，自动标记异常电机
4. 调用AI生成分析报告，提供检修与复测建议
5. 异常容错：单个文件处理失败不终止整体流程
 
环境安装
 
 pip install pandas python-dotenv openpyxl requests
 
 
在项目根目录新建  .env  文件填写密钥：
 
env
  
DEEPSEEK_API_KEY=你的密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com
 
 
⚠️ .env 文件加入.gitignore，严禁上传密钥
 
运行命令
 
 python main.py --input "./test_data"
 
 
参数：
 --input ：存放CSV原始数据的文件夹路径
 
文件夹名称带空格示例： python main.py --input "./test data" 
 
目录结构
   
├── main.py              # 程序入口
├── config.py            # 配置读取
├── data_clean.py        # 数据清洗
├── data_analysis.py     # 指标统计、异常判断
├── export_output.py     # 结果导出
├── ai_report.py         # AI接口调用，生成报告
├── test_data/           # 原始CSV输入目录
├── output_cleaned_data/ # 清洗后CSV
├── final_reports/       # Excel汇总表、AI分析报告
├── .gitignore
└── README.md
 
 
输出内容
 
1.  output_cleaned_data/ ：清洗完成的CSV文件
2.  final_reports/summary_result.xlsx ：电机数据汇总表，标注异常设备
3.  final_reports/analysis_report.md ：AI生成产线分析报告
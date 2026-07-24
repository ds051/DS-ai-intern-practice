import os
import pandas as pd
from datetime import datetime

class OutputExporter:
    """
    结果导出模块
    职责：将统计数据、清洗数据和 AI 报告导出为 Excel 和 Markdown 文件。
    """
    def __init__(self, output_dir="./final_reports"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def export(self, all_stats, cleaned_dfs, ai_report_text):
        """
        执行导出操作
        :param all_stats: 列表，包含所有电机的统计字典
        :param cleaned_dfs: 字典，{文件名: 清洗后的DataFrame}
        :param ai_report_text: 字符串，AI 生成的 Markdown 报告
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 导出 Excel (包含两个 Sheet)
        excel_path = os.path.join(self.output_dir, f"电机检测报告_{timestamp}.xlsx")
        try:
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                # Sheet 1: 统计汇总表
                if all_stats:
                    stats_df = pd.DataFrame(all_stats)
                    stats_df.to_excel(writer, sheet_name='电机统计汇总', index=False)
                
                # Sheet 2: 原始清洗数据合并
                if cleaned_dfs:
                    # 给每个 df 加上来源文件名，然后拼接
                    for fname, df in cleaned_dfs.items():
                        df_copy = df.copy()
                        df_copy.insert(0, '来源文件', fname)
                        # 写入同一个 sheet，追加模式
                        df_copy.to_excel(writer, sheet_name='清洗后原始数据', index=False, startrow=0)
                        
            print(f"✅ Excel 报告已生成: {excel_path}")
        except Exception as e:
            print(f"❌ Excel 导出失败: {e}")

        # 2. 导出 Markdown 报告
        md_path = os.path.join(self.output_dir, f"AI分析报告_{timestamp}.md")
        try:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(ai_report_text)
            print(f"✅ Markdown 报告已生成: {md_path}")
        except Exception as e:
            print(f"❌ Markdown 导出失败: {e}")

        return excel_path, md_path
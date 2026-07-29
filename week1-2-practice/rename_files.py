import os
import sys
from datetime import datetime

def main():
    # 1. 校验命令行参数
    if len(sys.argv) != 2:
        print("使用格式：python rename_files.py 目标文件夹路径")
        print("示例：python rename_files.py ./test_dir")
        return
    target_dir = sys.argv[1]

    # 2. 校验文件夹是否存在
    if not os.path.isdir(target_dir):
        print(f"错误：文件夹 [{target_dir}] 不存在，请检查路径")
        return

    date_prefix = datetime.now().strftime("%Y%m%d")
    rename_list = []

    # 筛选：只保留文件，跳过子文件夹、已带日期前缀的文件
    for name in os.listdir(target_dir):
        full_path = os.path.join(target_dir, name)
        if os.path.isfile(full_path) and not name.startswith(f"{date_prefix}_"):
            rename_list.append(name)

    # 无待改名文件直接退出
    if not rename_list:
        print("当前文件夹没有需要重命名的文件")
        return

    # 3. 打印改名预览清单（任务强制要求）
    print("\n========== 改名预览清单 ==========")
    for old_name in rename_list:
        new_name = f"{date_prefix}_{old_name}"
        print(f"{old_name}  →  {new_name}")
    print("==================================\n")

    # 4. 用户确认，输入y才执行
    confirm = input("确认执行批量重命名？输入 y 确认，其他字符取消：").strip().lower()
    if confirm != "y":
        print("操作已取消，文件未改动")
        return

    # 5. 执行重命名并统计数量
    success_count = 0
    for old_name in rename_list:
        old_path = os.path.join(target_dir, old_name)
        new_name = f"{date_prefix}_{old_name}"
        new_path = os.path.join(target_dir, new_name)
        os.rename(old_path, new_path)
        success_count += 1

    print(f"\n执行完成！成功重命名 {success_count} 个文件")

if __name__ == "__main__":
    main()
import json
from src import error_handler

def load_summary():
    """
    加载指定存档名的世界观和剧情摘要，未指定则列出所有存档供选择。
    返回 (world_description, summary_text, save_name, last_conversation) 或 (None, None, None, None)
    """
    import os
    data_dir = "data"
    if not os.path.exists(data_dir):
        print("未找到存档目录，需要先进行游戏存档")
        return None, None, None,None,None
    files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    if not files:
        print("未找到任何存档文件，需要先进行游戏存档")
        return None, None, None,None,None
    while True:
            print("可用存档：")
            for idx, f in enumerate(files):
                print(f"[{idx+1}] {f[:-5]}")
            print("[0] 取消")
            try:
                choice = int(input("请输入要操作的存档编号："))
                if choice == 0:
                    print("已取消")
                    return None, None, None,None,None
                if not (1 <= choice <= len(files)):
                    print("编号超出范围，请重新输入")
                    continue
                save_name = files[choice-1][:-5]
                action = input(f"对存档 [{save_name}] 请输入操作（1载入/2删除）：").strip()
                if action == "2":
                    confirm = input(f"确定要删除存档 [{save_name}] 吗？此操作不可恢复！（y/n）：").lower()
                    if confirm == "y":
                        os.remove(f"data/{save_name}.json")
                        print(f"存档 [{save_name}] 已删除。")
                        files.pop(choice-1)
                        if not files:
                            print("已无存档。")
                            return None, None, None,None,None
                        save_name = None
                        os.system('cls')  # 清屏
                        continue  # 回到存档选择
                    else:
                        print("已取消删除。")
                        save_name = None
                        os.system('cls')
                        continue
                elif action == "1":
                    break  # 载入
                else:
                    print("无效操作，请输入1或2。")
                    save_name = None
                    continue
            except Exception:
                print("输入有误，取消操作")
                return None, None, None,None,None
    file_path = f"data/{save_name}.json"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            last_conversation = data.get("last_conversation")
            role = data.get("role")
            return data["world_description"], data["latest_summary"], save_name, last_conversation, role
    except FileNotFoundError:
        print("未找到指定存档文件")
        return None, None, None, None,None
    except json.JSONDecodeError:
        error_handler.handle_llm_error(Exception("存档文件格式错误"))
        return None, None, None, None,None
    except Exception as e:
        error_handler.handle_llm_error(e)

import json
from src import error_handler

def load_summary(save_name=None):
    """
    加载指定存档名的世界观和剧情摘要，未指定则列出所有存档供选择。
    返回 (world_description, summary_text, save_name) 或 (None, None, None)
    """
    import os
    data_dir = "data"
    if not os.path.exists(data_dir):
        print("未找到存档目录，需要先进行游戏存档")
        return None, None, None
    files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    if not files:
        print("未找到任何存档文件，需要先进行游戏存档")
        return None, None, None
    if not save_name:
        print("可用存档：")
        for idx, f in enumerate(files):
            print(f"[{idx+1}] {f[:-5]}")
        try:
            choice = int(input("请输入要读取的存档编号："))
            save_name = files[choice-1][:-5]
        except Exception:
            print("输入有误，取消读取")
            return None, None, None
    file_path = f"data/{save_name}.json"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data["world_description"], data["latest_summary"], save_name
    except FileNotFoundError:
        print("未找到指定存档文件")
        return None, None, None
    except json.JSONDecodeError:
        error_handler.handle_llm_error(Exception("存档文件格式错误"))
        return None, None, None
    except Exception as e:
        error_handler.handle_llm_error(e)
        return None, None, None

import json
from src import error_handler

def load_summary():
    """
    从 summary.json 加载世界观和剧情摘要
    返回 (world_description, summary_text) 或 (None, None) 如果加载失败
    """
    try:
        with open("data/summary.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data["world_description"], data["latest_summary"]
    except FileNotFoundError:
        print("未找到存档文件，需要先进行游戏存档")
        return None, None
    except json.JSONDecodeError:
        error_handler.handle_llm_error(Exception("存档文件格式错误"))
        return None, None
    except Exception as e:
        error_handler.handle_llm_error(e)
        return None, None

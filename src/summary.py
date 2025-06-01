import openai
from dotenv import load_dotenv
import os
import json
from src.error_handler import error_handler


# 加载环境变量
load_dotenv()
client = openai.OpenAI(
    base_url=os.getenv("API_URL"),
    api_key=os.getenv("API_KEY")
)

def get_save_name(summary_text):
    """
    使用 LLM 根据剧情摘要自动生成存档名
    """
    try:
        response = client.chat.completions.create(
            model=os.getenv("MODEL_NAME"),
            messages=[
                {"role": "system", "content": "请根据以下剧情摘要为本次存档起一个简洁有趣的中文标题（不超过10字）："},
                {"role": "user", "content": summary_text}
            ],
            temperature=0.5
        )
        save_name = response.choices[0].message.content.strip().replace(" ", "")
        for ch in r'\\/:*?\"<>|':
            save_name = save_name.replace(ch, "")
        return save_name or "未命名存档"
    except Exception as e:
        error_handler.handle_llm_error(e)
        return "未命名存档"

def summarize_and_save(messages, world_description, save_name=None, role=None):
    """
    在满足轮数后调用 LLM 对聊天内容进行总结，并保存到 JSON 文件
    """
    try:
        # 调用 LLM 生成总结
        response = client.chat.completions.create(
            model=os.getenv("MODEL_NAME"),
            messages=[
                {"role": "system", "content": "请对以下对话历史进行简洁总结，提取关键剧情发展和和用户的状态，身份和物品档："},
                {"role": "user", "content": "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])}
            ],
            temperature=0.5
        )
        summary_text = response.choices[0].message.content

        # 提取世界观要素

        # 自动生成或使用提供的存档名
        if not save_name:
            save_name = get_save_name(summary_text)

        # 保存总结和世界观到 JSON 文件，并保存最后一次对话和角色
        last_conversation = messages[-1] if messages else None
        save_summary_to_json(summary_text, world_description, save_name, last_conversation, role)

        return summary_text, save_name

    except Exception as e:
        error_handler.handle_llm_error(e)
        return "", None

def save_summary_to_json(summary_text, world_description, save_name, last_conversation=None, role=None):
    """
    将总结内容和世界观保存到独立 JSON 文件，并保存最后一次对话和角色
    """
    summary_data = {
        "latest_summary": summary_text,
        "world_description": world_description,
        "last_conversation": last_conversation,
        "role": role
    }

    # 确保 data 目录存在
    os.makedirs("data", exist_ok=True)
    file_path = f"data/{save_name}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)

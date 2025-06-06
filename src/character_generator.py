import openai
import os
from dotenv import load_dotenv
from src.error_handler import error_handler

load_dotenv()
client = openai.OpenAI(
    base_url=os.getenv("API_URL"),
    api_key=os.getenv("API_KEY")
)

def generate_character(world_description):

    system_prompt = (
    "你是一个角色设定生成器，请根据用户的简短描述拓展出一个详细的角色设定，"
    "严格按照如下格式输出，不要添加多余内容，不要输出解释：\n"
    "姓名:\n"
    "职业:\n"
    "性别:\n"
    "年龄:\n"
    "能力:\n"
    "=====\n"
    "人物具体介绍:\n"
    "关系:\n"
    "请务必让角色的设定、背景、能力等与以下世界观保持一致：\n"
    f"{world_description}\n"
    "【示例】\n"
    "姓名: 李明\n"
    "职业: 魔法师\n"
    "性别: 男\n"
    "年龄: 28\n"
    "能力: 精通火系魔法\n"
    "=====\n"
    "人物具体介绍: 李明出生于魔法世家，性格坚毅，善于思考。\n"
    "关系: 与导师关系密切，曾与主角有过合作。\n"
    "请严格按照上述格式输出，不要输出任何解释或多余内容。"
)
    """
    根据用户输入的提示词生成角色设定，并允许用户多次生成或自定义修改
    """
    prompt = input("请输入角色提示词（如：一个来自东方的神秘法师）：")
    while True:
        try:
            response = client.chat.completions.create(
                model=os.getenv("MODEL_NAME"),
                messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            character = response.choices[0].message.content
            print(f"\n生成的角色设定：\n{character}\n")
            choice = input("是否接受这个角色？(1接受/2重新生成/3自定义修改)：")
            if choice == "1":
                return character
            elif choice == "2":
                continue  # 重新生成
            elif choice == "3":
                prompt = input("请输入修改后的提示词：")
            else:
                print("无效输入，请重新选择")
        except Exception as e:
            error_handler.handle_llm_error(e)
            return None

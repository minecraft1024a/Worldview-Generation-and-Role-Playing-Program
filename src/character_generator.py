import openai
import os
from dotenv import load_dotenv
from src.error_handler import error_handler

load_dotenv()
client = openai.OpenAI(
    base_url=os.getenv("API_URL"),
    api_key=os.getenv("API_KEY")
)

def generate_character():
    """
    根据用户输入的提示词生成角色设定，并允许用户多次生成或自定义修改
    """
    prompt = input("请输入角色提示词（如：一个来自东方的神秘法师）：")
    while True:
        try:
            response = client.chat.completions.create(
                model=os.getenv("MODEL_NAME"),
                messages=[
                    {"role": "system", "content": "你是一个角色设定生成器，请根据用户的简短描述生成一个详细的角色设定，包括背景、性格和能力"},
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

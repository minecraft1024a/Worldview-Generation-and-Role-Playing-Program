import openai
from dotenv import load_dotenv
import os

load_dotenv()
# 加载环境变量
client = openai.OpenAI(
    base_url=os.getenv("API_URL"),
    api_key=os.getenv("API_KEY")
)

def start_role_play(world_description):
    client = openai.OpenAI(
        base_url=os.getenv("API_URL"),
        api_key=os.getenv("API_KEY")
    )
    
    role = input("请输入你要扮演的角色（例如：冒险者、法师、商人）：")
    
    messages = [
        {"role": "system", "content": f"你是一个角色扮演游戏大师，根据以下世界观进行角色扮演：\n\n{world_description}"},
        {"role": "user", "content": f"""我扮演{role}，请开始角色扮演游戏,角色扮演的时候按照以下对话格式:
        时间:
        地点:
        情景:
        ================
        用户状态:
        ================
        用户物品栏:
        ================
        用户接下来的选择(使用数字标记):"""}

    ]
    # 初始化对话历史
    
    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=messages,
        temperature=0.7
    )
    
    print(response.choices[0].message.content)
    
    while True:
        user_input = input("你的行动（输入'退出'结束游戏）：")
        if user_input == '退出':
            break
        # 添加用户输入到对话历史
        messages.append({"role": "user", "content": user_input})
        response = client.chat.completions.create(
            model=os.getenv("MODEL_NAME"),
            messages=messages,
            temperature=0.7
        )
        # 添加AI响应到对话历史
        messages.append({"role": "assistant", "content": response.choices[0].message.content})
        print(response.choices[0].message.content)

import openai
from dotenv import load_dotenv
import os
from src import error_handler

load_dotenv()
client = openai.OpenAI(
    base_url=os.getenv("API_URL"),
    api_key=os.getenv("API_KEY")
)

def start_role_play(world_description):
    role = input("请输入你要扮演的角色（例如：冒险者、法师、商人）：")

    # 初始设定
    system_prompt = (
        "你是一个角色扮演游戏大师，请严格按照如下格式输出每一轮内容：\n"
        "用户身份：\n"
        "时间:\n"
        "地点:\n"
        "情景:\n"
        "===============\n"
        "用户状态:\n"
        "===============\n"
        "用户物品栏:\n"
        "===============\n"
        "用户接下来的选择(使用数字标记):\n"
        "【示例】\n"
        "用户身份：冒险者\n"
        "时间: 清晨\n"
        "地点: 森林入口\n"
        "情景: 你站在幽深的森林入口，阳光透过树叶洒下斑驳光影。\n"
        "===============\n"
        "用户状态: 精力充沛，装备齐全\n"
        "===============\n"
        "用户物品栏: 长剑x1，面包x2，水壶x1\n"
        "===============\n"
        "用户接下来的选择(使用数字标记):\n"
        "1. 进入森林\n"
        "2. 检查装备\n"
        "3. 休息片刻\n"
        "请严格按照上述格式输出，并根据玩家的行动推进剧情。根据以下世界观进行角色扮演：\n"
        f"{world_description}"
    )

    # 初始化对话历史
    def get_init_messages():
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"我扮演{role}，请开始角色扮演游戏。"}
        ]

    messages = get_init_messages()

    # 首次AI回复
    try:
        response = client.chat.completions.create(
            model=os.getenv("MODEL_NAME"),
            messages=messages,
            temperature=0.7
        )
        assistant_reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_reply})
        print(assistant_reply)
    except Exception as e:
        error_handler.handle_llm_error(e)
        return

    while True:
        user_input = input("你的行动（输入'退出'结束游戏，重新开始，清屏，重新生成本回合）：")
        if user_input == '退出':
            break
        elif user_input == '清屏':
            os.system('cls')
            print("屏幕已清空")
            continue
        elif user_input == '重新开始':
            print("\n正在重新生成场景，请稍候...\n")
            messages = get_init_messages()
            try:
                response = client.chat.completions.create(
                    model=os.getenv("MODEL_NAME"),
                    messages=messages,
                    temperature=0.7
                )
                assistant_reply = response.choices[0].message.content
                messages.append({"role": "assistant", "content": assistant_reply})
                print("=== 新的场景已生成 ===")
                print(assistant_reply)
            except Exception as e:
                error_handler.handle_llm_error(e)
            continue
        elif user_input == '重新生成本回合':
            print("\n正在重新生成本回合内容，请稍候...\n")
            # 找到上一个用户输入（即本回合的行动），以及之前的所有历史
            # 假设每一回合结构为：...assistant, user(行动), assistant
            # 只移除最后一个assistant回复，保留用户行动
            if len(messages) >= 2 and messages[-1]["role"] == "assistant" and messages[-2]["role"] == "user":
                last_user_action = messages[-2]
                # 移除最后一个assistant回复
                messages = messages[:-1]
                try:
                    response = client.chat.completions.create(
                        model=os.getenv("MODEL_NAME"),
                        messages=messages,
                        temperature=0.7
                    )
                    assistant_reply = response.choices[0].message.content
                    messages.append({"role": "assistant", "content": assistant_reply})
                    print("=== 本回合内容已重新生成 ===")
                    print(assistant_reply)
                except Exception as e:
                    error_handler.handle_llm_error(e)
            else:
                print("无法重新生成本回合（历史记录不足）")
            continue

        # 用户输入内嵌到提示中，并追加到对话历史
        action_prompt = f"我的行动：{user_input}"
        messages.append({"role": "user", "content": action_prompt})
        try:
            response = client.chat.completions.create(
                model=os.getenv("MODEL_NAME"),
                messages=messages,
                temperature=0.7
            )
            assistant_reply = response.choices[0].message.content
            messages.append({"role": "assistant", "content": assistant_reply})
            print(assistant_reply)
        except Exception as e:
            error_handler.handle_llm_error(e)

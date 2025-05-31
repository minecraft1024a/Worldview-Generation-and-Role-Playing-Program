import openai
from dotenv import load_dotenv
import os
import threading
from src import error_handler, summary
from src.error_handler import error_handler


# 加载环境变量
load_dotenv()
client = openai.OpenAI(
    base_url=os.getenv("API_URL"),
    api_key=os.getenv("API_KEY")
)

def start_role_play(world_description,summary_text):
    if not summary_text:
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
        "请根据以下世界观进行角色扮演：\n"
        f"{world_description}\n"
    )
    if summary_text:
        system_prompt += f"\n剧情摘要：{summary_text}\n"

    # 初始化对话历史
    def get_init_messages():
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"我扮演{role}，请开始角色扮演游戏。"}
        ]

    messages = get_init_messages()

    # 标志变量，用于标记摘要是否生成完成
    summary_generated = False

    # 首次AI回复
    try:
        response = client.chat.completions.create(
            model=os.getenv("MODEL_NAME"),
            messages=messages,
            temperature=0.7
        )
        assistant_reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_reply})
        os.system('cls')  # 清屏
        print(assistant_reply)
    except Exception as e:
        error_handler.handle_llm_error(e)
        return

    turn_count = 0
    summary_interval = 5  # 每5轮生成一次摘要

    def generate_summary_in_background(messages, world_description, turn_count, summary_interval):
        """
        在后台线程中生成摘要并保存到 JSON 文件
        """
        nonlocal summary_generated
        try:
            summary_text = summary.summarize_and_save(messages, world_description, turn_count, summary_interval)
            if summary_text:
                summary_generated = True  # 标记摘要生成完成
        except Exception as e:
            print("生成摘要时发生错误：", e)

    while True:
        user_input = input("你的行动（输入'退出'结束游戏，重新开始，清屏，重新生成本回合）：")
        if user_input == '退出':
            print("游戏已退出，再见！")
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
                os.system('cls')  # 清屏
                print("=== 新的场景已生成 ===")
                print(assistant_reply)
            except Exception as e:
                error_handler.handle_llm_error(e)
            continue
        elif user_input == '重新生成本回合':
            print("\n正在重新生成本回合内容，请稍候...\n")
            if len(messages) >= 2 and messages[-1]["role"] == "assistant" and messages[-2]["role"] == "user":
                messages = messages[:-1]  # 移除最后一个assistant回复
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

            # 如果摘要生成完成，在输出末尾附加提示
            if summary_generated:
                assistant_reply += "\n\n（摘要生成完成）"
                summary_generated = False  # 重置标志

            messages.append({"role": "assistant", "content": assistant_reply})
            os.system('cls')  # 清屏
            print(assistant_reply)

            # 每5轮生成一次摘要，并在后台线程中执行
            turn_count += 1
            if turn_count % summary_interval == 0:
                print("\n正在后台生成对话摘要，请继续游戏...\n")
                summary_thread = threading.Thread(
                    target=generate_summary_in_background,
                    args=(messages, world_description, turn_count, summary_interval)
                )
                summary_thread.start()

        except Exception as e:
            error_handler.handle_llm_error(e)

import openai
from dotenv import load_dotenv
import os
import threading
from src import error_handler, summary
from src.error_handler import error_handler
from src.character_generator import generate_character
from src import summary


# 加载环境变量
load_dotenv()
client = openai.OpenAI(
    base_url=os.getenv("API_URL"),
    api_key=os.getenv("API_KEY")
)

def start_role_play(world_description, summary_text, save_name=None, last_conversation=None,role=None):
    if not summary_text and not role:
        role = generate_character(world_description)
        if not role:
            return

    # 初始设定
    def build_system_prompt(include_last_conversation=True):
        prompt = (
            "你是一个角色设定生成器和角色扮演大师。请严格按照如下格式输出每一轮内容，不要添加任何解释或多余内容：\n"
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
            "【格式示例】\n"
            "用户身份：艾琳·星语\n"
            "时间: 晨曦初升\n"
            "地点: 雾林边境\n"
            "情景: 你正站在雾林边境，准备踏入未知的冒险。\n"
            "===============\n"
            "用户状态: 精神饱满，装备齐全\n"
            "===============\n"
            "用户物品栏: 魔法短杖，旅行斗篷，干粮\n"
            "===============\n"
            "用户接下来的选择(使用数字标记):\n1. 进入雾林 2. 检查装备 3. 休息片刻\n"
            "请严格按照上述格式输出每一轮内容，不要输出任何解释或多余内容。"
        )
        if summary_text:
            prompt += f"\n剧情摘要：{summary_text}\n"
            if last_conversation:
                prompt += f"\n上次对话：{last_conversation.get('content','')}\n,直接输出上次对话内容，不需要额外的提示。"
        return prompt

    # 初始化对话历史
    def get_init_messages(include_last_conversation=True):
        messages = [
            {"role": "system", "content": build_system_prompt(include_last_conversation)}
        ]
        messages.append({"role": "user", "content": f"我扮演以下角色，请以该角色的身份和视角进行角色扮演，不要以旁观者或叙述者视角：\n{role}\n请开始角色扮演游戏。"})
        return messages

    # 首次AI回复，包含上次对话
    messages = get_init_messages(include_last_conversation=True)
    summary_generated = False

    # 首次回复
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

    # 首次回复后，去除上次对话内容，重建 system_prompt
    messages = get_init_messages(include_last_conversation=False)
    messages.append({"role": "user", "content": f"我扮演以下角色：{role}，请开始角色扮演游戏,请以世界观的逻辑为主，不以扮演角色的逻辑为主。"})
    messages.append({"role": "assistant", "content": assistant_reply})

    turn_count = 0
    summary_interval = int(os.getenv("SUMMARY_INTERVAL", 5))  # 摘要生成的轮数间隔，可在.env中自定义

    def generate_summary_in_background(messages, world_description, save_name):
        """
        在后台线程中生成摘要并保存到 JSON 文件
        """
        nonlocal summary_generated
        try:
            # 摘要生成时不包含最后一轮AI回复
            if messages and messages[-1]["role"] == "assistant":
                summary_messages = messages[:-1]
                last_ai_reply = messages[-1]
            else:
                summary_messages = messages
                last_ai_reply = None
            summary_text, new_save_name = summary.summarize_and_save(summary_messages, world_description, save_name, role)
            # 摘要生成完毕后再把最后一轮AI回复加进存档
            if last_ai_reply:
                summary.save_last_conversation(save_name or new_save_name, last_ai_reply)
            if summary_text:
                summary_generated = True  # 标记摘要生成完成
        except Exception as e:
            print("生成摘要时发生错误：", e)

    while True:
        user_input = input("你的行动（输入'退出'结束游戏，重新开始，重新生成本回合）：")
        if user_input == '退出':
            print("游戏已退出，再见！")
            break
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
                # 获取当前存档名
                summary_name = save_name if save_name else "(无名存档)"
                assistant_reply += f"\n\n（摘要生成完成，存档名：{summary_name}）"
                summary_generated = False  # 重置标志

            messages.append({"role": "assistant", "content": assistant_reply})
            os.system('cls')  # 清屏
            print(assistant_reply)

            # 每x轮生成一次摘要，并在后台线程中执行
            turn_count += 1
            if turn_count % summary_interval == 0:
                print("\n正在后台生成对话摘要，请继续游戏...\n")
                summary_thread = threading.Thread(
                    target=generate_summary_in_background,
                    args=(messages, world_description, save_name)
                )
                summary_thread.start()

        except Exception as e:
            error_handler.handle_llm_error(e)
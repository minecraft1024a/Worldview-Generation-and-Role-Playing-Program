import openai
from dotenv import load_dotenv
import os
import threading
from src import error_handler, summary
from src.error_handler import error_handler
from src.character_generator import generate_character
from src import summary
from src.music_player import play_music_by_mood, stop_music, pause_music, resume_music
import random
import time
import queue

# 定义音乐文件夹路径，可以从环境变量读取或设置默认值
MUSIC_FOLDER = "game_music"


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
    summary_save_name_queue = queue.Queue()  # 新增队列用于传递save_name

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
    summary_save_name_queue = queue.Queue()  # 用于线程间传递实际存档名

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
                summary.save_last_conversation(new_save_name or save_name, last_ai_reply)
            if summary_text:
                summary_generated = True  # 标记摘要生成完成
            # 将实际save_name放入队列
            summary_save_name_queue.put(new_save_name or save_name)
            return new_save_name or save_name
        except Exception as e:
            print("生成摘要时发生错误：", e)
            summary_save_name_queue.put(save_name)
            return save_name

    while True:
        # 检查摘要线程是否有新存档名
        new_save_name = None
        while not summary_save_name_queue.empty():
            new_save_name = summary_save_name_queue.get()
        if new_save_name:
            save_name = new_save_name

        user_input = input("你的行动（输入'退出'结束游戏，重新开始，重新生成本回合）：")
        while not user_input.strip():
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

            # 检查摘要生成队列，若有新save_name则输出
            if not summary_save_name_queue.empty():
                latest_save_name = summary_save_name_queue.get()
                assistant_reply += f"\n\n（摘要生成完成，存档名：{latest_save_name}）"
                summary_generated = False  # 重置标志

            messages.append({"role": "assistant", "content": assistant_reply})

            # 检查音乐播放开关
            enable_music = os.getenv("ENABLE_MUSIC", "true").lower() == "true"

            if enable_music and turn_count == 0:  # 第零回合自动播放音乐
                available_moods = [name for name in os.listdir(MUSIC_FOLDER) if os.path.isdir(os.path.join(MUSIC_FOLDER, name))]
                mood_options = "\n".join([f"- {name}" for name in available_moods])
                mood_prompt = (
                    "请根据以下情景，从下列基调中选择一个最合适的基调，只能选择并输出下列基调名称之一：\n"
                    f"情景：{assistant_reply}\n"
                    f"{mood_options}\n"
                    "【重要】只能输出上面列表中的一个基调名称，不能输出编号、标点、解释、换行或任何其他内容。直接输出名称本身。"
                )
                messages.append({"role": "user", "content": mood_prompt})
                try:
                    mood_response = client.chat.completions.create(
                        model=os.getenv("MODEL_NAME"),
                        messages=messages,
                        temperature=0.7
                    )
                    mood = mood_response.choices[0].message.content.strip()

                    # 动态读取基调文件夹名称
                    while mood not in available_moods:
                        print(f"AI生成的基调'{mood}'无效，重新生成基调。")
                        mood_response = client.chat.completions.create(
                            model=os.getenv("MODEL_NAME"),
                            messages=messages,
                            temperature=0.7
                        )
                        mood = mood_response.choices[0].message.content.strip()

                    if mood:
                        play_music_by_mood(mood)
                        assistant_reply += f"\n\n正在播放基调为'{mood}'的音乐。"
                    else:
                        assistant_reply += "AI未生成基调，重新生成..."
                except Exception as e:
                    error_handler.handle_llm_error(e)
            elif enable_music and (turn_count % 3 == 0 or turn_count == 0):  # 每三回合检查是否需要更换音乐
                change_music_prompt = (
                    "根据当前情景和音乐基调，判断是否需要更换音乐。只输出'是'或'否'，不要添加其他内容。\n"
                    f"情景：{assistant_reply}\n"
                    f"当前基调：{mood}\n"
                )
                messages.append({"role": "user", "content": change_music_prompt})
                try:
                    change_music_response = client.chat.completions.create(
                        model=os.getenv("MODEL_NAME"),
                        messages=messages,
                        temperature=0.7
                    )
                    change_music_decision = change_music_response.choices[0].message.content.strip()

                    if change_music_decision == '是':
                        # 调用AI生成基调并播放音乐
                        available_moods = [name for name in os.listdir(MUSIC_FOLDER) if os.path.isdir(os.path.join(MUSIC_FOLDER, name))]
                        mood_options = "\n".join([f"- {name}" for name in available_moods])
                        mood_prompt = (
                            "请根据刚才的内容和以下情景，从下列基调中选择一个最合适的基调，只能选择并输出下列基调名称之一：\n"
                            f"情景：{assistant_reply}\n"
                            f"{mood_options}\n"
                            "【重要】只能输出上面列表中的一个基调名称，不能输出编号、标点、解释、换行或任何其他内容。直接输出名称本身。"
                        )
                        messages.append({"role": "user", "content": mood_prompt})
                        try:
                            mood_response = client.chat.completions.create(
                                model=os.getenv("MODEL_NAME"),
                                messages=messages,
                                temperature=0.7
                            )
                            mood = mood_response.choices[0].message.content.strip()

                            # 动态读取基调文件夹名称
                            while mood not in available_moods:
                                print(f"AI生成的基调'{mood}'无效，重新生成基调。")
                                mood_response = client.chat.completions.create(
                                    model=os.getenv("MODEL_NAME"),
                                    messages=messages,
                                    temperature=0.7
                                )
                                mood = mood_response.choices[0].message.content.strip()

                            if mood:
                                play_music_by_mood(mood)
                                assistant_reply += f"\n\n正在播放基调为'{mood}'的音乐。"
                            else:
                                assistant_reply += "AI未生成基调，重新生成..."
                        except Exception as e:
                            error_handler.handle_llm_error(e)
                except Exception as e:
                    error_handler.handle_llm_error(e)

            # 输出AI回复
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


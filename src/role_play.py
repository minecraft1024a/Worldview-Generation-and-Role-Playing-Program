from src.llm_core import llm_core
from src.summary import save_manager  # 使用新的存档管理器
from dotenv import load_dotenv
import os
import threading
from src import error_handler, summary
from src.error_handler import error_handler
from src.character_generator import generate_character
from src.music_player import play_music_by_mood
import queue

# 定义音乐文件夹路径，可以从环境变量读取或设置默认值
MUSIC_FOLDER = "game_music"

# 加载环境变量
load_dotenv()

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
    assistant_reply = llm_core.role_play_response(messages, temperature=0.7)
    if assistant_reply is None:
        return
        
    messages.append({"role": "assistant", "content": assistant_reply})
    os.system('cls')  # 清屏
    print(assistant_reply)

    # 首次回复后，去除上次对话内容，重建 system_prompt
    messages = get_init_messages(include_last_conversation=False)
    messages.append({"role": "user", "content": f"我扮演以下角色：{role}，请开始角色扮演游戏,请以世界观的逻辑为主，不以扮演角色的逻辑为主。"})
    messages.append({"role": "assistant", "content": assistant_reply})

    turn_count = 0
    mood = None  # 初始化音乐基调变量
    current_summary = summary_text or ""  # 当前摘要，用于增量更新
    summary_interval = int(os.getenv("SUMMARY_INTERVAL", 5))  # 摘要生成的轮数间隔
    summary_save_name_queue = queue.Queue()  # 用于线程间传递实际存档名

    def generate_smart_summary_in_background(messages, world_description, save_name, previous_summary):
        """
        智能后台摘要生成 - 使用增量更新和Token优化
        """
        nonlocal summary_generated
        try:
            # 使用新的智能存档管理器
            summary_text, new_save_name = save_manager.save_game_state(
                messages, world_description, save_name, role, previous_summary
            )
            
            if summary_text:
                summary_generated = True
                # 不在这里打印，通过队列传递信息到主线程显示
            
            # 将实际save_name放入队列
            summary_save_name_queue.put(new_save_name or save_name)
            return new_save_name or save_name, summary_text
            
        except Exception as e:
            # 静默处理错误，避免打断用户输入
            import logging
            logging.warning(f"生成摘要时发生错误: {e}")
            assistant_reply += f"生成摘要时发生错误: {e}"
            summary_save_name_queue.put(save_name)
            return save_name, previous_summary

    while True:
        # 检查摘要线程是否有新存档名和摘要更新
        new_save_name = None
        while not summary_save_name_queue.empty():
            new_save_name = summary_save_name_queue.get()
        if new_save_name:
            save_name = new_save_name
            # 同时更新当前摘要（用于下次增量更新）
            try:
                save_data = save_manager.load_game_state(save_name)
                if save_data[1]:  # 如果成功加载摘要
                    current_summary = save_data[1]
            except:
                pass

        user_input = input("你的行动（输入'退出'结束游戏，重新开始，重新生成本回合）：")
        while not user_input.strip():
            user_input = input("你的行动（输入'退出'结束游戏，重新开始，重新生成本回合）：")
        if user_input == '退出':
            print("游戏已退出，再见！")
            break
        elif user_input == '重新开始':
            print("\n正在重新生成场景，请稍候...\n")
            messages = get_init_messages()
            assistant_reply = llm_core.role_play_response(messages, temperature=0.7)
            if assistant_reply:
                messages.append({"role": "assistant", "content": assistant_reply})
                os.system('cls')  # 清屏
                print("=== 新的场景已生成 ===")
                print(assistant_reply)
            continue
        elif user_input == '重新生成本回合':
            print("\n正在重新生成本回合内容，请稍候...\n")
            if len(messages) >= 2 and messages[-1]["role"] == "assistant" and messages[-2]["role"] == "user":
                messages = messages[:-1]  # 移除最后一个assistant回复
                assistant_reply = llm_core.role_play_response(messages, temperature=0.7)
                if assistant_reply:
                    messages.append({"role": "assistant", "content": assistant_reply})
                    print("=== 本回合内容已重新生成 ===")
                    print(assistant_reply)
            else:
                print("无法重新生成本回合（历史记录不足）")
            continue

        # 用户输入内嵌到提示中，并追加到对话历史
        action_prompt = f"我的行动：{user_input}"
        messages.append({"role": "user", "content": action_prompt})
        assistant_reply = llm_core.role_play_response(messages, temperature=0.7)
        if assistant_reply is None:
            continue

        # 检查摘要生成队列，若有新save_name则添加到回复中
        if not summary_save_name_queue.empty():
            latest_save_name = summary_save_name_queue.get()
            assistant_reply += f"\n\n💾 进度已自动保存: {latest_save_name}"
            summary_generated = False  # 重置标志

        messages.append({"role": "assistant", "content": assistant_reply})

        # 检查音乐播放开关
        enable_music = os.getenv("ENABLE_MUSIC", "true").lower() == "true"

        if enable_music and turn_count == 0:  # 第零回合自动播放音乐
            available_moods = [name for name in os.listdir(MUSIC_FOLDER) if os.path.isdir(os.path.join(MUSIC_FOLDER, name))]
            mood = llm_core.select_music_mood(assistant_reply, available_moods)

            # 动态读取基调文件夹名称，静默重试
            retry_count = 0
            while mood not in available_moods and retry_count < 3:
                mood = llm_core.select_music_mood(assistant_reply, available_moods)
                retry_count += 1

            if mood and mood in available_moods:
                music_status = play_music_by_mood(mood)
                # 只在AI回复中显示音乐信息，不单独打印
                assistant_reply += f"\n\n🎵 {mood}基调音乐已开始播放"
            else:
                # 静默处理，不显示错误信息
                pass
        elif enable_music and (turn_count % 3 == 0 or turn_count == 0):  # 每三回合检查是否需要更换音乐
            should_change = llm_core.should_change_music(assistant_reply, mood)
            
            if should_change:
                # 调用AI生成基调并播放音乐
                available_moods = [name for name in os.listdir(MUSIC_FOLDER) if os.path.isdir(os.path.join(MUSIC_FOLDER, name))]
                new_mood = llm_core.select_music_mood(assistant_reply, available_moods)

                # 静默重试，避免打印错误信息
                retry_count = 0
                while new_mood not in available_moods and retry_count < 3:
                    new_mood = llm_core.select_music_mood(assistant_reply, available_moods)
                    retry_count += 1

                if new_mood and new_mood in available_moods:
                    mood = new_mood  # 更新当前基调
                    music_status = play_music_by_mood(mood)
                    assistant_reply += f"\n\n🎵 音乐已切换至{mood}基调"
                # 如果无法生成有效基调，静默处理，不添加错误信息

        # 输出AI回复
        os.system('cls')  # 清屏
        print(assistant_reply)

        # 每x轮生成一次智能摘要，并在后台线程中执行
        turn_count += 1
        if turn_count % summary_interval == 0:
            assistant_reply += f"\n\n💾 进度自动保存中..."
            # 静默启动后台摘要生成，不打印提示
            summary_thread = threading.Thread(
                target=generate_smart_summary_in_background,
                args=(messages, world_description, save_name, current_summary)
            )
            summary_thread.start()


from src.llm_core import llm_core
from src.summary import save_manager  # 使用新的存档管理器
import os
import threading
from src import error_handler, summary
from src.error_handler import error_handler
from src.character_generator import generate_character
from src.music_player import MusicPlayer  # 修正导入
import queue
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.progress import track
from rich import print as rich_print
import re
import toml

# 定义音乐文件夹路径，可以从环境变量读取或设置默认值
MUSIC_FOLDER = "game_music"

# 初始化Rich控制台
console = Console(force_terminal=True)
# 初始化音乐播放器实例
music_player = MusicPlayer()


def format_ai_reply(reply):
    """
    格式化AI回复，使用Rich进行美化显示
    """
    # 分割回复内容
    lines = reply.split('\n')
    formatted_content = []
    current_section = ""
    
    for line in lines:
        original_line = line
        line = line.strip()
        if not line:
            if current_section:
                current_section += "\n"
            continue
            
        # 识别不同的部分并应用样式
        if line.startswith('用户身份：'):
            if current_section:
                formatted_content.append(current_section)
            current_section = f"[bold cyan]👤 {line}[/bold cyan]"
        elif line.startswith('时间:') or line.startswith('时间：'):
            current_section += f"\n[yellow]🕐 {line}[/yellow]"
        elif line.startswith('地点:') or line.startswith('地点：'):
            current_section += f"\n[green]📍 {line}[/green]"
        elif line.startswith('情景:') or line.startswith('情景：'):
            current_section += f"\n[blue]🎬 {line}[/blue]"
        elif line == '===============':
            current_section += f"\n[dim bright_black]{'─' * 50}[/dim bright_black]"
        elif line.startswith('用户状态:') or line.startswith('用户状态：'):
            current_section += f"\n[magenta]💪 {line}[/magenta]"
        elif line.startswith('用户物品栏:') or line.startswith('用户物品栏：'):
            current_section += f"\n[red]🎒 {line}[/red]"
        elif line.startswith('用户接下来的选择') or line.startswith('选择'):
            current_section += f"\n[bold yellow]⚡ {line}[/bold yellow]"
        elif re.match(r'^\d+\.', line):  # 数字选项
            current_section += f"\n  [bright_blue]🔸 {line}[/bright_blue]"
        elif line.startswith('🎵'):  # 音乐信息
            current_section += f"\n[bold green]{line}[/bold green]"
        elif line.startswith('💾'):  # 保存信息
            current_section += f"\n[bold blue]{line}[/bold blue]"
        elif line.startswith('剧情摘要'):
            current_section += f"\n[dim italic]{line}[/dim italic]"
        else:
            # 保持原始的缩进和格式
            if original_line.startswith(' ') or original_line.startswith('\t'):
                current_section += f"\n{original_line}"
            else:
                current_section += f"\n[white]{line}[/white]"
    
    if current_section:
        formatted_content.append(current_section)
    
    return "\n\n".join(formatted_content)

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
    console.clear()  # 使用Rich清屏
    
    # 美化显示AI回复
    formatted_reply = format_ai_reply(assistant_reply)
    console.print(Panel(formatted_reply, title="[bold green]🎭 角色扮演游戏[/bold green]", border_style="green"))

    # 首次回复后，去除上次对话内容，重建 system_prompt
    messages = get_init_messages(include_last_conversation=False)
    messages.append({"role": "user", "content": f"我扮演以下角色：{role}，请开始角色扮演游戏,请以世界观的逻辑为主，不以扮演角色的逻辑为主。"})
    messages.append({"role": "assistant", "content": assistant_reply})

    turn_count = 0
    mood = None  # 初始化音乐基调变量
    current_summary = summary_text or ""  # 当前摘要，用于增量更新
    config = toml.load('config.toml')
    summary_interval = config['game']['summary_interval']  # 摘要生成的轮数间隔
    summary_save_name_queue = queue.Queue()  # 用于线程间传递实际存档名

    def generate_smart_summary_in_background(messages, world_description, save_name, previous_summary):
        """
        增强型智能后台摘要生成 - 使用新的智能摘要系统
        """
        nonlocal summary_generated, current_summary
        try:
            # 使用增强的智能摘要生成
            if len(messages) > 10:
                # 为长对话使用智能摘要系统
                session_context = f"世界观：{world_description[:200]}，角色：{role[:100] if role else '未知'}"
                new_summary = llm_core.generate_enhanced_summary(
                    messages=messages,
                    previous_summary=previous_summary,
                    session_context=session_context
                )
            else:
                # 较短对话使用标准智能摘要
                new_summary = llm_core.generate_smart_summary(
                    messages=messages,
                    previous_summary=previous_summary,
                    enable_optimization=True
                )
            
            if new_summary and new_summary.strip():
                # 生成优化的存档名
                context_info = f"第{turn_count}轮，{mood if mood else '未知'}基调"
                new_save_name = llm_core.generate_compact_save_name(
                    summary=new_summary,
                    context_info=context_info
                )
                
                # 使用存档管理器保存状态（已经包含了智能压缩）
                final_summary, actual_save_name = save_manager.save_game_state(
                    messages=messages,
                    world_description=world_description,
                    save_name=new_save_name,
                    role=role,
                    previous_summary=previous_summary
                )
                
                if final_summary:
                    summary_generated = True
                    current_summary = final_summary  # 更新当前摘要用于下次增量更新
                    # 将实际保存的名称放入队列
                    summary_save_name_queue.put(actual_save_name or new_save_name)
                    return actual_save_name or new_save_name, final_summary
            
            # 生成失败时的回退处理
            fallback_summary, fallback_name = save_manager.save_game_state(
                messages, world_description, save_name, role, previous_summary
            )
            summary_save_name_queue.put(fallback_name or save_name)
            current_summary = fallback_summary or previous_summary
            return fallback_name or save_name, fallback_summary or previous_summary
            
        except Exception as e:
            # 静默处理错误，避免打断用户输入
            import logging
            logging.warning(f"生成智能摘要时发生错误: {e}")
            
            # 使用最基本的保存方式作为最后回退
            try:
                backup_summary, backup_name = save_manager.save_game_state(
                    messages, world_description, save_name, role, previous_summary
                )
                summary_save_name_queue.put(backup_name or save_name)
                return backup_name or save_name, backup_summary or previous_summary
            except:
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

        # 显示帮助信息
        help_text = (
            "💡 [dim]可用命令: 退出、重新开始、重新生成本回合、查看摘要[/dim]"
        )
        console.print(help_text)
        console.print()  # 空行
        
        user_input = Prompt.ask(
            "[bold yellow]🎮 你的行动[/bold yellow]",
            default="",
            show_default=False,
            console=console
        )
        while not user_input.strip():
            console.print("[red]⚠️  请输入你的行动！[/red]")
            user_input = Prompt.ask(
                "[bold yellow]🎮 你的行动[/bold yellow]",
                default="",
                show_default=False,
                console=console
            )
        if user_input == '退出':
            console.print(Panel(
                "[bold red]🚪 游戏已退出，再见！[/bold red]",
                title="[red]退出游戏[/red]",
                border_style="red"
            ))
            break
        elif user_input == '重新开始':
            console.print(Panel(
                "[bold yellow]🔄 正在重新生成场景，请稍候...[/bold yellow]",
                title="[yellow]重新开始[/yellow]",
                border_style="yellow"
            ))
            messages = get_init_messages()
            assistant_reply = llm_core.role_play_response(messages, temperature=0.7)
            if assistant_reply:
                messages.append({"role": "assistant", "content": assistant_reply})
                console.clear()
                formatted_reply = format_ai_reply(assistant_reply)
                console.print(Panel(
                    formatted_reply,
                    title="[bold green]🎭 新的场景已生成[/bold green]",
                    border_style="green"
                ))
            continue
        elif user_input == '查看摘要':
            if current_summary:
                console.print(Panel(
                    f"[bold cyan]📖 当前故事摘要[/bold cyan]\n\n{current_summary}",
                    title="[cyan]故事进度[/cyan]",
                    border_style="cyan"
                ))
            else:
                console.print(Panel(
                    "[yellow]📝 当前还没有生成摘要，请继续游戏几回合后摘要将自动生成[/yellow]",
                    title="[yellow]摘要状态[/yellow]",
                    border_style="yellow"
                ))
            continue
        elif user_input == '重新生成本回合':
            console.print(Panel(
                "[bold cyan]🎲 正在重新生成本回合内容，请稍候...[/bold cyan]",
                title="[cyan]重新生成[/cyan]",
                border_style="cyan"
            ))
            if len(messages) >= 2 and messages[-1]["role"] == "assistant" and messages[-2]["role"] == "user":
                messages = messages[:-1]  # 移除最后一个assistant回复
                assistant_reply = llm_core.role_play_response(messages, temperature=0.7)
                if assistant_reply:
                    messages.append({"role": "assistant", "content": assistant_reply})
                    formatted_reply = format_ai_reply(assistant_reply)
                    console.print(Panel(
                        formatted_reply,
                        title="[bold cyan]🎲 本回合内容已重新生成[/bold cyan]",
                        border_style="cyan"
                    ))
            else:
                console.print("[red]❌ 无法重新生成本回合（历史记录不足）[/red]")
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
            # 使用更详细的保存完成信息
            assistant_reply += f"\n\n✅ 智能存档已完成: {latest_save_name}"
            assistant_reply += f"\n🔍 已优化对话内容并生成高质量摘要"
            summary_generated = False  # 重置标志

        messages.append({"role": "assistant", "content": assistant_reply})

        # 检查音乐播放开关
        config = toml.load('config.toml')
        enable_music = config['game']['enable_music']

        if enable_music and turn_count == 0:  # 第零回合自动播放音乐
            available_moods = [name for name in os.listdir(MUSIC_FOLDER) if os.path.isdir(os.path.join(MUSIC_FOLDER, name))]
            mood = llm_core.select_music_mood(assistant_reply, available_moods)

            # 动态读取基调文件夹名称，静默重试
            retry_count = 0
            while mood not in available_moods and retry_count < 3:
                mood = llm_core.select_music_mood(assistant_reply, available_moods)
                retry_count += 1

            if mood and mood in available_moods:
                music_status = music_player.play_music_by_mood(mood)  # 修正为实例方法调用
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
                    music_status = music_player.play_music_by_mood(mood)  # 修正为实例方法调用
                    assistant_reply += f"\n\n🎵 音乐已切换至{mood}基调"
                # 如果无法生成有效基调，静默处理，不添加错误信息

        # 输出AI回复
        console.clear()  # 使用Rich清屏
        formatted_reply = format_ai_reply(assistant_reply)
        console.print(Panel(
            formatted_reply,
            title="[bold green]🎭 角色扮演游戏[/bold green]",
            border_style="green"
        ))

        # 每x轮生成一次智能摘要，并在后台线程中执行
        turn_count += 1
        if turn_count % summary_interval == 0:
            # 显示智能摘要生成状态
            progress_msg = f"\n\n💡 第{turn_count}轮：正在生成智能摘要和优化存档..."
            assistant_reply += progress_msg
            
            # 重新显示当前回复（包含进度信息）
            console.clear()
            formatted_reply = format_ai_reply(assistant_reply)
            console.print(Panel(
                formatted_reply,
                title="[bold green]🎭 角色扮演游戏[/bold green]",
                border_style="green"
            ))
            
            # 启动增强型后台摘要生成
            summary_thread = threading.Thread(
                target=generate_smart_summary_in_background,
                args=(messages, world_description, save_name, current_summary),
                daemon=True  # 设为守护线程，主程序退出时自动结束
            )
            summary_thread.start()
        
        # 智能摘要优化：每2轮进行一次轻量级状态更新
        elif turn_count % 2 == 0 and turn_count > 0:
            # 使用轻量级摘要更新，不保存文件
            try:
                recent_progress = llm_core.generate_smart_summary(
                    messages=messages[-4:],  # 只分析最近4条消息
                    previous_summary="",
                    max_tokens=200,
                    enable_optimization=True
                )
                if recent_progress and len(recent_progress.strip()) > 10:
                    # 更新内存中的当前摘要
                    if current_summary:
                        # 合并最新进展到当前摘要
                        current_summary = f"{current_summary[:400]}...最新：{recent_progress[:100]}"
                    else:
                        current_summary = recent_progress
            except:
                pass  # 轻量级更新失败时忽略


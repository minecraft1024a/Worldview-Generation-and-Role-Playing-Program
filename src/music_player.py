import os
import random
from dotenv import load_dotenv
import pygame

# 加载环境变量
load_dotenv()

# 获取音乐播放开关
enable_music = os.getenv("ENABLE_MUSIC", "true").lower() == "true"

# 音乐文件夹路径
MUSIC_FOLDER = "game_music"

def play_music_by_mood(mood):
    """
    根据情景基调播放对应的音乐。

    :param mood: 基调名称（对应音乐文件夹名称）
    """
    if not enable_music:
        print("音乐播放已关闭。")
        return

    # 动态读取基调文件夹名称
    available_moods = [name for name in os.listdir(MUSIC_FOLDER) if os.path.isdir(os.path.join(MUSIC_FOLDER, name))]

    # 如果基调不存在，随机选择一个
    if mood not in available_moods:
        print(f"基调'{mood}'无效，随机选择一个基调。")
        mood = random.choice(available_moods)

    mood_folder = os.path.join(MUSIC_FOLDER, mood)
    if not os.path.exists(mood_folder):
        print(f"未找到基调为'{mood}'的音乐文件夹。")
        return

    music_files = [f for f in os.listdir(mood_folder) if f.endswith(".mp3")]
    if not music_files:
        return

    # 随机选择一首音乐
    music_file = random.choice(music_files)
    music_path = os.path.join(mood_folder, music_file)

    # 初始化并播放音乐
    pygame.mixer.init()
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play()


def stop_music():
    """停止播放音乐"""
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
        pygame.mixer.quit()
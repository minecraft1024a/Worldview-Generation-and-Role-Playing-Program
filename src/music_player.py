import os
import random
import pygame
import logging
import toml

# 配置日志记录，避免在终端显示音乐状态信息
logging.basicConfig(level=logging.WARNING)

# 音乐文件夹路径
MUSIC_FOLDER = "game_music"

class MusicPlayer:
    def __init__(self):
        self.config = toml.load('config.toml')
        # 修正为从 [game] 区块读取 enable_music
        self.enable_music = self.config.get('game', {}).get('enable_music', False)

    def play_music_by_mood(self, mood):
        """
        根据情景基调播放对应的音乐。
        静默播放，不会打断用户输入界面。

        :param mood: 基调名称（对应音乐文件夹名称）
        :return: 播放状态信息（不会打印到终端）
        """
        if not self.enable_music:
            return "音乐播放已关闭"

        try:
            # 检查音乐文件夹是否存在
            if not os.path.exists(MUSIC_FOLDER):
                return f"音乐文件夹不存在: {MUSIC_FOLDER}"

            # 动态读取基调文件夹名称
            available_moods = [name for name in os.listdir(MUSIC_FOLDER) if os.path.isdir(os.path.join(MUSIC_FOLDER, name))]
            
            if not available_moods:
                return "未找到任何音乐基调文件夹"

            # 如果基调不存在，随机选择一个
            if mood not in available_moods:
                mood = random.choice(available_moods)

            mood_folder = os.path.join(MUSIC_FOLDER, mood)
            if not os.path.exists(mood_folder):
                return f"基调文件夹不存在: {mood}"

            # 查找音乐文件（支持多种格式）
            music_files = [f for f in os.listdir(mood_folder) if f.endswith((".mp3", ".wav", ".ogg"))]
            if not music_files:
                return f"基调文件夹中没有音乐文件: {mood}"

            # 随机选择一首音乐
            music_file = random.choice(music_files)
            music_path = os.path.join(mood_folder, music_file)

            # 停止当前播放的音乐
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()

            # 初始化并播放音乐
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.3)  # 设置较低音量，避免干扰游戏
            pygame.mixer.music.play(-1)  # 循环播放
            
            return f"正在播放: {mood}/{music_file}"
            
        except Exception as e:
            # 静默处理错误，不打断用户界面
            logging.warning(f"音乐播放错误: {e}")
            return f"音乐播放失败: {str(e)}"


    def stop_music(self):
        """静默停止播放音乐"""
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                return "音乐已停止"
        except Exception as e:
            logging.warning(f"停止音乐错误: {e}")
            return "停止音乐失败"

    def pause_music(self):
        """静默暂停播放音乐"""
        try:
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                return "音乐已暂停"
            return "没有正在播放的音乐"
        except Exception as e:
            logging.warning(f"暂停音乐错误: {e}")
            return "暂停音乐失败"

    def resume_music(self):
        """静默恢复播放音乐"""
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.unpause()
                return "音乐已恢复播放"
            return "音乐系统未初始化"
        except Exception as e:
            logging.warning(f"恢复音乐错误: {e}")
            return "恢复音乐失败"

    def get_music_status(self):
        """获取当前音乐播放状态"""
        try:
            if not pygame.mixer.get_init():
                return "音乐系统未初始化"
            elif pygame.mixer.music.get_busy():
                return "正在播放"
            else:
                return "已停止"
        except Exception as e:
            logging.warning(f"获取音乐状态错误: {e}")
            return "状态未知"

    def set_volume(self, volume):
        """设置音乐音量
        
        :param volume: 音量值 (0.0 - 1.0)
        """
        try:
            if pygame.mixer.get_init():
                volume = max(0.0, min(1.0, volume))  # 确保音量在有效范围内
                pygame.mixer.music.set_volume(volume)
                return f"音量已设置为: {int(volume * 100)}%"
            return "音乐系统未初始化"
        except Exception as e:
            logging.warning(f"设置音量错误: {e}")
            return "设置音量失败"
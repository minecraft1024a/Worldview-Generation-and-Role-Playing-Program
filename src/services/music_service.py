"""
音乐播放服务
提供游戏背景音乐播放功能
"""

import os
import random
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
import threading
import time

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from ..utils.error_handler import ErrorHandler

logger = logging.getLogger(__name__)

class MusicService:
    """音乐播放服务类"""
    
    def __init__(self, error_handler: ErrorHandler, music_folder: str = "game_music"):
        self.error_handler = error_handler
        self.music_folder = Path(music_folder)
        self.enabled = False
        self.current_track = None
        self.current_mood = None
        self.volume = 0.7
        self.is_playing = False
        self.available_moods = []
        
        # 初始化pygame mixer
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                self.enabled = True
                logger.info("音乐服务初始化成功")
            except Exception as e:
                logger.warning(f"音乐服务初始化失败: {e}")
                self.enabled = False
        else:
            logger.warning("pygame未安装，音乐功能不可用")
        
        # 扫描可用的音乐基调
        self._scan_available_moods()
    
    def enable_music(self, enabled: bool = True):
        """启用或禁用音乐播放"""
        if not PYGAME_AVAILABLE:
            logger.warning("pygame未安装，无法启用音乐")
            return False
        
        self.enabled = enabled
        if not enabled and self.is_playing:
            self.stop_music()
        
        logger.info(f"音乐播放已{'启用' if enabled else '禁用'}")
        return True
    
    def set_volume(self, volume: float):
        """
        设置音量
        
        Args:
            volume: 音量大小 (0.0-1.0)
        """
        try:
            volume = max(0.0, min(1.0, volume))
            self.volume = volume
            
            if PYGAME_AVAILABLE and pygame.mixer.get_init():
                pygame.mixer.music.set_volume(volume)
            
            logger.info(f"音量设置为: {volume}")
            
        except Exception as e:
            self.error_handler.handle_error(e, "设置音量")
    
    def play_music_by_mood(self, mood: str) -> Dict[str, Any]:
        """
        根据情景基调播放对应的音乐
        
        Args:
            mood: 基调名称（对应音乐文件夹名称）
            
        Returns:
            播放状态信息
        """
        try:
            if not self.enabled:
                return {"status": "disabled", "message": "音乐播放已关闭"}
            
            if not PYGAME_AVAILABLE:
                return {"status": "error", "message": "pygame未安装"}
            
            # 检查音乐文件夹是否存在
            if not self.music_folder.exists():
                return {"status": "error", "message": f"音乐文件夹不存在: {self.music_folder}"}
            
            # 如果基调不存在，随机选择一个
            if mood not in self.available_moods:
                if self.available_moods:
                    mood = random.choice(self.available_moods)
                    logger.info(f"指定的基调不存在，随机选择: {mood}")
                else:
                    return {"status": "error", "message": "未找到任何音乐基调文件夹"}
            
            mood_folder = self.music_folder / mood
            if not mood_folder.exists():
                return {"status": "error", "message": f"基调文件夹不存在: {mood}"}
            
            # 查找音乐文件
            music_files = list(mood_folder.glob("*.mp3")) + \
                         list(mood_folder.glob("*.wav")) + \
                         list(mood_folder.glob("*.ogg"))
            
            if not music_files:
                return {"status": "error", "message": f"基调文件夹中没有音乐文件: {mood}"}
            
            # 随机选择一首音乐
            selected_file = random.choice(music_files)
            
            # 播放音乐
            try:
                pygame.mixer.music.load(str(selected_file))
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play(-1)  # 循环播放
                
                self.current_track = selected_file.name
                self.current_mood = mood
                self.is_playing = True
                
                logger.info(f"开始播放音乐: {mood}/{selected_file.name}")
                
                return {
                    "status": "success",
                    "message": f"🎵 正在播放: {mood} - {selected_file.stem}",
                    "mood": mood,
                    "track": selected_file.name,
                    "volume": self.volume
                }
                
            except Exception as e:
                logger.error(f"播放音乐失败: {e}")
                return {"status": "error", "message": f"播放音乐失败: {e}"}
            
        except Exception as e:
            self.error_handler.handle_error(e, "播放音乐")
            return {"status": "error", "message": str(e)}
    
    def stop_music(self) -> Dict[str, Any]:
        """停止音乐播放"""
        try:
            if not PYGAME_AVAILABLE:
                return {"status": "error", "message": "pygame未安装"}
            
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
            
            self.is_playing = False
            self.current_track = None
            self.current_mood = None
            
            logger.info("音乐播放已停止")
            return {"status": "success", "message": "音乐播放已停止"}
            
        except Exception as e:
            self.error_handler.handle_error(e, "停止音乐")
            return {"status": "error", "message": str(e)}
    
    def pause_music(self) -> Dict[str, Any]:
        """暂停音乐播放"""
        try:
            if not PYGAME_AVAILABLE:
                return {"status": "error", "message": "pygame未安装"}
            
            if pygame.mixer.get_init():
                pygame.mixer.music.pause()
            
            logger.info("音乐播放已暂停")
            return {"status": "success", "message": "音乐播放已暂停"}
            
        except Exception as e:
            self.error_handler.handle_error(e, "暂停音乐")
            return {"status": "error", "message": str(e)}
    
    def resume_music(self) -> Dict[str, Any]:
        """恢复音乐播放"""
        try:
            if not PYGAME_AVAILABLE:
                return {"status": "error", "message": "pygame未安装"}
            
            if pygame.mixer.get_init():
                pygame.mixer.music.unpause()
            
            logger.info("音乐播放已恢复")
            return {"status": "success", "message": "音乐播放已恢复"}
            
        except Exception as e:
            self.error_handler.handle_error(e, "恢复音乐")
            return {"status": "error", "message": str(e)}
    
    def get_music_status(self) -> Dict[str, Any]:
        """获取音乐播放状态"""
        try:
            status = {
                "enabled": self.enabled,
                "is_playing": self.is_playing,
                "current_track": self.current_track,
                "current_mood": self.current_mood,
                "volume": self.volume,
                "available_moods": self.available_moods,
                "pygame_available": PYGAME_AVAILABLE
            }
            
            if PYGAME_AVAILABLE and pygame.mixer.get_init():
                status["mixer_busy"] = pygame.mixer.music.get_busy()
            
            return status
            
        except Exception as e:
            self.error_handler.handle_error(e, "获取音乐状态")
            return {"error": str(e)}
    
    def get_available_moods(self) -> List[str]:
        """获取所有可用的音乐基调"""
        return self.available_moods.copy()
    
    def get_mood_tracks(self, mood: str) -> List[str]:
        """
        获取指定基调下的所有音乐文件
        
        Args:
            mood: 基调名称
            
        Returns:
            音乐文件列表
        """
        try:
            mood_folder = self.music_folder / mood
            if not mood_folder.exists():
                return []
            
            music_files = []
            for pattern in ["*.mp3", "*.wav", "*.ogg"]:
                music_files.extend([f.name for f in mood_folder.glob(pattern)])
            
            return sorted(music_files)
            
        except Exception as e:
            logger.error(f"获取基调音乐列表失败: {e}")
            return []
    
    def smart_mood_selection(self, scenario_text: str) -> str:
        """
        基于场景文本智能选择音乐基调
        
        Args:
            scenario_text: 场景描述文本
            
        Returns:
            推荐的音乐基调
        """
        try:
            if not self.available_moods:
                return "default"
            
            # 简单的关键词匹配算法
            mood_keywords = {
                "battle": ["战斗", "打斗", "攻击", "敌人", "怪物", "危险"],
                "peaceful": ["宁静", "安静", "休息", "和平", "美丽", "温柔"],
                "mysterious": ["神秘", "未知", "奇怪", "诡异", "魔法", "古老"],
                "adventure": ["冒险", "探索", "旅行", "前进", "发现", "寻找"],
                "sad": ["悲伤", "痛苦", "失落", "眼泪", "离别", "死亡"],
                "happy": ["快乐", "高兴", "笑声", "庆祝", "胜利", "成功"]
            }
            
            scenario_lower = scenario_text.lower()
            
            # 计算每个基调的匹配分数
            mood_scores = {}
            for mood, keywords in mood_keywords.items():
                if mood in self.available_moods:
                    score = sum(1 for keyword in keywords if keyword in scenario_lower)
                    mood_scores[mood] = score
            
            # 选择分数最高的基调
            if mood_scores:
                best_mood = max(mood_scores, key=mood_scores.get)
                if mood_scores[best_mood] > 0:
                    return best_mood
            
            # 如果没有匹配，随机选择
            return random.choice(self.available_moods)
            
        except Exception as e:
            logger.error(f"智能基调选择失败: {e}")
            return self.available_moods[0] if self.available_moods else "default"
    
    def _scan_available_moods(self):
        """扫描可用的音乐基调"""
        try:
            if not self.music_folder.exists():
                logger.warning(f"音乐文件夹不存在: {self.music_folder}")
                return
            
            self.available_moods = []
            for item in self.music_folder.iterdir():
                if item.is_dir():
                    # 检查文件夹中是否有音乐文件
                    music_files = list(item.glob("*.mp3")) + \
                                 list(item.glob("*.wav")) + \
                                 list(item.glob("*.ogg"))
                    if music_files:
                        self.available_moods.append(item.name)
            
            logger.info(f"发现音乐基调: {self.available_moods}")
            
        except Exception as e:
            logger.error(f"扫描音乐基调失败: {e}")
            self.available_moods = []

# 为了保持兼容性，创建一个全局实例
music_player = None

def get_music_service(error_handler: ErrorHandler) -> MusicService:
    """获取音乐服务实例"""
    global music_player
    if music_player is None:
        music_player = MusicService(error_handler)
    return music_player

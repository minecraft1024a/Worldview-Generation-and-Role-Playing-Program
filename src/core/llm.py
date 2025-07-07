"""
WGARP 核心 LLM 模块 - 重构版本
统一的大模型调用接口，支持多个提供商，提供更好的错误处理和重试机制
"""

import openai
from dotenv import load_dotenv
import os
from typing import List, Dict, Any, Optional
import time
import json
from src.core.config import config_manager
from src.utils.error_handler import error_handler

# 加载环境变量
load_dotenv()


class LLMCore:
    """统一的大模型调用核心类"""
    
    def __init__(self):
        self.config_manager = config_manager
        # 初始化客户端字典，支持多个提供商
        self.clients = {}
        self._init_clients()
    
    def _init_clients(self):
        """初始化不同提供商的客户端"""
        try:
            providers = self.config_manager.get_all_providers()
            
            for provider in providers:
                api_url_key = f"{provider.upper()}_API_URL"
                api_url = os.getenv(api_url_key)
                
                if api_url:
                    # 获取该提供商专用的API密钥
                    try:
                        api_key = self.config_manager.get_api_key(provider)
                        self.clients[provider] = openai.OpenAI(
                            base_url=api_url,
                            api_key=api_key
                        )
                        print(f"初始化 {provider} 客户端成功")
                    except Exception as e:
                        print(f"初始化 {provider} 客户端失败: {e}")
        except Exception as e:
            print(f"初始化 LLM 客户端时发生错误: {e}")
    
    def _get_client(self, provider: str):
        """获取指定提供商的客户端"""
        if provider not in self.clients:
            # 尝试重新初始化
            self._init_clients()
            if provider not in self.clients:
                raise ValueError(f"未初始化的提供商客户端: {provider}")
        return self.clients[provider]
    
    def _make_request(self, messages: List[Dict[str, str]], model_type: str = 'role_play', 
                     max_retries: int = None) -> Optional[str]:
        """
        通用的大模型请求方法
        
        Args:
            messages: 消息列表
            model_type: 模型类型
            max_retries: 最大重试次数
            
        Returns:
            生成的文本或 None
        """
        try:
            # 获取模型配置
            config = self.config_manager.get_model_config(model_type)
            provider = config['provider']
            model_name = config['model_name']
            temperature = config['temperature']
            max_tokens = config.get('max_tokens')
            timeout = config.get('timeout', 30)
            
            # 获取重试配置
            if max_retries is None:
                api_config = self.config_manager.get_api_config()
                max_retries = api_config.get('retry_attempts', 3)
                retry_delay = api_config.get('retry_delay', 1.0)
            else:
                retry_delay = 1.0
            
            client = self._get_client(provider)
            
            # 准备请求参数
            request_params = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "timeout": timeout
            }
            
            if max_tokens:
                request_params["max_tokens"] = max_tokens
            
            # 执行请求，支持重试
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    response = client.chat.completions.create(**request_params)
                    
                    if response.choices and len(response.choices) > 0:
                        content = response.choices[0].message.content
                        if content:
                            return content.strip()
                    
                    print(f"警告: {provider} 返回空响应")
                    return None
                    
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        print(f"请求失败 (尝试 {attempt + 1}/{max_retries + 1}): {e}")
                        time.sleep(retry_delay * (attempt + 1))  # 递增延迟
                        continue
                    else:
                        break
            
            # 所有重试都失败了
            error_handler.handle_llm_error(last_exception)
            return None
            
        except Exception as e:
            error_handler.handle_llm_error(e)
            return None
    
    def generate_world(self, background: str = "地理、历史、文化、魔法体系") -> Optional[str]:
        """生成世界观"""
        messages = [
            {"role": "system", "content": "你是一个世界构建大师，擅长生成完整的世界观设定"},
            {"role": "user", "content": f"请生成一个包含{background}的完整世界观，使用中文输出"}
        ]
        return self._make_request(messages, model_type='world_generation')
    
    def generate_character(self, world_description: str, prompt: str) -> Optional[str]:
        """生成角色设定"""
        system_prompt = (
            "你是一个角色设定生成器，请根据用户的简短描述拓展出一个详细的角色设定，"
            "严格按照如下格式输出，不要添加多余内容，不要输出解释：\n"
            "姓名:\n"
            "职业:\n"
            "性别:\n"
            "年龄:\n"
            "能力:\n"
            "=====\n"
            "人物具体介绍:\n"
            "关系:\n"
            "请务必让角色的设定、背景、能力等与以下世界观保持一致：\n"
            f"{world_description}\n"
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        return self._make_request(messages, model_type='character_generation')
    
    def role_play_response(self, messages: List[Dict[str, str]], 
                          temperature: float = None) -> Optional[str]:
        """角色扮演回复"""
        # 如果指定了温度，临时修改配置
        if temperature is not None:
            # 这里可以考虑临时修改配置，但为了简单起见，暂时忽略
            pass
        
        return self._make_request(messages, model_type='role_play')
    
    def generate_summary(self, messages: List[Dict[str, str]], 
                        previous_summary: str = "", 
                        summary_type: str = "smart") -> Optional[str]:
        """
        生成对话摘要
        
        Args:
            messages: 消息列表
            previous_summary: 之前的摘要
            summary_type: 摘要类型 ('smart', 'save', 'traditional')
            
        Returns:
            生成的摘要
        """
        if summary_type == "smart":
            return self._generate_smart_summary(messages, previous_summary)
        elif summary_type == "save":
            return self._generate_save_summary(messages)
        else:
            return self._generate_traditional_summary(messages, previous_summary)
    
    def _generate_smart_summary(self, messages: List[Dict[str, str]], 
                               previous_summary: str = "") -> Optional[str]:
        """生成智能摘要"""
        if previous_summary:
            # 增量摘要
            recent_messages = messages[-6:] if len(messages) > 6 else messages
            prompt = f"之前摘要：{previous_summary}\n\n最新对话：\n"
            prompt += "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
            prompt += "\n\n请更新摘要，只需要包含最重要的剧情进展和状态变化："
        else:
            # 全新摘要
            prompt = "请总结以下对话的核心剧情和角色状态：\n"
            prompt += "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        messages_to_send = [{"role": "user", "content": prompt}]
        return self._make_request(messages_to_send, model_type='smart_summary')
    
    def _generate_save_summary(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """生成存档摘要"""
        prompt = "请对以下对话历史进行总结，提取剧情和用户的状态、身份和物品：\n"
        prompt += "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        messages_to_send = [
            {"role": "system", "content": "请对以下对话历史进行总结，提取剧情和用户的状态，身份和物品档："},
            {"role": "user", "content": prompt}
        ]
        return self._make_request(messages_to_send, model_type='save_summary')
    
    def _generate_traditional_summary(self, messages: List[Dict[str, str]], 
                                    previous_summary: str = "") -> Optional[str]:
        """生成传统摘要"""
        if previous_summary:
            recent_content = self._extract_key_content(messages[-6:])
            prompt = f"之前摘要：{previous_summary[:300]}\n最新进展：{recent_content}\n请更新摘要(限200字)："
        else:
            key_content = self._extract_key_content(messages)
            prompt = f"对话内容：{key_content}\n请生成简洁摘要(限200字)："
        
        messages_to_send = [{"role": "user", "content": prompt}]
        return self._make_request(messages_to_send, model_type='save_summary')
    
    def _extract_key_content(self, messages: List[Dict[str, str]]) -> str:
        """提取对话的关键内容"""
        key_messages = []
        for msg in messages:
            content = msg.get("content", "")
            # 过滤掉系统消息和过长的消息
            if (not self._is_system_message(content) and 
                len(content) < 500 and 
                content.strip()):
                key_messages.append(f"{msg['role']}: {content[:200]}")
        
        return "\n".join(key_messages[-10:])  # 最多保留10条关键消息
    
    def _is_system_message(self, content: str) -> bool:
        """判断是否为系统性消息"""
        system_keywords = ["正在播放", "摘要生成", "存档", "加载", "音乐", "保存"]
        return any(keyword in content for keyword in system_keywords)
    
    def generate_save_name(self, summary_text: str) -> Optional[str]:
        """根据摘要生成存档名"""
        messages = [
            {"role": "system", "content": "请根据以下剧情摘要为本次存档起一个简洁有趣的中文标题（不超过10字）："},
            {"role": "user", "content": summary_text}
        ]
        return self._make_request(messages, model_type='save_name')
    
    def select_music_mood(self, scenario: str, available_moods: List[str]) -> Optional[str]:
        """选择音乐基调"""
        prompt = f"根据以下游戏场景，从给定的音乐基调中选择最合适的一个：\n"
        prompt += f"场景：{scenario}\n"
        prompt += f"可选基调：{', '.join(available_moods)}\n"
        prompt += "请只回答基调名称，不要其他内容。"
        
        messages = [{"role": "user", "content": prompt}]
        return self._make_request(messages, model_type='music_mood')
    
    def should_change_music(self, scenario: str, current_mood: str) -> bool:
        """判断是否需要更换音乐"""
        prompt = f"当前音乐基调：{current_mood}\n场景：{scenario}\n"
        prompt += "当前音乐基调是否适合这个场景？请回答：是 或 否"
        
        messages = [{"role": "user", "content": prompt}]
        response = self._make_request(messages, model_type='music_mood')
        
        return response and "否" in response
    
    def get_available_providers(self) -> List[str]:
        """获取可用的提供商列表"""
        return list(self.clients.keys())
    
    def test_provider(self, provider: str) -> bool:
        """测试提供商连接"""
        try:
            client = self._get_client(provider)
            # 发送一个简单的测试请求
            test_messages = [{"role": "user", "content": "测试连接，请回复'OK'"}]
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # 使用一个通用模型名
                messages=test_messages,
                max_tokens=10,
                timeout=10
            )
            return response.choices and len(response.choices) > 0
        except Exception as e:
            print(f"测试 {provider} 连接失败: {e}")
            return False
    
    def reload_clients(self):
        """重新加载所有客户端"""
        self.clients.clear()
        self._init_clients()


# 创建全局LLM实例
llm_core = LLMCore()

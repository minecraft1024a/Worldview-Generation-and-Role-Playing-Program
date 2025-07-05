import openai
from dotenv import load_dotenv
import os
from src.error_handler import error_handler

# 加载环境变量
load_dotenv()

class LLMCore:
    """统一的大模型调用核心类"""
    
    def __init__(self):
        self.client = openai.OpenAI(
            base_url=os.getenv("API_URL"),
            api_key=os.getenv("API_KEY")
        )
        self.model_name = os.getenv("MODEL_NAME")
    
    def _make_request(self, messages, temperature=0.7, max_retries=3):
        """通用的大模型请求方法"""
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature
                )
                return response.choices[0].message.content
            except Exception as e:
                if attempt == max_retries - 1:
                    error_handler.handle_llm_error(e)
                    return None
                continue
        return None
    
    def generate_world(self, background="地理、历史、文化、魔法体系"):
        """生成世界观"""
        messages = [
            {"role": "system", "content": "你是一个世界构建大师，擅长生成完整的世界观设定"},
            {"role": "user", "content": f"请生成一个包含{background}的完整世界观，使用中文输出"}
        ]
        return self._make_request(messages, temperature=0.7)
    
    def generate_character(self, world_description, prompt):
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
            "【示例】\n"
            "姓名: 李明\n"
            "职业: 魔法师\n"
            "性别: 男\n"
            "年龄: 28\n"
            "能力: 精通火系魔法\n"
            "=====\n"
            "人物具体介绍: 李明出生于魔法世家，性格坚毅，善于思考。\n"
            "关系: 与导师关系密切，曾与主角有过合作。\n"
            "请严格按照上述格式输出，不要输出任何解释或多余内容。"
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        return self._make_request(messages, temperature=0.7)
    
    def generate_save_name(self, summary_text):
        """根据摘要生成存档名"""
        messages = [
            {"role": "system", "content": "请根据以下剧情摘要为本次存档起一个简洁有趣的中文标题（不超过10字）："},
            {"role": "user", "content": summary_text}
        ]
        return self._make_request(messages, temperature=0.5)
    
    def summarize_conversation(self, messages):
        """生成对话摘要"""
        messages_content = [
            {"role": "system", "content": "请对以下对话历史进行总结，提取剧情和用户的状态，身份和物品档："},
            {"role": "user", "content": "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])}
        ]
        return self._make_request(messages_content, temperature=0.5)
    
    def role_play_response(self, messages, temperature=0.7):
        """角色扮演回复"""
        return self._make_request(messages, temperature=temperature)
    
    def select_music_mood(self, scenario, available_moods):
        """选择音乐基调"""
        mood_options = "\n".join([f"- {name}" for name in available_moods])
        messages = [
            {"role": "user", "content": (
                "请根据以下情景，从下列基调中选择一个最合适的基调，只能选择并输出下列基调名称之一：\n"
                f"情景：{scenario}\n"
                f"{mood_options}\n"
                "【重要】只能输出上面列表中的一个基调名称，不能输出编号、标点、解释、换行或任何其他内容。直接输出名称本身。"
            )}
        ]
        result = self._make_request(messages, temperature=0.7)
        if result:
            return result.strip()
        return None
    
    def should_change_music(self, scenario, current_mood):
        """判断是否需要更换音乐"""
        messages = [
            {"role": "user", "content": (
                "根据当前情景和音乐基调，判断是否需要更换音乐。只输出'是'或'否'，不要添加其他内容。\n"
                f"情景：{scenario}\n"
                f"当前基调：{current_mood}\n"
            )}
        ]
        result = self._make_request(messages, temperature=0.7)
        if result:
            return result.strip() == '是'
        return False
    
    def generate_smart_summary(self, messages, previous_summary="", max_tokens=1000):
        """生成智能摘要，优化Token使用"""
        # 构建高效的摘要提示
        if previous_summary:
            # 增量摘要模式
            recent_content = self._extract_key_content(messages[-6:])
            prompt = f"之前摘要：{previous_summary[:300]}\n最新进展：{recent_content}\n请更新摘要(限200字)："
        else:
            # 全新摘要模式
            key_content = self._extract_key_content(messages)
            prompt = f"对话内容：{key_content}\n请生成简洁摘要(限200字)："
        
        messages_to_send = [{"role": "user", "content": prompt}]
        return self._make_request(messages_to_send, temperature=0.3)
    
    def _extract_key_content(self, messages):
        """提取对话的关键内容，移除冗余信息"""
        key_parts = []
        for msg in messages:
            content = msg.get("content", "")
            
            # 移除系统性信息
            if "正在播放" in content or "摘要生成" in content:
                continue
            
            # 提取核心动作和结果
            if msg.get("role") == "user" and content.startswith("我的行动："):
                action = content[5:].strip()
                key_parts.append(f"行动：{action}")
            elif msg.get("role") == "assistant":
                # 提取关键场景信息
                scenario = self._extract_scenario_info(content)
                if scenario:
                    key_parts.append(f"结果：{scenario}")
        
        return " | ".join(key_parts[-8:])  # 只保留最近8个关键点
    
    def _extract_scenario_info(self, content):
        """从AI回复中提取关键场景信息"""
        lines = content.split('\n')
        important_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('=') and '：' in line:
                # 保留包含关键信息的行
                if any(keyword in line for keyword in ['情景', '地点', '状态', '物品', '选择']):
                    important_lines.append(line)
        
        return ' '.join(important_lines[:3])  # 最多保留3行关键信息
    
    def generate_compact_save_name(self, summary):
        """生成紧凑的存档名"""
        # 使用更简短的提示来生成存档名
        short_summary = summary[:100] if len(summary) > 100 else summary
        messages = [
            {"role": "user", "content": f"为以下内容生成5字以内的标题：{short_summary}"}
        ]
        return self._make_request(messages, temperature=0.5)

# 创建全局LLM实例
llm_core = LLMCore()
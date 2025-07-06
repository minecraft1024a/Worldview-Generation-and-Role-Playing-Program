import openai
from dotenv import load_dotenv
import os
from src.error_handler import error_handler
from src.config_manager import config_manager

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
        providers = self.config_manager.get_all_providers()
        
        for provider in providers:
            api_url_key = f"{provider.upper()}_API_URL"
            api_url = os.getenv(api_url_key)
            
            if api_url:
                # 获取该提供商专用的API密钥
                api_key = self.config_manager.get_api_key(provider)
                self.clients[provider] = openai.OpenAI(
                    base_url=api_url,
                    api_key=api_key
                )
    
    def _get_client(self, provider):
        """获取指定提供商的客户端"""
        if provider not in self.clients:
            raise ValueError(f"未初始化的提供商客户端: {provider}")
        return self.clients[provider]
    
    def _make_request(self, messages, model_type, max_retries=3):
        """通用的大模型请求方法"""
        model_config = self.config_manager.get_model_config(model_type)
        client = self._get_client(model_config['provider'])
        
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=model_config['model_name'],
                    messages=messages,
                    temperature=model_config['temperature'],
                    max_tokens=model_config['max_tokens'],
                    timeout=model_config['timeout']
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
        return self._make_request(messages, model_type='world_generation')
    
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
        return self._make_request(messages, model_type='character_generation')
    
    def generate_save_name(self, summary_text):
        """根据摘要生成存档名"""
        messages = [
            {"role": "system", "content": "请根据以下剧情摘要为本次存档起一个简洁有趣的中文标题（不超过10字）："},
            {"role": "user", "content": summary_text}
        ]
        return self._make_request(messages, model_type='save_name')
    
    def summarize_conversation(self, messages):
        """生成对话摘要"""
        messages_content = [
            {"role": "system", "content": "请对以下对话历史进行总结，提取剧情和用户的状态，身份和物品档："},
            {"role": "user", "content": "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])}
        ]
        return self._make_request(messages_content, model_type='save_summary')
    
    def role_play_response(self, messages, temperature=0.7):
        """角色扮演回复"""
        return self._make_request(messages, model_type='role_play')
    
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
        result = self._make_request(messages, model_type='music_mood')
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
        result = self._make_request(messages, model_type='music_mood')
        if result:
            return result.strip() == '是'
        return False
    
    def generate_smart_summary(self, messages, previous_summary="", max_tokens=1000, enable_optimization=True):
        """生成智能摘要，优化Token使用和内容质量"""
        if enable_optimization:
            # 智能摘要模式：提取关键信息
            if previous_summary:
                # 增量摘要：基于上次摘要更新
                summary = self._generate_incremental_summary(messages, previous_summary, max_tokens)
            else:
                # 全新摘要：从零开始
                summary = self._generate_comprehensive_summary(messages, max_tokens)
        else:
            # 传统摘要模式：保持原有逻辑
            summary = self._generate_traditional_summary(messages, previous_summary)
        
        return summary
    
    def _generate_incremental_summary(self, messages, previous_summary, max_tokens):
        """生成增量摘要，基于之前的摘要进行更新"""
        # 提取最近的重要对话内容
        recent_content = self._extract_recent_key_events(messages[-10:])
        
        if not recent_content:
            return previous_summary
        
        # 构建增量更新提示
        prompt = (
            f"基于以下摘要和最新进展，更新摘要内容（控制在{max_tokens//5}字以内）：\n"
            f"【原摘要】{previous_summary[:400]}\n"
            f"【最新进展】{recent_content}\n"
            "请合并信息，保持连贯性，突出重要变化："
        )
        
        messages_to_send = [{"role": "user", "content": prompt}]
        return self._make_request(messages_to_send, model_type='save_summary')
    
    def _generate_comprehensive_summary(self, messages, max_tokens):
        """生成全面摘要，从完整对话中提取核心信息"""
        # 智能提取对话中的关键要素
        key_elements = self._extract_story_elements(messages)
        
        if not key_elements:
            return "暂无重要情节"
        
        prompt = (
            f"根据以下关键要素生成故事摘要（控制在{max_tokens//5}字以内）：\n"
            f"{key_elements}\n"
            "要求：1）突出主要情节线 2）保留重要角色和事件 3）语言简洁流畅"
        )
        
        messages_to_send = [{"role": "user", "content": prompt}]
        return self._make_request(messages_to_send, model_type='save_summary')
    
    def _generate_traditional_summary(self, messages, previous_summary):
        """传统摘要生成方式（兼容性保留）"""
        if previous_summary:
            recent_content = self._extract_key_content(messages[-6:])
            prompt = f"之前摘要：{previous_summary[:300]}\n最新进展：{recent_content}\n请更新摘要(限200字)："
        else:
            key_content = self._extract_key_content(messages)
            prompt = f"对话内容：{key_content}\n请生成简洁摘要(限200字)："
        
        messages_to_send = [{"role": "user", "content": prompt}]
        return self._make_request(messages_to_send, model_type='save_summary')
    
    def _extract_recent_key_events(self, recent_messages):
        """从最近的对话中提取关键事件"""
        key_events = []
        
        for i, msg in enumerate(recent_messages):
            content = msg.get("content", "")
            role = msg.get("role", "")
            
            # 跳过系统性消息
            if self._is_system_message(content):
                continue
            
            # 提取用户行动
            if role == "user":
                action = self._extract_user_action(content)
                if action:
                    key_events.append(f"玩家行动：{action}")
            
            # 提取重要结果
            elif role == "assistant":
                result = self._extract_important_result(content)
                if result:
                    key_events.append(f"结果：{result}")
        
        return " | ".join(key_events[-5:])  # 保留最近5个关键事件
    
    def _extract_story_elements(self, messages):
        """从完整对话中提取故事要素"""
        elements = {
            "characters": set(),
            "locations": set(),
            "events": [],
            "items": set(),
            "relationships": []
        }
        
        for msg in messages:
            content = msg.get("content", "")
            
            if self._is_system_message(content):
                continue
            
            # 提取角色名称
            self._extract_characters(content, elements["characters"])
            
            # 提取地点信息
            self._extract_locations(content, elements["locations"])
            
            # 提取重要事件
            if msg.get("role") == "assistant":
                event = self._extract_plot_event(content)
                if event:
                    elements["events"].append(event)
            
            # 提取物品
            self._extract_items(content, elements["items"])
        
        return self._format_story_elements(elements)
    
    def _is_system_message(self, content):
        """判断是否为系统性消息"""
        system_keywords = ["正在播放", "摘要生成", "存档", "加载", "音乐", "保存"]
        return any(keyword in content for keyword in system_keywords)
    
    def _extract_user_action(self, content):
        """提取用户行动的核心内容"""
        if content.startswith("我的行动："):
            return content[5:].strip()
        elif content.startswith("我"):
            # 提取"我..."形式的行动描述
            action_line = content.split('\n')[0]
            if len(action_line) <= 50:  # 避免过长的描述
                return action_line.strip()
        return None
    
    def _extract_important_result(self, content):
        """从AI回复中提取重要结果"""
        lines = content.split('\n')
        important_info = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('='):
                continue
            
            # 关键信息标识
            if any(keyword in line for keyword in ['发现', '获得', '遇到', '到达', '死亡', '成功', '失败']):
                if len(line) <= 100:  # 避免过长描述
                    important_info.append(line)
            
            # 状态变化
            elif '：' in line and any(keyword in line for keyword in ['生命', '魔法', '经验', '金币', '物品']):
                important_info.append(line)
        
        return ' '.join(important_info[:2])  # 最多保留2条重要信息
    
    def _extract_characters(self, content, characters_set):
        """提取角色名称"""
        # 简单的角色名提取逻辑（可根据需要改进）
        import re
        # 匹配中文姓名模式
        names = re.findall(r'([A-Za-z\u4e00-\u9fa5]{2,4})(?=说|道|告诉|回答)', content)
        for name in names:
            if len(name) >= 2:
                characters_set.add(name)
    
    def _extract_locations(self, content, locations_set):
        """提取地点信息"""
        import re
        # 匹配地点模式
        locations = re.findall(r'(?:到达|前往|来到|进入)([A-Za-z\u4e00-\u9fa5]{2,8})', content)
        for location in locations:
            locations_set.add(location)
    
    def _extract_plot_event(self, content):
        """提取情节事件"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            # 寻找包含动作动词的重要事件
            if any(verb in line for verb in ['战斗', '对话', '探索', '解谜', '交易', '学习']):
                if 20 <= len(line) <= 80:  # 合适长度的事件描述
                    return line
        return None
    
    def _extract_items(self, content, items_set):
        """提取物品信息"""
        import re
        # 匹配物品模式
        items = re.findall(r'(?:获得|得到|拿到|发现)([A-Za-z\u4e00-\u9fa5]{2,8})', content)
        for item in items:
            items_set.add(item)
    
    def _format_story_elements(self, elements):
        """格式化故事要素为摘要用的文本"""
        formatted_parts = []
        
        if elements["characters"]:
            chars = ', '.join(list(elements["characters"])[:5])
            formatted_parts.append(f"角色：{chars}")
        
        if elements["locations"]:
            locs = ', '.join(list(elements["locations"])[:3])
            formatted_parts.append(f"地点：{locs}")
        
        if elements["events"]:
            events = ' | '.join(elements["events"][-3:])
            formatted_parts.append(f"事件：{events}")
        
        if elements["items"]:
            items = ', '.join(list(elements["items"])[:5])
            formatted_parts.append(f"物品：{items}")
        
        return '\n'.join(formatted_parts)
    
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
    
    def generate_compact_save_name(self, summary, context_info=""):
        """生成紧凑且有意义的存档名"""
        # 从摘要中提取关键词
        key_points = self._extract_save_name_keywords(summary)
        
        # 构建优化的提示
        if context_info:
            prompt = f"基于以下信息生成4-6字的存档标题：\n摘要：{summary[:80]}\n背景：{context_info[:50]}\n关键词：{key_points}"
        else:
            prompt = f"为以下内容生成4-6字的精炼标题：\n{summary[:100]}\n关键词：{key_points}"
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        result = self._make_request(messages, model_type='save_name')
        
        # 清理和验证结果
        if result:
            cleaned_name = self._clean_save_name(result.strip())
            return cleaned_name if cleaned_name else self._generate_fallback_name(summary)
        
        return self._generate_fallback_name(summary)
    
    def _extract_save_name_keywords(self, summary):
        """从摘要中提取用于生成存档名的关键词"""
        import re
        
        # 提取重要名词和动词
        keywords = []
        
        # 地点关键词
        location_pattern = r'(?:到达|前往|来到|在)([A-Za-z\u4e00-\u9fa5]{2,6})'
        locations = re.findall(location_pattern, summary)
        keywords.extend(locations[:2])
        
        # 行动关键词
        action_pattern = r'(战斗|探索|对话|交易|学习|解谜|逃跑|拯救|寻找)'
        actions = re.findall(action_pattern, summary)
        keywords.extend(actions[:2])
        
        # 物品关键词
        item_pattern = r'(?:获得|得到|发现)([A-Za-z\u4e00-\u9fa5]{2,6})'
        items = re.findall(item_pattern, summary)
        keywords.extend(items[:1])
        
        return ' '.join(keywords[:4]) if keywords else "冒险"
    
    def _clean_save_name(self, name):
        """清理存档名，移除不合适的字符"""
        import re
        
        # 移除标点符号和特殊字符
        cleaned = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', name)
        
        # 确保长度合适
        if 2 <= len(cleaned) <= 8:
            return cleaned
        elif len(cleaned) > 8:
            return cleaned[:6]
        
        return None
    
    def _generate_fallback_name(self, summary):
        """生成备用存档名"""
        import re
        from datetime import datetime
        
        # 尝试从摘要中提取第一个有意义的词
        words = re.findall(r'[\u4e00-\u9fa5]{2,4}', summary)
        if words:
            return words[0][:4]
        
        # 最后备用：使用时间戳
        now = datetime.now()
        return f"存档{now.strftime('%m%d')}"
    
    def generate_enhanced_summary(self, messages, previous_summary="", session_context=""):
        """使用专门的智能摘要模型生成高质量摘要"""
        try:
            # 使用专用的智能摘要模型
            if previous_summary:
                summary = self._generate_incremental_summary_enhanced(messages, previous_summary, session_context)
            else:
                summary = self._generate_comprehensive_summary_enhanced(messages, session_context)
            
            return summary
        except Exception as e:
            # 回退到标准摘要
            error_handler.handle_llm_error(e)
            return self.generate_smart_summary(messages, previous_summary, enable_optimization=False)
    
    def _generate_incremental_summary_enhanced(self, messages, previous_summary, session_context):
        """使用智能摘要模型生成增量摘要"""
        recent_events = self._extract_recent_key_events(messages[-8:])
        
        prompt = (
            f"作为故事摘要专家，请更新以下摘要：\n"
            f"【会话背景】{session_context}\n"
            f"【当前摘要】{previous_summary[:400]}\n"
            f"【新增事件】{recent_events}\n\n"
            f"要求：\n"
            f"1. 保持故事连贯性\n"
            f"2. 突出重要变化和进展\n"
            f"3. 控制在300字以内\n"
            f"4. 保留关键角色、地点、物品信息"
        )
        
        messages_to_send = [{"role": "user", "content": prompt}]
        return self._make_request(messages_to_send, model_type='smart_summary')
    
    def _generate_comprehensive_summary_enhanced(self, messages, session_context):
        """使用智能摘要模型生成全面摘要"""
        story_elements = self._extract_story_elements(messages)
        
        prompt = (
            f"作为故事摘要专家，请为以下冒险生成摘要：\n"
            f"【背景设定】{session_context}\n"
            f"【故事要素】\n{story_elements}\n\n"
            f"要求：\n"
            f"1. 构建完整的故事脉络\n"
            f"2. 突出主要情节和角色发展\n"
            f"3. 控制在400字以内\n"
            f"4. 语言生动，具有故事性"
        )
        
        messages_to_send = [{"role": "user", "content": prompt}]
        return self._make_request(messages_to_send, model_type='smart_summary')

# 创建全局LLM实例
llm_core = LLMCore()
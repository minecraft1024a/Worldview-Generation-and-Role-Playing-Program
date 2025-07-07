"""
世界观生成服务
提供世界观生成的核心功能，支持多种生成策略和模板
"""

from typing import Optional, Dict, Any, List
from src.models import WorldDescription, APIResponse
from src.core.config import config_manager
from src.core.llm import llm_core
from src.utils.error_handler import logger
import json
import random


class WorldGenerationService:
    """世界观生成服务"""
    
    def __init__(self):
        self.config = config_manager
        self.llm = llm_core
        
        # 预定义的世界观模板
        self.templates = {
            "fantasy": {
                "name": "奇幻世界",
                "prompt": "创造一个包含魔法、神话生物、古老文明的奇幻世界",
                "elements": ["魔法体系", "种族设定", "神话传说", "古老文明", "地理环境"]
            },
            "scifi": {
                "name": "科幻世界", 
                "prompt": "构建一个科技发达、星际文明、未来科技的科幻世界",
                "elements": ["科技水平", "星际政治", "人工智能", "宇宙探索", "未来社会"]
            },
            "cyberpunk": {
                "name": "赛博朋克",
                "prompt": "设计一个高科技低生活、企业控制、网络空间的赛博朋克世界", 
                "elements": ["网络空间", "企业势力", "街头文化", "改造人", "数字社会"]
            },
            "wuxia": {
                "name": "武侠仙侠",
                "prompt": "创建一个武林门派、修仙体系、江湖恩怨的古风武侠世界",
                "elements": ["武学体系", "门派势力", "修仙等级", "江湖规则", "古代文化"]
            },
            "modern": {
                "name": "现代都市",
                "prompt": "构造一个现代都市、日常生活、现实背景的当代世界", 
                "elements": ["都市环境", "社会结构", "生活方式", "文化背景", "现代科技"]
            },
            "historical": {
                "name": "历史时代",
                "prompt": "重现某个历史时期的真实环境、社会制度、文化背景",
                "elements": ["历史背景", "社会制度", "文化习俗", "政治结构", "经济体系"]
            }
        }
    
    def generate_world(self, background: str = "", template_type: str = None) -> APIResponse:
        """
        生成世界观
        
        Args:
            background: 用户提供的背景描述
            template_type: 模板类型，如果不提供则自动推断
            
        Returns:
            APIResponse: 包含生成结果的响应
        """
        try:
            # 构建生成提示
            if template_type and template_type in self.templates:
                template = self.templates[template_type]
                enhanced_prompt = self._build_template_prompt(template, background)
            else:
                enhanced_prompt = self._build_custom_prompt(background)
            
            logger.info(f"开始生成世界观，背景: {background[:50]}...")
            
            # 调用 LLM 生成
            world_content = self.llm.generate_world(enhanced_prompt)
            
            if not world_content:
                return APIResponse(
                    success=False,
                    message="世界观生成失败，请重试"
                )
            
            # 创建世界观对象
            world_desc = WorldDescription(
                content=world_content,
                background_prompt=background,
                metadata={
                    "template_type": template_type,
                    "enhanced_prompt": enhanced_prompt,
                    "generation_method": "llm"
                }
            )
            
            logger.info("世界观生成成功")
            
            return APIResponse(
                success=True,
                data=world_desc.to_dict(),
                message="世界观生成成功"
            )
            
        except Exception as e:
            logger.error(f"生成世界观时发生错误: {e}")
            return APIResponse(
                success=False,
                message=f"生成世界观时发生错误: {str(e)}",
                error_code="GENERATION_ERROR"
            )
    
    def _build_template_prompt(self, template: Dict[str, Any], background: str) -> str:
        """根据模板构建提示"""
        base_prompt = template["prompt"]
        elements = template["elements"]
        
        if background:
            prompt = f"{base_prompt}。\n\n用户要求: {background}\n\n"
        else:
            prompt = f"{base_prompt}。\n\n"
        
        prompt += "请详细描述以下方面:\n"
        for i, element in enumerate(elements, 1):
            prompt += f"{i}. {element}\n"
        
        prompt += "\n请用中文输出，内容丰富详细，具有想象力和创造性。"
        
        return prompt
    
    def _build_custom_prompt(self, background: str) -> str:
        """构建自定义提示"""
        if not background:
            background = "地理、历史、文化、魔法体系"
        
        prompt = f"""请生成一个包含{background}的完整世界观，要求：

1. 地理环境: 描述世界的地理特征、气候、重要地点
2. 历史背景: 重要历史事件、文明发展、传说故事  
3. 文化体系: 社会结构、风俗习惯、语言文字
4. 政治结构: 政府形式、权力分配、主要势力
5. 经济体系: 贸易方式、货币制度、资源分布
6. 特殊元素: 魔法、科技、超自然现象等独特设定

请用中文输出，内容详细丰富，具有内在逻辑性和创造性。"""

        return prompt
    
    def get_available_templates(self) -> List[Dict[str, str]]:
        """获取可用的世界观模板"""
        return [
            {
                "type": key,
                "name": template["name"],
                "description": template["prompt"]
            }
            for key, template in self.templates.items()
        ]
    
    def suggest_template(self, background: str) -> Optional[str]:
        """根据背景描述推荐模板"""
        background_lower = background.lower()
        
        keywords = {
            "fantasy": ["魔法", "奇幻", "精灵", "矮人", "法师", "剑与魔法", "龙"],
            "scifi": ["科幻", "太空", "星际", "机器人", "未来", "科技", "外星"],
            "cyberpunk": ["赛博朋克", "黑客", "网络", "企业", "改造人", "数字"],
            "wuxia": ["武侠", "仙侠", "修仙", "江湖", "武林", "门派", "内功"],
            "modern": ["现代", "都市", "当代", "现实", "日常"],
            "historical": ["历史", "古代", "传统", "古典", "朝代"]
        }
        
        scores = {}
        for template_type, words in keywords.items():
            score = sum(1 for word in words if word in background_lower)
            if score > 0:
                scores[template_type] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return None
    
    def regenerate_world(self, previous_world: WorldDescription, 
                        feedback: str = "") -> APIResponse:
        """
        基于反馈重新生成世界观
        
        Args:
            previous_world: 之前生成的世界观
            feedback: 用户反馈
            
        Returns:
            APIResponse: 新的世界观
        """
        try:
            original_prompt = previous_world.background_prompt
            
            if feedback:
                enhanced_prompt = f"""之前生成的世界观:
{previous_world.content[:500]}...

用户反馈: {feedback}

请根据反馈重新生成世界观，在保持原有风格的基础上进行改进。
原始要求: {original_prompt}"""
            else:
                enhanced_prompt = f"请重新生成世界观，要求: {original_prompt}"
            
            world_content = self.llm.generate_world(enhanced_prompt)
            
            if not world_content:
                return APIResponse(
                    success=False,
                    message="重新生成失败，请重试"
                )
            
            new_world = WorldDescription(
                content=world_content,
                background_prompt=original_prompt,
                metadata={
                    "regeneration": True,
                    "feedback": feedback,
                    "previous_version": previous_world.to_dict()
                }
            )
            
            return APIResponse(
                success=True,
                data=new_world.to_dict(),
                message="世界观重新生成成功"
            )
            
        except Exception as e:
            logger.error(f"重新生成世界观时发生错误: {e}")
            return APIResponse(
                success=False,
                message=f"重新生成失败: {str(e)}",
                error_code="REGENERATION_ERROR"
            )


# 创建全局实例
world_generation_service = WorldGenerationService()

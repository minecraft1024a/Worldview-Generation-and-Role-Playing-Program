"""
角色生成服务
提供角色创建、修改和管理功能
"""

import logging
from typing import Optional, Dict, Any
from ..core.llm import LLMService
from ..models import CharacterModel
from ..utils.error_handler import ErrorHandler

logger = logging.getLogger(__name__)

class CharacterGenerationService:
    """角色生成服务类"""
    
    def __init__(self, llm_service: LLMService, error_handler: ErrorHandler):
        self.llm_service = llm_service
        self.error_handler = error_handler
    
    async def generate_character(
        self, 
        world_description: str, 
        prompt: str,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Optional[CharacterModel]:
        """
        根据世界观描述和提示词生成角色
        
        Args:
            world_description: 世界观描述
            prompt: 角色生成提示词
            user_preferences: 用户偏好设置
            
        Returns:
            生成的角色模型，失败时返回None
        """
        try:
            logger.info(f"开始生成角色，提示词: {prompt[:50]}...")
            
            # 构建角色生成的系统提示
            system_prompt = self._build_character_generation_prompt(world_description)
            
            # 调用LLM生成角色
            character_description = await self.llm_service.generate_character(
                world_description=world_description,
                user_prompt=prompt,
                system_prompt=system_prompt
            )
            
            if not character_description:
                logger.warning("LLM返回空的角色描述")
                return None
            
            # 创建角色模型
            character = CharacterModel(
                name=self._extract_character_name(character_description),
                description=character_description,
                world_context=world_description,
                creation_prompt=prompt,
                preferences=user_preferences or {}
            )
            
            logger.info(f"成功生成角色: {character.name}")
            return character
            
        except Exception as e:
            self.error_handler.handle_error(e, "角色生成")
            return None
    
    async def modify_character(
        self, 
        character: CharacterModel, 
        modification_prompt: str
    ) -> Optional[CharacterModel]:
        """
        修改现有角色
        
        Args:
            character: 现有角色模型
            modification_prompt: 修改提示词
            
        Returns:
            修改后的角色模型，失败时返回None
        """
        try:
            logger.info(f"开始修改角色: {character.name}")
            
            # 构建修改提示
            system_prompt = f"""
            你需要根据用户的修改要求，对以下角色进行调整：
            
            原角色描述：
            {character.description}
            
            请根据用户的修改要求进行调整，保持角色的核心特征，但按要求进行必要的修改。
            """
            
            # 调用LLM修改角色
            modified_description = await self.llm_service.generate_text(
                prompt=modification_prompt,
                system_prompt=system_prompt
            )
            
            if not modified_description:
                logger.warning("LLM返回空的修改结果")
                return None
            
            # 更新角色模型
            character.description = modified_description
            character.name = self._extract_character_name(modified_description)
            character.modification_history.append({
                "prompt": modification_prompt,
                "timestamp": character.created_at.isoformat()
            })
            
            logger.info(f"成功修改角色: {character.name}")
            return character
            
        except Exception as e:
            self.error_handler.handle_error(e, "角色修改")
            return None
    
    def validate_character(self, character: CharacterModel) -> Dict[str, Any]:
        """
        验证角色设定的完整性和合理性
        
        Args:
            character: 角色模型
            
        Returns:
            验证结果字典
        """
        try:
            validation_result = {
                "is_valid": True,
                "warnings": [],
                "errors": []
            }
            
            # 检查必要字段
            if not character.name or len(character.name.strip()) == 0:
                validation_result["errors"].append("角色缺少名称")
                validation_result["is_valid"] = False
            
            if not character.description or len(character.description.strip()) < 50:
                validation_result["warnings"].append("角色描述过于简短")
            
            # 检查描述长度
            if len(character.description) > 2000:
                validation_result["warnings"].append("角色描述过长，可能影响性能")
            
            # 检查角色与世界观的一致性
            if character.world_context and character.description:
                consistency_score = self._check_world_consistency(
                    character.description, 
                    character.world_context
                )
                if consistency_score < 0.7:
                    validation_result["warnings"].append("角色与世界观设定可能不够一致")
            
            logger.info(f"角色验证完成: {character.name}, 有效性: {validation_result['is_valid']}")
            return validation_result
            
        except Exception as e:
            self.error_handler.handle_error(e, "角色验证")
            return {
                "is_valid": False,
                "errors": ["验证过程发生错误"],
                "warnings": []
            }
    
    def _build_character_generation_prompt(self, world_description: str) -> str:
        """构建角色生成的系统提示"""
        return f"""
        你是一个专业的角色设定生成器。请根据以下世界观设定和用户需求，生成一个详细、生动的角色设定。

        世界观背景：
        {world_description}

        请生成包含以下要素的角色设定：
        1. 角色姓名
        2. 基本信息（年龄、性别、职业等）
        3. 外貌特征
        4. 性格特点
        5. 背景故事
        6. 技能和能力
        7. 目标和动机
        8. 与世界观的关联

        请确保角色设定与世界观保持一致，具有独特性和趣味性。
        """
    
    def _extract_character_name(self, description: str) -> str:
        """从角色描述中提取角色名称"""
        try:
            lines = description.split('\n')
            for line in lines[:5]:  # 在前5行中查找
                line = line.strip()
                if any(keyword in line.lower() for keyword in ['名字', '姓名', 'name', '名称']):
                    # 提取冒号或其他分隔符后的内容
                    if '：' in line:
                        return line.split('：')[1].strip()
                    elif ':' in line:
                        return line.split(':')[1].strip()
                    elif '是' in line:
                        parts = line.split('是')
                        if len(parts) > 1:
                            return parts[1].strip()
            
            # 如果没有找到明确的名称，返回默认值
            return "未命名角色"
            
        except Exception:
            return "未命名角色"
    
    def _check_world_consistency(self, character_desc: str, world_desc: str) -> float:
        """
        检查角色与世界观的一致性
        返回0-1之间的分数
        """
        try:
            # 简单的关键词匹配算法
            # 在实际应用中可以使用更复杂的NLP技术
            
            world_keywords = set(world_desc.lower().split())
            char_keywords = set(character_desc.lower().split())
            
            # 计算关键词重叠度
            common_keywords = world_keywords.intersection(char_keywords)
            total_keywords = len(world_keywords.union(char_keywords))
            
            if total_keywords == 0:
                return 0.5  # 默认中等一致性
            
            consistency_score = len(common_keywords) / total_keywords
            return min(consistency_score * 2, 1.0)  # 放大分数并限制在1.0以内
            
        except Exception:
            return 0.5  # 出错时返回中等一致性

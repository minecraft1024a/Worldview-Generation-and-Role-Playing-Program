from src.llm_core import llm_core
from src.error_handler import error_handler
import os
import json
import time
from datetime import datetime

class SaveManager:
    """智能存档管理器"""
    
    def __init__(self):
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _compress_messages(self, messages):
        """压缩消息格式，移除冗余信息"""
        compressed = []
        for msg in messages[-10:]:  # 只保留最近10条消息
            if msg["role"] == "user":
                # 提取用户行动的核心内容
                content = msg["content"]
                if content.startswith("我的行动："):
                    content = content[5:]  # 移除"我的行动："前缀
                compressed.append({"r": "u", "c": content})
            elif msg["role"] == "assistant":
                # 只保留核心场景信息，去除格式化内容
                content = self._extract_core_scenario(msg["content"])
                compressed.append({"r": "a", "c": content})
        return compressed
    
    def _extract_core_scenario(self, content):
        """从AI回复中提取核心场景信息"""
        # 移除音乐相关信息
        lines = content.split('\n')
        filtered_lines = []
        for line in lines:
            if not ('正在播放' in line or '摘要生成完成' in line):
                filtered_lines.append(line)
        
        core_content = '\n'.join(filtered_lines).strip()
        # 限制长度以节省tokens
        if len(core_content) > 800:
            core_content = core_content[:800] + "..."
        return core_content
    
    def generate_smart_summary(self, messages, previous_summary=""):
        """生成智能增量摘要"""
        # 只对新的对话内容生成摘要
        recent_messages = messages[-6:] if len(messages) > 6 else messages
        
        # 如果有之前的摘要，只需要更新摘要
        if previous_summary:
            prompt = f"之前摘要：{previous_summary}\n\n最新对话：\n"
            prompt += "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
            prompt += "\n\n请更新摘要，只需要包含最重要的剧情进展和状态变化："
        else:
            prompt = "请总结以下对话的核心剧情和角色状态：\n"
            prompt += "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
        
        return llm_core.summarize_conversation([{"role": "user", "content": prompt}])
    
    def save_game_state(self, messages, world_description, save_name=None, role=None, previous_summary=""):
        """保存游戏状态（智能增量保存）"""
        try:
            # 生成增量摘要
            current_summary = self.generate_smart_summary(messages, previous_summary)
            if not current_summary:
                return "", None
            
            # 生成存档名（如果需要）
            if not save_name:
                save_name = self._generate_save_name(current_summary)
            
            # 压缩最近的对话
            compressed_messages = self._compress_messages(messages)
            
            # 构建存档数据
            save_data = {
                "summary": current_summary,
                "world": world_description,
                "role": role,
                "recent_context": compressed_messages,
                "last_updated": datetime.now().isoformat(),
                "version": "2.0"  # 新版本标识
            }
            
            # 保存到文件
            file_path = f"{self.data_dir}/{save_name}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            return current_summary, save_name
            
        except Exception as e:
            error_handler.handle_llm_error(e)
            return "", None
    
    def _generate_save_name(self, summary):
        """生成存档名"""
        # 使用更简短的提示
        save_name = llm_core.generate_save_name(summary[:200])  # 只发送前200字符
        if save_name:
            save_name = save_name.strip().replace(" ", "")
            # 移除换行符和回车符
            save_name = save_name.replace("\\n", "").replace("\\r", "")
            for ch in r'\\/:*?\"<>|':
                save_name = save_name.replace(ch, "")
            timestamp = int(time.time())
            return f"{save_name}_{timestamp}"
        else:
            return f"存档_{int(time.time())}"
    
    def load_game_state(self, save_name):
        """加载游戏状态"""
        file_path = f"{self.data_dir}/{save_name}.json"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 检查版本兼容性
            version = data.get("version", "1.0")
            if version == "2.0":
                return self._load_v2_format(data)
            else:
                return self._load_v1_format(data)
                
        except FileNotFoundError:
            print(f"存档文件 {save_name} 不存在")
            return None, None, None, None, None
        except Exception as e:
            error_handler.handle_llm_error(e)
            return None, None, None, None, None
    
    def _load_v2_format(self, data):
        """加载新版本格式的存档"""
        # 重建最后的对话上下文
        last_conversation = None
        if data.get("recent_context"):
            # 展开压缩的消息格式
            last_msg = data["recent_context"][-1]
            if last_msg.get("r") == "a":  # assistant message
                last_conversation = {
                    "role": "assistant",
                    "content": last_msg.get("c", "")
                }
        
        return (
            data.get("world", ""),
            data.get("summary", ""),
            None,  # save_name 由调用者管理
            last_conversation,
            data.get("role", "")
        )
    
    def _load_v1_format(self, data):
        """加载旧版本格式的存档（向后兼容）"""
        return (
            data.get("world_description", ""),
            data.get("latest_summary", ""),
            None,
            data.get("last_conversation"),
            data.get("role", "")
        )
    
    def get_save_list(self):
        """获取存档列表"""
        if not os.path.exists(self.data_dir):
            return []
        
        files = []
        for f in os.listdir(self.data_dir):
            if f.endswith('.json'):
                try:
                    # 获取存档的基本信息
                    file_path = f"{self.data_dir}/{f}"
                    with open(file_path, "r", encoding="utf-8") as file:
                        data = json.load(file)
                    
                    # 获取存档的显示信息
                    save_info = {
                        "filename": f[:-5],  # 去除.json后缀
                        "last_updated": data.get("last_updated", "未知"),
                        "summary_preview": self._get_summary_preview(data)
                    }
                    files.append(save_info)
                except:
                    # 如果文件损坏，跳过
                    continue
        
        # 按更新时间排序
        files.sort(key=lambda x: x["last_updated"], reverse=True)
        return files
    
    def _get_summary_preview(self, data):
        """获取存档摘要预览"""
        summary = data.get("summary", data.get("latest_summary", ""))
        if len(summary) > 50:
            return summary[:50] + "..."
        return summary
    
    def delete_save(self, save_name):
        """删除存档"""
        file_path = f"{self.data_dir}/{save_name}.json"
        try:
            os.remove(file_path)
            return True
        except:
            return False

# 创建全局存档管理器实例
save_manager = SaveManager()

# 向后兼容的函数
def summarize_and_save(messages, world_description, save_name=None, role=None):
    """向后兼容的摘要保存函数"""
    return save_manager.save_game_state(messages, world_description, save_name, role)

def save_summary_to_json(summary_text, world_description, save_name, last_conversation=None, role=None):
    """向后兼容的保存函数"""
    # 这个函数在新系统中不再需要，但保留以兼容旧代码
    pass

def save_last_conversation(save_name, last_conversation):
    """向后兼容的最后对话保存函数"""
    # 在新系统中，这个信息已经包含在主存档中
    pass


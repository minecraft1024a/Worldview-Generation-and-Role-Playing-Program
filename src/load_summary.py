import json
import os
import toml
from src.summary import save_manager
from src.error_handler import error_handler

class SaveLoader:
    """智能存档加载器"""
    
    def __init__(self):
        self.save_manager = save_manager
        self.config = toml.load('config.toml')
    
    def load_summary(self):
        """
        智能加载存档，提供更好的用户体验
        返回 (world_description, summary_text, save_name, last_conversation, role)
        """
        saves = self.save_manager.get_save_list()
        
        if not saves:
            print("📁 未找到任何存档文件")
            print("💡 提示：需要先进行游戏并生成存档")
            return None, None, None, None, None
        
        while True:
            self._display_saves(saves)
            
            try:
                choice = input("\n请选择操作 (输入数字或命令): ").strip()
                
                if choice == "0" or choice.lower() in ["q", "quit", "退出"]:
                    print("👋 已取消")
                    return None, None, None, None, None
                
                if choice.lower() in ["r", "refresh", "刷新"]:
                    saves = self.save_manager.get_save_list()
                    os.system('cls')
                    continue
                
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(saves):
                        return self._handle_save_operation(saves[idx])
                    else:
                        print("❌ 编号超出范围")
                        continue
                except ValueError:
                    print("❌ 请输入有效的数字")
                    continue
                    
            except KeyboardInterrupt:
                print("\n👋 已取消操作")
                return None, None, None, None, None
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                return None, None, None, None, None
    
    def _display_saves(self, saves):
        """显示存档列表"""
        print("\n" + "="*60)
        print("📚 可用存档列表")
        print("="*60)
        
        for idx, save in enumerate(saves):
            print(f"[{idx+1:2d}] 📄 {save['filename']}")
            print(f"     📅 {self._format_time(save['last_updated'])}")
            print(f"     📖 {save['summary_preview']}")
            print()
        
        print("[0] ❌ 取消")
        print("命令: r/refresh (刷新列表)")
        print("="*60)
    
    def _format_time(self, time_str):
        """格式化时间显示"""
        if time_str == "未知":
            return "未知时间"
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(time_str)
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return time_str
    
    def _handle_save_operation(self, save_info):
        """处理存档操作"""
        save_name = save_info['filename']
        
        print(f"\n📄 选中存档: {save_name}")
        print(f"📅 更新时间: {self._format_time(save_info['last_updated'])}")
        print(f"📖 摘要预览: {save_info['summary_preview']}")
        
        while True:
            action = input("\n请选择操作 [1-载入 / 2-删除 / 0-返回]: ").strip()
            
            if action == "0":
                os.system('cls')
                return "continue", None, None, None, None  # 特殊返回值表示继续循环
            
            elif action == "1":
                return self._load_save(save_name)
            
            elif action == "2":
                return self._delete_save(save_name, save_info)
            
            else:
                print("❌ 无效操作，请输入 1、2 或 0")
    
    def _load_save(self, save_name):
        """加载存档"""
        try:
            print("⏳ 正在加载存档...")
            result = self.save_manager.load_game_state(save_name)
            
            if result[0] is None:  # 加载失败
                print("❌ 存档加载失败")
                input("按回车键继续...")
                os.system('cls')
                return "continue", None, None, None, None
            
            world_desc, summary, _, last_conv, role = result
            print("✅ 存档加载成功!")
            print(f"🌍 世界观: {world_desc[:100]}{'...' if len(world_desc) > 100 else ''}")
            print(f"👤 角色: {role[:50] if role else '未设定'}{'...' if role and len(role) > 50 else ''}")
            print(f"📜 剧情: {summary[:100]}{'...' if len(summary) > 100 else ''}")
            
            input("\n按回车键开始游戏...")
            os.system('cls')
            
            return world_desc, summary, save_name, last_conv, role
            
        except Exception as e:
            error_handler.handle_llm_error(e)
            print("❌ 加载存档时发生错误")
            input("按回车键继续...")
            os.system('cls')
            return "continue", None, None, None, None
    
    def _delete_save(self, save_name, save_info):
        """删除存档"""
        print(f"\n⚠️  危险操作：删除存档")
        print(f"📄 存档名: {save_name}")
        print(f"📖 内容: {save_info['summary_preview']}")
        print(f"⚠️  此操作不可恢复！")
        
        confirm = input("\n确认删除? 请输入 'DELETE' 来确认: ").strip()
        
        if confirm == "DELETE":
            if self.save_manager.delete_save(save_name):
                print("✅ 存档已删除")
            else:
                print("❌ 删除失败")
            input("按回车键继续...")
            os.system('cls')
            return "continue", None, None, None, None
        else:
            print("❌ 已取消删除")
            os.system('cls')
            return "continue", None, None, None, None

# 全局加载器实例
save_loader = SaveLoader()

def load_summary():
    """
    向后兼容的加载函数
    """
    while True:
        result = save_loader.load_summary()
        if result[0] == "continue":  # 特殊返回值，继续循环
            continue
        return result

summary_interval = save_loader.config['SUMMARY_INTERVAL']

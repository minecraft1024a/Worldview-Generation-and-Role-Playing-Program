import os
import json
import random
from dotenv import load_dotenv
from src import world_generation, role_play, load_summary

load_dotenv()

class WGARPApp:
    """WGARP - 世界观生成与角色扮演程序主应用"""
    
    def __init__(self):
        self.daily_quote = self._get_daily_quote()
    
    def _get_daily_quote(self):
        """获取每日格言"""
        try:
            with open("src/daily_quotes.json", "r", encoding="utf-8") as file:
                quotes = json.load(file).get("quotes", [])
            return random.choice(quotes) if quotes else "今日无名言，明日再试！"
        except Exception:
            return "欢迎来到WGARP世界！"
    
    def _show_banner(self):
        """显示程序标题"""
        os.system('cls')
        print("\n██╗    ██╗ ██████╗  █████╗ ██████╗ ██████╗")
        print("██║    ██║██╔═══██╗██╔══██╗██╔══██╗██╔══██╗")
        print("██║ █╗ ██║██║   ██║███████║██████╔╝██████╔╝")
        print("██║███╗██║██║   ██║██╔══██║██╔═══╝ ██╔═══╝")
        print("╚███╔███╔╝╚██████╔╝██║  ██║██║     ██║")
        print(" ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝")
        print("\n=== WGARP - 世界观生成与角色扮演程序 ===")
        print(f"💡 每日一言：{self.daily_quote}")
    
    def _show_main_menu(self):
        """显示主菜单选项"""
        print("\n" + "="*50)
        print("📚 主菜单")
        print("="*50)
        print("1. 📖 读取存档开始游戏")
        print("2. 🌟 开始新游戏")
        print("3. 🚪 退出程序")
        print("="*50)
    
    def load_saved_game(self):
        """加载存档游戏"""
        result = load_summary.load_summary()
        if result and result[0]:  # 检查是否成功加载
            world_desc, summary_text, save_name, last_conversation, role = result
            print(f"\n✅ 存档加载成功: {save_name}")
            input("按回车键开始游戏...")
            os.system('cls')
            role_play.start_role_play(world_desc, summary_text, save_name, last_conversation, role)
            return True
        return False
    
    def create_new_game(self):
        """创建新游戏"""
        os.system('cls')
        print("🌍 新游戏创建")
        print("="*50)
        
        # 获取世界观背景
        background = input("请描述您想要的世界观背景\n(例如：魔法学院、赛博朋克、古代仙侠等，留空使用默认)\n> ").strip()
        if not background:
            background = "地理、历史、文化、魔法体系"
        
        # 生成并确认世界观
        while True:
            os.system('cls')
            print("🔮 正在生成世界观...")
            world_desc = world_generation.generate_world(background)
            
            if not world_desc:
                print("❌ 世界观生成失败，请重试")
                input("按回车键继续...")
                continue
            
            # 显示生成的世界观
            print("\n" + "="*60)
            print("🌍 生成的世界观")
            print("="*60)
            print(world_desc)
            print("="*60)
            
            # 用户确认
            while True:
                print("\n请选择操作：")
                print("1. ✅ 接受此世界观，开始游戏")
                print("2. 🔄 重新生成世界观")
                print("3. ✏️  修改背景设定")
                print("4. 🔙 返回主菜单")
                
                choice = input("\n> ").strip()
                
                if choice == "1":
                    os.system('cls')
                    print("🎮 正在进入游戏...")
                    role_play.start_role_play(world_desc, None, None, None)
                    return True
                elif choice == "2":
                    break  # 重新生成
                elif choice == "3":
                    background = input("\n请输入新的背景设定：").strip()
                    if not background:
                        background = "地理、历史、文化、魔法体系"
                    break  # 重新生成
                elif choice == "4":
                    return False
                else:
                    print("❌ 无效选择，请重新输入")
    
    def run(self):
        """运行主程序"""
        while True:
            self._show_banner()
            self._show_main_menu()
            
            choice = input("请选择操作 > ").strip()
            
            if choice == "1":
                if self.load_saved_game():
                    break  # 游戏结束，退出主循环
            elif choice == "2":
                if self.create_new_game():
                    break  # 游戏结束，退出主循环
            elif choice == "3":
                os.system('cls')
                print("👋 感谢使用 WGARP！")
                print("🌟 期待您的下次冒险！")
                break
            else:
                print("❌ 无效选择，请输入 1、2 或 3")
                input("按回车键继续...")

def main():
    """程序入口点"""
    try:
        app = WGARPApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断，再见！")
    except Exception as e:
        print(f"\n❌ 程序发生错误: {e}")
        print("请检查配置文件和依赖项")
        input("按回车键退出...")

if __name__ == "__main__":
    main()

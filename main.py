import os
from dotenv import load_dotenv
from src import world_generation, role_play

load_dotenv()

def main_menu():
    while True:
        print("\n=== 主菜单 ===")
        print("1. 开始游戏")
        print("2. 退出")
        choice = input("请选择操作（输入数字）：")
        if choice == "1":
            background = input("请输入你想要的世界观背景（如：地理、历史、文化、魔法体系等，留空为默认）：")
            if not background.strip():
                background = "地理、历史、文化、魔法体系"
            while True:
                print("\n正在生成世界观...")
                world_desc = world_generation.generate_world(background)
                print(f"\n世界观描述：\n{world_desc}\n")
                print("1. 重新生成")
                print("2. 重新输入背景并生成")
                print("3. 继续进入角色扮演")
                sub_choice = input("请选择操作（输入数字）：")
                if sub_choice == "1":
                    continue
                elif sub_choice == "2":
                    background = input("请输入新的世界观背景：")
                    if not background.strip():
                        background = "地理、历史、文化、魔法体系"
                    continue
                elif sub_choice == "3":
                    print("\n进入角色扮演模式...")
                    role_play.start_role_play(world_desc)
                else:
                    print("无效选择，请重新输入")
                    break
        elif choice == "2":
            print("再见！")
            break
        else:
            print("无效选择，请重新输入")

if __name__ == "__main__":
    main_menu()

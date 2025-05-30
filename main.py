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
            print("\n正在生成世界观...")
            world_desc = world_generation.generate_world()
            print(f"世界观描述：{world_desc}")
            print("\n进入角色扮演模式...")
            role_play.start_role_play(world_desc)
        elif choice == "2":
            print("再见！")
            break
        else:
            print("无效选择，请重新输入")

if __name__ == "__main__":
    main_menu()

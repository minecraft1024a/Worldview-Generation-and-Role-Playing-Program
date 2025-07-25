from src.llm_core import llm_core

def generate_character(world_description):

    """
    根据用户输入的提示词生成角色设定，并允许用户多次生成或自定义修改
    """
    prompt = input("请输入角色提示词（如：一个来自东方的神秘法师）：")
    while True:
        character = llm_core.generate_character(world_description, prompt)
        if character is None:
            return None
            
        print(f"\n生成的角色设定：\n{character}\n")
        choice = input("是否接受这个角色？(1接受/2重新生成/3自定义修改)：")
        if choice == "1":
            return character
        elif choice == "2":
            continue  # 重新生成
        elif choice == "3":
            prompt = input("请输入修改后的提示词：")
        else:
            print("无效输入，请重新选择")

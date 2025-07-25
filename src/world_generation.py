from src.llm_core import llm_core

def generate_world(background="地理、历史、文化、魔法体系"):
    result = llm_core.generate_world(background)
    if result is None:
        print(f"\n世界观生成失败\n")
    return result

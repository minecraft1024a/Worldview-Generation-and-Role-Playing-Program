import openai
from dotenv import load_dotenv
import os

load_dotenv()

def generate_world(background="地理、历史、文化、魔法体系"):
    client = openai.OpenAI(
        base_url=os.getenv("API_URL"),
        api_key=os.getenv("API_KEY")
    )
    
    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=[
            {"role": "system", "content": "你是一个世界构建大师，擅长生成完整的奇幻世界观设定"},
            {"role": "user", "content": f"请生成一个包含{background}的完整世界观，使用中文输出"}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

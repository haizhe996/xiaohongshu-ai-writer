from langchain_openai import ChatOpenAI
from prompt_template import prompt

def generate_xiaohongshu_copy(theme, api_key):
    # 配置 Kimi (Moonshot AI) 的参数
    model = ChatOpenAI(
        model="moonshot-v1-8k",                  # Kimi 的模型名称 
        openai_api_key=api_key,                  # 你从 sidebar 传入的 API Key
        openai_api_base="https://api.moonshot.cn/v1", # Kimi 的 Base URL 
        temperature=0.7                          # 创意程度，0.7 比较适合文案创作
    )

    # 使用 LangChain 的链式调用：提示词 -> 模型
    chain = prompt | model
    
    # 执行并返回结果
    response = chain.invoke({"theme": theme})
    return response.content
##sk-q05DZcPxdJECPuioOJL6xVGdxs0DjYfh17QSLvpSHjqyHuby
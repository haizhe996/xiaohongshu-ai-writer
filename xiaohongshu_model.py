from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from prompt_template import prompt

# 1. 生成小红书文案的主函数
def generate_xiaohongshu_copy(theme, api_key, base_url, model_name, style, length, context=""):
    model = ChatOpenAI(
        model=model_name,
        openai_api_key=api_key,
        openai_api_base=base_url,
        temperature=0.7
    )

    chain = prompt | model
    
    response = chain.invoke({
        "theme": theme,
        "context": context,
        "style": style,
        "length": length
    })
    return response.content

# 2. 【新增】根据文案生成画画提示词的函数
def generate_image_prompt(article_content, api_key, base_url, model_name):
    # 定义专门提取画面的 Prompt
    img_prompt_template = ChatPromptTemplate.from_messages([
        ("system", "你是一个AI绘画提示词专家。请阅读用户提供的小红书文案，提取出适合作为封面图的视觉元素（画面主体、场景氛围、配色风格）。请直接输出一段逗号分隔的中文提示词，不要包含'当然'、'好的'等废话，字数控制在100字以内。"),
        ("human", "文案内容：\n{content}")
    ])
    
    model = ChatOpenAI(
        model=model_name,
        openai_api_key=api_key,
        openai_api_base=base_url,
        temperature=0.7
    )
    
    chain = img_prompt_template | model
    response = chain.invoke({"content": article_content})
    return response.content

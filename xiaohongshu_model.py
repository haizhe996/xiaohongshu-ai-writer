from langchain_openai import ChatOpenAI
from prompt_template import prompt

# 接收 theme, api_key, base_url, model_name, style, length, context
def generate_xiaohongshu_copy(theme, api_key, base_url, model_name, style, length, context=""):
    
    model = ChatOpenAI(
        model=model_name,
        openai_api_key=api_key,
        openai_api_base=base_url,
        temperature=0.7
    )

    chain = prompt | model
    
    # 这里的 invoke 里面是一个字典，每一行结尾都要有逗号
    response = chain.invoke({
        "theme": theme,
        "context": context,
        "style": style,    # 👈 之前可能这里漏了逗号
        "length": length
    })
    return response.content

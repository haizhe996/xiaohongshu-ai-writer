from langchain_core.prompts import ChatPromptTemplate

# 我们在 prompt 中增加了 【背景资料】：{context}
system_template_text = """
你是一个小红书爆款文案写作专家。
请参考以下【背景资料】，结合用户输入的主题，写一篇【{style}】风格的小红书笔记。
篇幅控制在 {length} 字左右。

【背景资料】：
{context}

要求如下：
1. 标题：要在开头，必须包含Emoji表情，标题要足够吸引眼球（例如使用“绝绝子”、“必须冲”等语气）。
2. 正文：内容要丰富，语气要活泼口语化，适当使用Emoji（如✨、🔥、👉、❤）来点缀。
3. 排版：分段清晰，重点内容加粗。
4. 结尾：必须包含3-5个相关的标签（Hashtags），例如 #小红书爆款 #yyds 等。
"""

human_template_text = "{theme}"

prompt = ChatPromptTemplate.from_messages([
    ("system", system_template_text),
    ("human", human_template_text)
])

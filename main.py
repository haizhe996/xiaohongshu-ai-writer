import streamlit as st
from xiaohongshu_model import generate_xiaohongshu_copy
from rag_utils import build_vector_store 

st.set_page_config(page_title="小红书写作助手", page_icon="📝")
st.header("小红书文案AI写作助手 (RAG增强版) 🚀")

# --- 侧边栏 ---
with st.sidebar:
    st.markdown("### ⚙️ 模型配置")
    api_key = st.text_input("请输入API密钥：", type="password")
    model_provider = st.selectbox("选择模型厂商", ["通义千问", "DeepSeek", "Kimi"])
    
    if model_provider == "通义千问":
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        model_name = "qwen-plus"
    elif model_provider == "DeepSeek":
        base_url = "https://api.deepseek.com"
        model_name = "deepseek-chat"
    elif model_provider == "Kimi":
        base_url = "https://api.moonshot.cn/v1"
        model_name = "moonshot-v1-8k"

    st.markdown("---")
    st.markdown("### 🎨 写作风格")
    # 新增控件
    style = st.selectbox("文案风格", ["吸引眼球的爆款风", "干货满满的科普风", "温柔治愈的情感风", "幽默搞笑的吐槽风"])
    length = st.slider("生成字数", 100, 1000, 400)
    
    st.markdown("---")
    uploaded_file = st.file_uploader("上传参考资料", type=["pdf", "docx"])

# --- RAG 逻辑 ---
vector_store = None
if uploaded_file is not None:
    if not api_key:
        st.warning("⚠️ 请先输入 API Key")
    else:
        with st.spinner("正在读取文档..."):
            try:
                vector_store = build_vector_store(uploaded_file, api_key, base_url)
                st.success(f"✅ 文档学习完成！")
            except Exception as e:
                st.error(f"❌ 解析失败：{e}")

st.divider()

# --- 主界面 ---
theme = st.text_input("请输入文案主题：", placeholder="例如：大学生特种兵旅游")

if st.button("开始写作 ✨"):
    if not api_key:
        st.info("请先在左侧输入 API Key 🗝️")
    elif not theme:
        st.info("请输入一个主题 ✍️")
    else:
        # 1. 检索上下文
        context = "暂无背景资料"
        if vector_store:
            with st.spinner("AI正在查阅知识库..."):
                docs = vector_store.similarity_search(theme, k=2)
                context = "\n".join([doc.page_content for doc in docs])
                st.markdown(f"**📖 已参考资料片段：**\n> {context[:100]}...") 

        # 2. 生成文案
        with st.spinner("AI 正在疯狂创作中..."):
            try:
                # 传入所有参数
                result = generate_xiaohongshu_copy(
                    theme=theme,
                    api_key=api_key,
                    base_url=base_url,
                    model_name=model_name,
                    style=style,   # 新参数
                    length=length, # 新参数
                    context=context
                )
                st.success("生成成功！")
                st.markdown(result)
                
                # 下载按钮
                st.download_button(
                    label="💾 下载文案",
                    data=result,
                    file_name=f"{theme}_文案.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"生成出错了：{e}")

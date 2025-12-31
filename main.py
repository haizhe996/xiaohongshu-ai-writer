import streamlit as st
from xiaohongshu_model import generate_xiaohongshu_copy, generate_image_prompt # 👈 引入新函数
from rag_utils import build_vector_store
try:
    from wanx_model import generate_wanx_image
except ImportError:
    generate_wanx_image = None

st.set_page_config(page_title="小红书写作助手", page_icon="📝", layout="wide")

# 初始化 Session State
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
# 【新增】用来存储自动生成的画图提示词
if "auto_image_prompt" not in st.session_state:
    st.session_state.auto_image_prompt = ""

st.header("小红书文案AI写作助手 (RAG + 画图版) 🚀")

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
    style = st.selectbox("文案风格", ["吸引眼球的爆款风", "干货满满的科普风", "温柔治愈的情感风", "幽默搞笑的吐槽风"])
    length = st.slider("生成字数", 100, 1000, 400)
    
    st.markdown("---")
    st.markdown("### 📂 知识库上传")
    uploaded_file = st.file_uploader("上传参考资料", type=["pdf", "docx"])

    st.markdown("---")
    st.markdown("### 📜 历史记录")
    if st.session_state.history:
        for i, record in enumerate(reversed(st.session_state.history)):
            with st.expander(f"{record['theme']} (记录{len(st.session_state.history)-i})"):
                st.markdown(record['content'])

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
col1, col2 = st.columns([2, 1])

# --- 左侧：写文案 ---
with col1:
    st.subheader("✍️ 文案生成")
    if st.button("开始写作 ✨"):
        if not api_key:
            st.info("请先在左侧输入 API Key 🗝️")
        elif not theme:
            st.info("请输入一个主题 ✍️")
        else:
            # 1. RAG 检索
            context = "暂无背景资料"
            if vector_store:
                with st.spinner("AI正在查阅知识库..."):
                    docs = vector_store.similarity_search(theme, k=2)
                    context = "\n".join([doc.page_content for doc in docs])
                    st.markdown(f"**📖 已参考资料片段：**\n> {context[:100]}...") 

            # 2. 生成文案
            with st.spinner("AI 正在疯狂创作中..."):
                try:
                    # 生成文案
                    result = generate_xiaohongshu_copy(
                        theme=theme,
                        api_key=api_key,
                        base_url=base_url,
                        model_name=model_name,
                        style=style,   
                        length=length, 
                        context=context
                    )
                    st.session_state.last_result = result
                    st.session_state.history.append({"theme": theme, "content": result})
                    
                    st.success("文案生成成功！")
                    st.markdown(result)
                    
                    # 【核心修改】3. 立即根据文案生成画画提示词
                    with st.spinner("正在构思封面图..."):
                        img_prompt = generate_image_prompt(result, api_key, base_url, model_name)
                        # 存入 Session State，这样右边的框就能读到了
                        st.session_state.auto_image_prompt = img_prompt
                        # 强制刷新页面，让右边的框立刻更新
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"生成出错了：{e}")

    # 刷新后回显文案
    elif st.session_state.last_result:
        st.markdown(st.session_state.last_result)
        # 补一个下载按钮
        st.download_button("💾 下载文案", st.session_state.last_result, f"{theme}.md")

# --- 右侧：生成图片 ---
with col2:
    st.subheader("🎨 配图生成 (通义万相)")
    
    # 逻辑：如果有自动生成的Prompt，就用自动的；否则用默认的
    initial_value = st.session_state.auto_image_prompt if st.session_state.auto_image_prompt else f"小红书封面，插画风格，{theme}"
    
    # 这里用 key 来绑定 session_state，实现自动填入
    image_prompt = st.text_area("图片描述 (Prompt)", value=initial_value, height=150)
    
    if st.button("生成封面图 🖼️"):
        if not api_key:
            st.warning("请先输入 API Key")
        elif generate_wanx_image is None:
            st.error("❌ 未找到 wanx_model.py")
        else:
            with st.spinner("AI 画师正在挥毫泼墨..."):
                try:
                    image_url = generate_wanx_image(image_prompt, api_key)
                    if image_url and image_url.startswith("http"):
                        st.success("封面图生成成功！")
                        st.image(image_url, caption="由通义万相生成", use_column_width=True)
                        st.markdown(f"[📥 点击下载大图]({image_url})")
                    else:
                        st.error(f"生成失败：{image_url}")
                except Exception as e:
                    st.error(f"调用报错：{e}")

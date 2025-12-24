import streamlit as st
from xiaohongshu_model import generate_xiaohongshu_copy

# 设置页面标题
st.header("小红书文案AI写作助手~ 📝")

# 侧边栏布局：输入API Key
with st.sidebar:
    api_key = st.text_input("请输入API密钥：", type="password")
    st.markdown("[DeepSeek获取Key](https://platform.deepseek.com/) | [Kimi获取Key](https://platform.moonshot.cn/)")

# 主界面：输入主题
st.divider()
theme = st.text_input("请输入文案主题：")

# 按钮逻辑
if st.button("开始写作"):
    if not api_key:
        st.info("请先在左侧输入 API Key 🗝️")
    elif not theme:
        st.info("请输入一个主题，比如：'大模型时代' ✍️")
    else:
        # 显示加载转圈圈
        with st.spinner("AI 正在疯狂创作中..."):
            try:
                # 调用我们在 xiaohongshu_model.py 中写的函数
                result = generate_xiaohongshu_copy(theme, api_key)
                st.success("生成成功！")
                st.markdown(result) # 展示生成结果
            except Exception as e:
                st.error(f"出错了：{e}")
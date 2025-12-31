import os
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# 引入 LangChain 的官方阿里云工具
from langchain_community.embeddings import DashScopeEmbeddings 
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

def build_vector_store(uploaded_file, api_key, base_url):
    print(f"Debug: 开始处理文件: {uploaded_file.name}") 
    
    # 1. 保存临时文件
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    temp_file_path = f"temp{file_extension}" 
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    # 2. 根据类型选择加载器
    try:
        if file_extension == ".pdf":
            loader = PyPDFLoader(temp_file_path)
        elif file_extension == ".docx":
            loader = Docx2txtLoader(temp_file_path)
        else:
            raise ValueError(f"不支持的文件类型: {file_extension}")
        docs = loader.load()
    except Exception as e:
        raise ValueError(f"文件加载失败: {e}")

    # 3. 切分文本
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n", "。", "！", "？", "，", "、", ""]
    )
    raw_texts = text_splitter.split_documents(docs)

    # 4. 清洗数据 (保留之前的清洗逻辑，防止脏数据)
    clean_texts = []
    for t in raw_texts:
        raw_content = str(t.page_content) if t.page_content else ""
        # 只保留中英文和标点
        safe_content = re.sub(r'[^\w\u4e00-\u9fa5,.!?;:"\'()（）《》\n-]', '', raw_content)
        safe_content = safe_content.strip()
        
        if len(safe_content) > 5:
            t.page_content = safe_content
            clean_texts.append(t)

    if not clean_texts:
        raise ValueError("文档内容为空！")

    print(f"Debug: 准备向量化 {len(clean_texts)} 段文本...")

    # 5. 向量化 (Embedding) - 【核心修改区】
    try:
        if "aliyuncs" in base_url:
            print("Debug: 检测到阿里云，切换使用 DashScope 原生模式...")
            # 使用阿里云官方 SDK，彻底避开兼容性 bug
            embeddings_model = DashScopeEmbeddings(
                model="text-embedding-v2",
                dashscope_api_key=api_key
            )
        else:
            # 其他模型继续使用 OpenAI 兼容模式
            embeddings_model = OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_key=api_key,
                openai_api_base=base_url,
                tiktoken_enabled=True,
                tiktoken_model_name="cl100k_base",
                check_embedding_ctx_length=False
            )
        
        # 建立索引
        db = FAISS.from_documents(clean_texts, embeddings_model)
        print("Debug: 向量库构建成功！")
        return db

    except Exception as e:
        # 如果是没安装库的错误，给出提示
        if "No module named 'dashscope'" in str(e):
            raise ValueError("请先在终端运行: pip install dashscope")
        
        print(f"Debug: 向量化报错: {e}")
        raise ValueError(f"向量化失败: {e}")
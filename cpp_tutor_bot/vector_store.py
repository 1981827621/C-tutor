"""
向量数据库和RAG检索模块
"""

import os
from typing import List, Optional
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from cpp_tutor_bot.config import get_settings


class VectorStoreManager:
    """向量数据库管理器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.embeddings = self._create_embeddings()
        self.vector_store: Optional[Chroma] = None
        self._initialize_vector_store()
    
    def _create_embeddings(self):
        """创建嵌入模型"""
        # 使用sentence-transformers（预编译，无需编译）
        from langchain_community.embeddings import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(
            model_name=self.settings.embedding_model
        )
    
    def _initialize_vector_store(self):
        """初始化向量数据库"""
        persist_dir = self.settings.chroma_persist_dir
        os.makedirs(persist_dir, exist_ok=True)
        
        self.vector_store = Chroma(
            persist_directory=persist_dir,
            embedding_function=self.embeddings,
            collection_name="cpp_tutor_knowledge"
        )
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """添加文档到向量数据库"""
        if not self.vector_store:
            raise RuntimeError("向量数据库未初始化")
        
        ids = self.vector_store.add_documents(documents)
        return ids
    
    def add_texts(self, texts: List[str], metadatas: List[dict] = None) -> List[str]:
        """添加文本到向量数据库"""
        if not self.vector_store:
            raise RuntimeError("向量数据库未初始化")
        
        ids = self.vector_store.add_texts(texts=texts, metadatas=metadatas)
        return ids
    
    def search(self, query: str, k: int = None) -> List[Document]:
        """检索相关文档"""
        if not self.vector_store:
            raise RuntimeError("向量数据库未初始化")
        
        top_k = k or self.settings.top_k_retrieval
        results = self.vector_store.similarity_search(query, k=top_k)
        return results
    
    def search_with_score(self, query: str, k: int = None) -> List[tuple]:
        """检索相关文档并返回相似度分数"""
        if not self.vector_store:
            raise RuntimeError("向量数据库未初始化")
        
        top_k = k or self.settings.top_k_retrieval
        results = self.vector_store.similarity_search_with_score(query, k=top_k)
        return results
    
    def delete_collection(self):
        """删除集合"""
        if self.vector_store:
            self.vector_store.delete_collection()
            self._initialize_vector_store()
    
    def get_document_count(self) -> int:
        """获取文档数量"""
        if not self.vector_store:
            return 0
        return self.vector_store._collection.count()


class RAGRetriever:
    """RAG检索器"""
    
    def __init__(self, vector_store_manager: VectorStoreManager):
        self.vector_store = vector_store_manager
    
    def retrieve_knowledge(self, query: str, category: str = None) -> List[Document]:
        """检索知识"""
        # 可以添加分类过滤逻辑
        docs = self.vector_store.search(query)
        
        if category:
            docs = [doc for doc in docs if doc.metadata.get("category") == category]
        
        return docs
    
    def retrieve_with_context(self, query: str) -> str:
        """检索并格式化上下文"""
        docs = self.vector_store.search(query)
        
        if not docs:
            return "未找到相关参考资料。"
        
        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "未知来源")
            context_parts.append(f"[资料{i}] (来源: {source})\n{doc.page_content}")
        
        return "\n\n".join(context_parts)

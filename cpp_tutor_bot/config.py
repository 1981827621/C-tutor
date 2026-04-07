"""
应用配置模块
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # DeepSeek API配置
    deepseek_api_key: str = ""
    deepseek_api_base: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"
    
    # 向量数据库配置
    chroma_persist_dir: str = "./chroma_db"
    
    # 应用配置
    max_memory_turns: int = 10
    top_k_retrieval: int = 3
    
    # 嵌入模型配置（使用本地模型）
    embedding_model: str = "shibing624/text2vec-base-chinese"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()

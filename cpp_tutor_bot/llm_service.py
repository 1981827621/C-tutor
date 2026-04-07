"""
LLM调用模块 - DeepSeek API
"""

from typing import List, Optional, AsyncGenerator
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage

from cpp_tutor_bot.config import get_settings


class LLMService:
    """LLM服务 - 封装DeepSeek API调用"""
    
    def __init__(self):
        self.settings = get_settings()
        self.llm = self._create_llm()
    
    def _create_llm(self) -> ChatOpenAI:
        """创建LLM实例"""
        return ChatOpenAI(
            model=self.settings.deepseek_model,
            openai_api_key=self.settings.deepseek_api_key,
            openai_api_base=self.settings.deepseek_api_base,
            temperature=0.7,
            max_tokens=2000,
            streaming=True  # 启用流式输出
        )
    
    def chat(self, messages: List[BaseMessage]) -> str:
        """
        发送聊天请求并获取回复
        
        Args:
            messages: 消息列表
        
        Returns:
            AI回复内容
        """
        response = self.llm.invoke(messages)
        return response.content
    
    async def chat_stream(self, messages: List[BaseMessage]) -> AsyncGenerator[str, None]:
        """
        发送流式聊天请求
        
        Args:
            messages: 消息列表
        
        Yields:
            流式返回的内容
        """
        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content
    
    def chat_with_retry(self, messages: List[BaseMessage], max_retries: int = 3) -> str:
        """带重试的聊天"""
        import time
        
        for attempt in range(max_retries):
            try:
                return self.chat(messages)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"LLM调用失败，已重试{max_retries}次: {str(e)}")
                time.sleep(2 ** attempt)  # 指数退避

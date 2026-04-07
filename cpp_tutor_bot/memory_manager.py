"""
对话记忆管理模块
"""

from typing import List, Dict, Optional
import time
import uuid
import logging

from cpp_tutor_bot.config import get_settings

logger = logging.getLogger(__name__)


class ConversationMemory:
    """单个会话的记忆管理"""
    
    def __init__(self, session_id: str, max_turns: int = 10):
        self.session_id = session_id
        self.max_turns = max_turns
        self.messages: List[Dict[str, str]] = []
        self.created_at = time.time()
        self.last_updated = time.time()
    
    def add_message(self, role: str, content: str):
        """添加消息到记忆"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
        self.last_updated = time.time()
        
        # 如果超出最大轮数，移除最早的消息
        while len(self.messages) > self.max_turns * 2:  # 一轮包含用户和AI各一条
            self.messages.pop(0)
    
    def get_history(self, max_turns: Optional[int] = None) -> List[Dict[str, str]]:
        """获取对话历史"""
        limit = max_turns or self.max_turns
        return self.messages[-limit * 2:]  # 返回最近的历史
    
    def clear(self):
        """清空记忆"""
        self.messages = []
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "message_count": len(self.messages),
            "created_at": self.created_at,
            "last_updated": self.last_updated
        }


class MemoryManager:
    """全局记忆管理器 - 管理所有会话"""

    def __init__(self):
        self.settings = get_settings()
        self.sessions: Dict[str, ConversationMemory] = {}
        self._cleanup_task = None

    def get_or_create_session(self, session_id: Optional[str] = None) -> ConversationMemory:
        """获取或创建会话"""
        if not session_id:
            session_id = str(uuid.uuid4())

        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationMemory(
                session_id=session_id,
                max_turns=self.settings.max_memory_turns
            )
            logger.info(f"创建新会话: {session_id}")

        return self.sessions[session_id]
    
    def get_session(self, session_id: str) -> Optional[ConversationMemory]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    def add_message(self, session_id: str, role: str, content: str):
        """添加消息"""
        memory = self.get_or_create_session(session_id)
        memory.add_message(role, content)
    
    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """获取对话历史"""
        memory = self.get_or_create_session(session_id)
        return memory.get_history()
    
    def clear_session(self, session_id: str):
        """清空会话"""
        if session_id in self.sessions:
            self.sessions[session_id].clear()
    
    def delete_session(self, session_id: str):
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24):
        """清理过期会话"""
        current_time = time.time()
        expired_sessions = []

        for session_id, memory in self.sessions.items():
            if current_time - memory.last_updated > max_age_hours * 3600:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            logger.info(f"清理了 {len(expired_sessions)} 个过期会话")
    
    async def start_cleanup_task(self):
        """启动定期清理任务"""
        import asyncio
        
        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(3600)  # 每小时清理一次
                    self.cleanup_expired_sessions()
                except Exception as e:
                    logger.error(f"清理过期会话时出错: {e}")
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())
        logger.info("已启动定期清理任务")

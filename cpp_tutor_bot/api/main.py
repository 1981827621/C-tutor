"""
FastAPI主应用
"""

import os
import uuid
import glob
import json
import logging
from typing import Optional, List, AsyncGenerator
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 先导入UserIntent避免循环引用
from cpp_tutor_bot.intent_classifier import UserIntent
from cpp_tutor_bot.config import get_settings
from cpp_tutor_bot.document_parser import DocumentProcessor
from cpp_tutor_bot.vector_store import VectorStoreManager, RAGRetriever
from cpp_tutor_bot.intent_classifier import IntentClassifier
from cpp_tutor_bot.prompt_builder import PromptBuilder
from cpp_tutor_bot.memory_manager import MemoryManager
from cpp_tutor_bot.llm_service import LLMService


# 创建FastAPI应用
app = FastAPI(title="C++竞赛助教Bot", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
settings = get_settings()
document_processor = DocumentProcessor()
vector_store_manager = VectorStoreManager()
rag_retriever = RAGRetriever(vector_store_manager)
intent_classifier = IntentClassifier()
prompt_builder = PromptBuilder()
memory_manager = MemoryManager()
llm_service = LLMService()

# 知识库目录（开发者预置）
KNOWLEDGE_BASE_DIR = "./knowledge_base"


# 请求模型
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000, description="用户消息内容")
    session_id: Optional[str] = Field(None, max_length=100, description="会话ID")


class ChatResponse(BaseModel):
    response: str
    session_id: str
    intent: str


class SessionInfo(BaseModel):
    session_id: str
    message_count: int


class KnowledgeStats(BaseModel):
    total_documents: int
    loaded_files: List[str]


def load_knowledge_base():
    """加载知识库目录下的所有文档"""
    knowledge_dir = KNOWLEDGE_BASE_DIR

    if not os.path.exists(knowledge_dir):
        os.makedirs(knowledge_dir)
        logger.info(f"[知识库] 创建知识库目录: {knowledge_dir}")
        logger.info(f"[知识库] 请将教学资料放入 {knowledge_dir} 目录后重启服务")
        return

    # 获取支持的文件
    supported_exts = document_processor.get_supported_extensions()
    files_to_load = []

    for ext in supported_exts:
        pattern = os.path.join(knowledge_dir, f"**/*{ext}")
        files_to_load.extend(glob.glob(pattern, recursive=True))

    if not files_to_load:
        logger.info(f"[知识库] 知识库目录为空: {knowledge_dir}")
        logger.info(f"[知识库] 支持的格式: {', '.join(supported_exts)}")
        return

    logger.info(f"\n{'='*60}")
    logger.info(f"[知识库] 开始加载知识库...")
    logger.info(f"[知识库] 目录: {os.path.abspath(knowledge_dir)}")
    logger.info(f"[知识库] 发现 {len(files_to_load)} 个文件")

    total_docs = 0
    for file_path in files_to_load:
        try:
            filename = os.path.basename(file_path)
            logger.info(f"[知识库] 正在处理: {filename}")

            # 处理文件
            documents = document_processor.process_file(file_path, source_name=filename)

            # 添加到向量数据库
            if documents:
                vector_store_manager.add_documents(documents)
                total_docs += len(documents)
                logger.info(f"[知识库] ✓ {filename} -> {len(documents)} 个文档块")
            else:
                logger.warning(f"[知识库] ✗ {filename} -> 无内容")

        except Exception as e:
            logger.error(f"[知识库] ✗ {os.path.basename(file_path)} -> 错误: {str(e)}")

    logger.info(f"\n[知识库] 加载完成！共处理 {total_docs} 个文档块")
    logger.info(f"{'='*60}\n")


# 启动时加载知识库
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("\n" + "="*60)
    logger.info("  C++竞赛助教Bot 启动中...")
    logger.info("="*60)
    load_knowledge_base()
    
    # 启动定期清理过期会话任务
    await memory_manager.start_cleanup_task()


# API路由
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """聊天接口（非流式）"""
    try:
        # 获取或创建会话
        session = memory_manager.get_or_create_session(request.session_id)
        session_id = session.session_id

        # 分类用户意图
        intent, extracted_info = intent_classifier.classify(request.message)

        # 检索相关知识（GENERAL_CHAT跳过检索）
        retrieved_context = None
        if intent != UserIntent.GENERAL_CHAT:
            retrieved_context = rag_retriever.retrieve_with_context(request.message)

        # 获取对话历史
        history = memory_manager.get_history(session_id)

        # 构建消息
        messages = prompt_builder.build_messages(
            user_input=request.message,
            intent=intent,
            retrieved_context=retrieved_context,
            conversation_history=history
        )

        # 调用LLM
        response = llm_service.chat_with_retry(messages)

        # 保存到记忆
        memory_manager.add_message(session_id, "human", request.message)
        memory_manager.add_message(session_id, "ai", response)

        logger.info(f"聊天完成 - 会话: {session_id}, 意图: {intent.value}")

        return ChatResponse(
            response=response,
            session_id=session_id,
            intent=intent.value
        )

    except Exception as e:
        error_detail = f"处理请求失败: {str(e)}"
        logger.error(f"{error_detail}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_detail)


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """聊天接口（流式输出）"""
    try:
        # 获取或创建会话
        session = memory_manager.get_or_create_session(request.session_id)
        session_id = session.session_id

        # 分类用户意图
        intent, extracted_info = intent_classifier.classify(request.message)

        # 检索相关知识（GENERAL_CHAT跳过检索）
        retrieved_context = None
        if intent != UserIntent.GENERAL_CHAT:
            retrieved_context = rag_retriever.retrieve_with_context(request.message)

        # 获取对话历史
        history = memory_manager.get_history(session_id)

        # 构建消息
        messages = prompt_builder.build_messages(
            user_input=request.message,
            intent=intent,
            retrieved_context=retrieved_context,
            conversation_history=history
        )

        # 流式生成
        async def generate_stream():
            full_response = ""

            # 发送session_id和intent
            meta_data = {
                "session_id": session_id,
                "intent": intent.value
            }
            yield f"data: {json.dumps({'type': 'meta', 'data': meta_data})}\n\n"

            try:
                # 使用封装的chat_stream方法流式获取内容
                async for chunk_content in llm_service.chat_stream(messages):
                    full_response += chunk_content
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk_content})}\n\n"

                # 保存到记忆
                memory_manager.add_message(session_id, "human", request.message)
                memory_manager.add_message(session_id, "ai", full_response)

                logger.info(f"流式聊天完成 - 会话: {session_id}, 意图: {intent.value}")

                # 发送完成信号
                yield f"data: {json.dumps({'type': 'done', 'content': full_response})}\n\n"

            except Exception as e:
                logger.error(f"流式输出错误: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    except Exception as e:
        import traceback
        error_detail = f"处理请求失败: {str(e)}"
        logger.error(f"{error_detail}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/api/knowledge/stats", response_model=KnowledgeStats)
async def get_knowledge_stats():
    """获取知识库统计信息"""
    # 获取已加载的文件列表
    docs = vector_store_manager.vector_store.get() if vector_store_manager.vector_store else None
    
    loaded_files = []
    if docs and 'metadatas' in docs:
        sources = set()
        for metadata in docs['metadatas']:
            if 'source' in metadata:
                sources.add(metadata['source'])
        loaded_files = list(sources)
    
    return KnowledgeStats(
        total_documents=vector_store_manager.get_document_count(),
        loaded_files=loaded_files
    )


@app.get("/api/session/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str):
    """获取会话信息"""
    session = memory_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    return SessionInfo(
        session_id=session_id,
        message_count=len(session.messages)
    )


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    memory_manager.delete_session(session_id)
    return {"success": True, "message": "会话已删除"}


@app.post("/api/session/{session_id}/clear")
async def clear_session(session_id: str):
    """清空会话历史"""
    memory_manager.clear_session(session_id)
    return {"success": True, "message": "会话历史已清空"}


@app.get("/api/stats")
async def get_stats():
    """获取系统统计信息"""
    return {
        "document_count": vector_store_manager.get_document_count(),
        "session_count": len(memory_manager.sessions),
        "supported_formats": document_processor.get_supported_extensions(),
        "knowledge_base_dir": os.path.abspath(KNOWLEDGE_BASE_DIR)
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}

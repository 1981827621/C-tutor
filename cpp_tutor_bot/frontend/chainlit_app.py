"""
Chainlit前端聊天界面
支持流式输出、代码文件上传、Markdown渲染、语法高亮
"""

import os
import json
import requests
import chainlit as cl
from chainlit.element import ElementBased
from typing import Optional


# 配置
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def get_session_id() -> str:
    """获取当前会话ID"""
    return cl.user_session.get("session_id")


def set_session_id(session_id: str):
    """设置会话ID"""
    cl.user_session.set("session_id", session_id)


def process_uploaded_file(file_path: str) -> Optional[str]:
    """处理上传的代码文件"""
    try:
        print(f"正在处理文件: {file_path}")
        encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin-1']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    print(f"成功使用 {encoding} 编码读取文件")
                    return content
            except (UnicodeDecodeError, UnicodeError):
                continue
        print("所有编码尝试失败")
        return None
    except Exception as e:
        print(f"文件读取失败: {e}")
        return None


@cl.on_chat_start
async def start():
    """聊天开始时执行"""
    set_session_id(None)

    welcome_content = """# 🌟 同学你好呀！

我是你的 **C++小老师**，是你的编程学习好伙伴！💪

---

## 🎯 我可以帮你做什么？

### 📝 解答问题
不知道怎么写的都可以问我哦～

### 🐛 调试代码
代码有bug？贴出来我帮你看看！

### 📚 学习知识点
循环、数组、函数...不懂就问！

### 🎯 竞赛技巧
教你拿比赛高分的秘诀！

### 📁 上传代码
点击输入框左边的 📎 上传 .cpp 文件，我会帮你分析！

---

## 💡 开始学习吧！

直接在输入框中输入你的问题，按回车发送即可～"""

    await cl.Message(
        content=welcome_content,
        author="🎓 C++小老师",
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """处理用户消息"""
    user_input = message.content
    uploaded_filename = None
    uploaded_content = None

    # 检查是否有上传的文件
    if message.elements and len(message.elements) > 0:
        for element in message.elements:
            print(f"上传的文件元素: {element}")
            print(f"文件类型: {type(element)}")
            
            # 尝试获取文件路径
            file_path = None
            if hasattr(element, 'path'):
                file_path = element.path
            elif hasattr(element, 'url'):
                file_path = element.url
            elif hasattr(element, 'content'):
                # 直接获取内容
                uploaded_content = element.content
                uploaded_filename = element.name if hasattr(element, 'name') else 'unknown.cpp'
            
            print(f"文件路径: {file_path}")
            print(f"文件名: {uploaded_filename}")
            
            if file_path:
                uploaded_content = process_uploaded_file(file_path)
                uploaded_filename = element.name if hasattr(element, 'name') else 'unknown.cpp'

            if uploaded_content is None:
                await cl.Message(
                    content="😵 文件编码不支持，请另存为UTF-8格式哦～",
                    author="🎓 C++小老师",
                ).send()
                return

            # 将代码添加到用户消息中
            user_input = f"请帮我分析下面的C++代码：\n\n上传的代码文件: {uploaded_filename}\n\n```cpp\n{uploaded_content}\n```"
            break

    print(f"用户输入: {user_input[:100]}...")

    # 显示思考中的消息
    thinking_msg = cl.Message(
        content="🤔 *小老师正在认真思考中...*",
        author="🎓 C++小老师",
    )
    await thinking_msg.send()

    # 流式获取AI回复并实时更新显示
    session_id = get_session_id()
    full_response = ""
    intent = "general_chat"

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chat/stream",
            json={
                "message": user_input,
                "session_id": session_id
            },
            stream=True,
            timeout=120
        )
        response.raise_for_status()

        # 解析SSE流并实时更新消息
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]
                    try:
                        data = json.loads(data_str)

                        if data['type'] == 'meta':
                            new_session_id = data['data'].get('session_id', session_id)
                            intent = data['data'].get('intent', 'general_chat')
                            set_session_id(new_session_id)

                        elif data['type'] == 'content':
                            chunk = data['content']
                            full_response += chunk
                            # 实时更新消息内容（流式输出）
                            thinking_msg.content = full_response
                            await thinking_msg.update()

                        elif data['type'] == 'done':
                            break

                        elif data['type'] == 'error':
                            thinking_msg.content = f"😵 出错了: {data['error']}"
                            await thinking_msg.update()
                            return

                    except json.JSONDecodeError:
                        continue

    except requests.exceptions.ConnectionError:
        thinking_msg.content = "😵 哎呀，连接不到老师的大脑哦～请确认后端服务已启动（端口8000）"
        await thinking_msg.update()
    except requests.exceptions.Timeout:
        thinking_msg.content = "😵 老师思考太久了，请稍后再试"
        await thinking_msg.update()
    except Exception as e:
        thinking_msg.content = f"😵 出错啦: {str(e)}"
        await thinking_msg.update()


@cl.on_chat_end
async def on_chat_end():
    """聊天结束时清理"""
    session_id = get_session_id()
    if session_id:
        try:
            requests.delete(
                f"{API_BASE_URL}/api/session/{session_id}",
                timeout=5
            )
        except Exception:
            pass


@cl.on_chat_resume
async def on_chat_resume(thread):
    """恢复聊天时加载历史"""
    pass

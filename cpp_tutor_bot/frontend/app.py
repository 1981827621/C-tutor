"""
Streamlit前端聊天界面 - 可爱版（面向中小学生）
支持流式输出、代码文件上传、自动清空
"""

import os
import requests
import streamlit as st
import json


# 配置
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# 快捷问题配置（可通过环境变量或配置文件修改）
QUICK_QUESTIONS = [
    ("📝", "C++零基础入门"),
    ("🔢", "NOI竞赛大纲"),
    ("🔄", "for循环怎么用呀？"),
    ("📚", "什么是变量呢？"),
    ("🐛", "代码报错了怎么办？"),
    ("🎮", "怎么做一个小游戏？")
]


def init_session_state():
    """初始化会话状态"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "is_generating" not in st.session_state:
        st.session_state.is_generating = False
    # 上传的代码相关状态
    if "uploaded_content" not in st.session_state:
        st.session_state.uploaded_content = None
    if "uploaded_filename" not in st.session_state:
        st.session_state.uploaded_filename = None
    if "show_upload_preview" not in st.session_state:
        st.session_state.show_upload_preview = False


def send_message_stream(message: str, callback):
    """发送消息到后端流式接口"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chat/stream",
            json={
                "message": message,
                "session_id": st.session_state.session_id
            },
            stream=True,
            timeout=120
        )
        response.raise_for_status()
        
        full_response = ""
        
        # 解析SSE流
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]
                    try:
                        data = json.loads(data_str)
                        
                        if data['type'] == 'meta':
                            st.session_state.session_id = data['data'].get('session_id')
                        
                        elif data['type'] == 'content':
                            chunk = data['content']
                            full_response += chunk
                            callback(full_response, False)
                        
                        elif data['type'] == 'done':
                            callback(full_response, True)
                            return full_response
                        
                        elif data['type'] == 'error':
                            return {"error": data['error']}
                    
                    except json.JSONDecodeError:
                        continue
        
        return full_response
    
    except requests.exceptions.ConnectionError:
        return {"error": "哎呀，连接不到老师的大脑哦～请确认后端服务已启动（端口8000）"}
    except requests.exceptions.Timeout:
        return {"error": "老师思考太久了，请稍后再试"}
    except Exception as e:
        return {"error": f"出错啦: {str(e)}"}


def render_styles():
    """渲染CSS样式"""
    st.markdown("""
    <style>
    /* 全局样式 */
    .main .block-container {
        background-color: #FFF5E6;
        padding-bottom: 280px !important;
    }
    
    /* 标题样式 */
    .cute-title {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 20px;
        color: white;
        margin-bottom: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .cute-subtitle {
        text-align: center;
        color: #888;
        font-size: 14px;
        margin-bottom: 20px;
    }
    
    /* 欢迎卡片 */
    .welcome-card {
        text-align: center;
        padding: 30px;
        background: white;
        border-radius: 20px;
        margin: 20px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* 固定底部输入区域 */
    .bottom-input-area {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background: white !important;
        padding: 15px 20px !important;
        box-shadow: 0 -4px 15px rgba(0,0,0,0.15) !important;
        z-index: 9999 !important;
        border-top: 3px solid #667eea !important;
    }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """渲染头部"""
    st.markdown("""
    <div class="cute-title">
        <h1>🎓 C++小老师 🌟</h1>
        <p style="font-size: 16px; margin: 0;">你的编程学习好伙伴！</p>
    </div>
    <div class="cute-subtitle">
        💡 有问题尽管问，老师会一步步教你哦～
    </div>
    """, unsafe_allow_html=True)


def render_welcome():
    """渲染欢迎消息"""
    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div class="welcome-card">
            <h2 style="color: #667eea;">👋 同学你好呀！</h2>
            <p style="color: #666; font-size: 16px;">
                我是你的C++小老师，可以帮你：<br><br>
                📝 <b>解答问题</b> - 不知道怎么写的都可以问我哦～<br>
                🐛 <b>调试代码</b> - 代码有bug？贴出来我帮你看看！<br>
                📚 <b>学习知识点</b> - 循环、数组、函数...不懂就问！<br>
                🎯 <b>竞赛技巧</b> - 教你拿比赛高分的秘诀！<br>
                📁 <b>上传代码</b> - 可以上传.cpp文件让我帮你分析！<br><br>
                <span style="color: #999; font-size: 14px;">
                    💡 试试下面的快捷问题开始学习吧～
                </span>
            </p>
        </div>
        """, unsafe_allow_html=True)


def render_quick_questions():
    """渲染快捷问题"""
    st.markdown("### 🎯 快速提问")

    col1, col2, col3 = st.columns(3)

    clicked = None

    for i, (emoji, question) in enumerate(QUICK_QUESTIONS):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.button(f"{emoji} {question}", key=f"quick_q_{i}"):
                clicked = question

    return clicked


def process_message(user_input, uploaded_content=None, uploaded_filename=None):
    """处理用户消息并获取AI回复"""
    # 构造完整的消息
    full_message = user_input
    if uploaded_content and uploaded_filename:
        full_message = f"{user_input}\n\n📁 **上传的代码文件**: {uploaded_filename}\n\n```cpp\n{uploaded_content}\n```"
    
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(f"👦 **同学**: {full_message}")
    
    st.session_state.messages.append({"role": "user", "content": full_message})
    
    # 显示AI消息（流式更新）
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        def update_display(current_response, is_done):
            if not is_done:
                message_placeholder.markdown(f"🎓 **C++小老师** *(正在输入...)*:\n\n{current_response}")
            else:
                message_placeholder.markdown(f"🎓 **C++小老师**:\n\n{current_response}")
        
        # 发送流式请求
        result = send_message_stream(full_message, update_display)
        
        # 处理结果
        if isinstance(result, dict) and "error" in result:
            error_msg = f"😵 {result['error']}"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            return False
        else:
            final_response = result if result else full_response
            message_placeholder.markdown(f"🎓 **C++小老师**:\n\n{final_response}")
            st.session_state.messages.append({"role": "assistant", "content": final_response})
            return True


def render_sidebar():
    """渲染侧边栏"""
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; color: white; margin-bottom: 20px;">
        <h2 style="margin: 0;">🎮 工具箱</h2>
        <p style="margin: 5px 0 0 0; font-size: 12px;">管理你的学习</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 新建会话
    if st.sidebar.button("🆕 开始新对话", use_container_width=True):
        st.session_state.session_id = None
        st.session_state.messages = []
        st.session_state.is_generating = False
        st.session_state.uploaded_content = None
        st.session_state.uploaded_filename = None
        st.session_state.show_upload_preview = False
        st.rerun()
    
    # 清空历史
    if st.sidebar.button("🗑️ 清空聊天记录", use_container_width=True):
        if st.session_state.session_id:
            try:
                requests.post(
                    f"{API_BASE_URL}/api/session/{st.session_state.session_id}/clear",
                    timeout=10
                )
            except Exception as e:
                st.warning(f"清空会话失败: {e}")
        st.session_state.messages = []
        st.session_state.uploaded_content = None
        st.session_state.uploaded_filename = None
        st.session_state.show_upload_preview = False
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # 帮助
    with st.sidebar.expander("❓ 怎么使用呀？"):
        st.markdown("""
        **使用超简单！** 🎉
        
        1. 📁 点击"上传代码"按钮（可选）
        2. 👀 查看代码预览，点 ❌ 可以清除
        3. 💬 在底部输入框写问题
        4. 📤 按回车或点击发送
        5. 🎓 老师就会回答你啦！
        """)


def clear_uploaded_code():
    """清除已上传的代码"""
    st.session_state.uploaded_content = None
    st.session_state.uploaded_filename = None
    st.session_state.show_upload_preview = False


def render_bottom_input_area():
    """渲染固定在底部的输入区域（包含文件上传和输入框）"""
    st.markdown('<div class="bottom-input-area">', unsafe_allow_html=True)
    
    # 如果还没有上传代码，显示上传按钮
    if not st.session_state.uploaded_filename:
        uploaded_file = st.file_uploader(
            "📁 上传代码文件（可选）",
            type=["cpp", "cxx", "cc", "c", "h", "hpp"],
            key="main_uploader",
            disabled=st.session_state.is_generating,
            label_visibility="visible"
        )
        
        # 处理文件上传
        if uploaded_file is not None:
            try:
                # 尝试多种编码
                content = None
                for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                    try:
                        content = uploaded_file.getvalue().decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue

                if content is None:
                    st.error("😵 文件编码不支持，请另存为UTF-8格式")
                else:
                    # 保存上传的内容
                    st.session_state.uploaded_content = content
                    st.session_state.uploaded_filename = uploaded_file.name
                    st.session_state.show_upload_preview = True
                    st.rerun()
            except Exception as e:
                st.error(f"😵 文件读取失败: {str(e)}")
    else:
        # 已上传代码，显示预览和清除按钮
        st.success(f"✅ 已上传: {st.session_state.uploaded_filename}")
        
        # 显示代码预览和清除按钮
        col_preview, col_clear = st.columns([4, 1])
        
        with col_preview:
            with st.expander("📄 代码预览", expanded=True):
                preview = st.session_state.uploaded_content
                if len(preview) > 400:
                    preview = preview[:400] + "\n..."
                st.code(preview, language="cpp")
        
        with col_clear:
            if st.button("❌ 清除", use_container_width=True, type="secondary", disabled=st.session_state.is_generating):
                clear_uploaded_code()
                st.rerun()
    
    # 输入框
    if prompt := st.chat_input("输入你的问题，按回车发送...", disabled=st.session_state.is_generating):
        # 用户输入了内容，处理消息
        st.session_state.is_generating = True
        
        success = process_message(
            prompt,
            st.session_state.uploaded_content,
            st.session_state.uploaded_filename
        )
        
        # 发送后自动清除代码
        clear_uploaded_code()
        st.session_state.is_generating = False
        
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


def main():
    """主函数"""
    st.set_page_config(
        page_title="C++小老师 🎓",
        page_icon="🌟",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 初始化
    init_session_state()
    
    # 渲染样式
    render_styles()
    
    # 渲染头部
    render_header()
    
    # 渲染侧边栏
    render_sidebar()
    
    # 渲染欢迎消息
    render_welcome()
    
    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(f"👦 **同学**: {message['content']}")
            else:
                st.markdown(f"🎓 **C++小老师**: {message['content']}")
    
    # 快捷问题（仅在没有消息时显示）
    if len(st.session_state.messages) == 0:
        quick_question = render_quick_questions()
        if quick_question:
            process_message(quick_question)
            st.rerun()
    
    # 渲染固定在底部的输入区域
    render_bottom_input_area()


if __name__ == "__main__":
    main()

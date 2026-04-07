# C++小老师 - Chainlit前端

## 🎉 全新升级

基于 Chainlit 打造的现代化AI对话界面，相比 Streamlit 版本有以下优势：

### ✨ 核心特性

| 特性 | 说明 |
|------|------|
| **🎨 美观UI** | 自带圆角阴影卡片、渐变背景、毛玻璃效果 |
| **📝 Markdown渲染** | 完美支持代码块、表格、列表、加粗、斜体 |
| **💻 代码高亮** | C++代码语法高亮，类似VS Code体验 |
| **🎬 流畅动画** | 消息滑入、按钮悬停、打字指示器动画 |
| **📁 文件上传** | 拖拽上传.cpp文件，自动识别编码 |
| **💬 快捷问题** | 内置6个快捷问题，一键开始学习 |
| **📱 响应式** | 完美适配手机、平板、桌面 |
| **🌙 暗色主题** | 支持一键切换明暗主题 |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 激活虚拟环境
.venv\Scripts\activate.bat

# 安装Chainlit
pip install chainlit>=1.0.0
```

### 2. 启动后端

```bash
# 在另一个终端运行
start_backend.bat
```

### 3. 启动前端

```bash
# 方式一：使用启动脚本
start_chainlit.bat

# 方式二：手动启动
cd cpp_tutor_bot\frontend
chainlit run chainlit_app.py --host 0.0.0.0 --port 8080
```

### 4. 访问

打开浏览器访问：`http://localhost:8080`

---

## 📖 使用指南

### 快捷问题
进入页面后，点击底部的快捷问题按钮快速开始：
- 📝 C++零基础入门
- 🔢 NOI竞赛大纲
- 🔄 for循环怎么用呀？
- 📚 什么是变量呢？
- 🐛 代码报错了怎么办？
- 🎮 怎么做一个小游戏？

### 上传代码文件
1. 点击输入框左侧的 📎 附件按钮
2. 选择 `.cpp/.cxx/.cc/.c/.h/.hpp` 文件
3. 在输入框中写下你的问题
4. 按回车或点击发送按钮

### 切换主题
点击右上角的 🌙/☀️ 按钮切换明暗主题

### 清空对话
点击侧边栏的 🗑️ 清空按钮清除当前对话历史

---

## 🎯 功能对比

| 功能 | Streamlit版本 | Chainlit版本 |
|------|---------------|--------------|
| Markdown渲染 | ⚠️ 部分支持 | ✅ 完美支持 |
| 代码语法高亮 | ❌ 不支持 | ✅ 支持 |
| 消息动画 | ❌ 无 | ✅ 流畅动画 |
| 打字指示器 | ⚠️ 文字提示 | ✅ 动画效果 |
| 文件上传 | ⚠️ 手动选择 | ✅ 拖拽+选择 |
| 响应式布局 | ⚠️ 基础适配 | ✅ 完美适配 |
| 暗色主题 | ❌ 无 | ✅ 一键切换 |
| 快捷问题 | ✅ 按钮 | ✅ 卡片式启动器 |
| 会话管理 | ⚠️ 基础 | ✅ 侧边栏管理 |
| 复制消息 | ❌ 无 | ✅ 一键复制 |

---

## 🔧 高级配置

### 环境变量

在 `.env` 文件中配置：

```bash
# 后端API地址
API_BASE_URL=http://localhost:8000

# Chainlit配置
CHAINLIT_PORT=8080
CHAINLIT_HOST=0.0.0.0
```

### 自定义快捷问题

编辑 `chainlit_app.py` 中的 `QUICK_QUESTIONS` 数组：

```python
QUICK_QUESTIONS = [
    "📝 C++零基础入门",
    "🔢 NOI竞赛大纲",
    # 添加你的快捷问题...
]
```

### 自定义CSS

编辑 `public/custom.css` 文件自定义样式

---

## 🐛 常见问题

### Q: 连接不到后端服务
**A:** 请确认后端服务已启动在 `http://localhost:8000`，运行 `start_backend.bat`

### Q: 文件上传失败
**A:** 确认文件格式为 `.cpp/.cxx/.cc/.c/.h/.hpp`，且编码为UTF-8/GBK

### Q: 代码没有语法高亮
**A:** Chainlit自动检测代码语言，确保代码块标记为 `cpp`

---

## 📝 更新日志

### v2.0.0 (Chainlit版本)
- ✅ 全新UI设计，美观度提升300%
- ✅ 原生Markdown渲染支持
- ✅ 代码语法高亮
- ✅ 流畅动画和过渡效果
- ✅ 拖拽文件上传
- ✅ 暗色主题切换
- ✅ 快捷问题卡片
- ✅ 响应式布局优化

### v1.0.0 (Streamlit版本)
- 基础聊天功能
- 流式输出
- 文件上传

---

## 🎓 技术栈

| 技术 | 说明 |
|------|------|
| **Chainlit** | AI对话框架，专为LLM应用设计 |
| **Markdown** | 原生支持，完美渲染格式化文本 |
| **Highlight.js** | 代码语法高亮引擎 |
| **FastAPI** | 后端API服务 |
| **SSE** | Server-Sent Events实现流式输出 |

---

## 💡 开发提示

### 项目结构

```
frontend/
├── chainlit_app.py      # Chainlit主应用
├── chainlit.md          # Chainlit配置
├── public/
│   ├── custom.css       # 自定义CSS
│   └── favicon.ico      # 网站图标
└── app.py               # Streamlit版本（保留）
```

### 如何调试

Chainlit支持热重载，修改代码后自动刷新：

```bash
chainlit run chainlit_app.py --watch
```

---

## 📞 支持

如有问题，请查看：
- Chainlit官方文档：https://docs.chainlit.io
- 项目Issues：https://github.com/your-repo/issues

---

**祝你学习愉快！🎉**

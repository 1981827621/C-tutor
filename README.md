# 🎓 C++小老师 - 竞赛助教Bot

> 🌟 专为中小学生设计的C++编程学习助手，可爱又智能！

## ✨ 主要功能

- 💬 **智能对话** - 用简单易懂的语言解答C++问题
- � **代码调试** - 帮你找出代码中的bug，一步步教你修改
- � **知识点学习** - 循环、数组、函数...不懂就问！
- 🎯 **竞赛技巧** - 教你拿比赛高分的秘诀
- 🧠 **知识检索** - 从教学资料中智能检索相关内容
- 🎨 **可爱界面** - 专为小朋友设计的美观界面和可爱语言风格

## 🏗️ 系统架构

```
用户输入（问题/错误代码）
    ↓
[前端] Streamlit 聊天界面
    ↓
[后端] FastAPI 后端
    ↓
[决策模块] 判断用户意图（求助、贴代码、问概念）
    ↓
[RAG检索] 从向量数据库中检索相关C++教学资料
    ↓
[Prompt构建] 根据意图 + 检索结果 + 对话历史 → 构造引导式Prompt
    ↓
[LLM调用] 调用DeepSeek大模型API
    ↓
[输出后处理] 格式化、过滤直接答案
    ↓
返回前端展示
```

##  快速开始

### 1. 安装依赖

```bash
# Windows用户
install.bat

# 或手动安装
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，并填入你的DeepSeek API密钥：

```bash
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
```

### 3. 准备知识库（开发者）

将教学资料文件放入 `knowledge_base` 目录：

```
knowledge_base/
├── 动态规划基础.pdf
├── STL容器详解.pptx
├── 图论算法总结.txt
└── 贪心算法技巧.docx
```

**支持的格式**：PDF、PPT、PPTX、TXT、DOCX

### 4. 启动服务

**方式一：使用启动脚本（推荐）**

```bash
# 启动后端服务（终端1）
start_backend.bat

# 启动前端界面（终端2）
start_frontend.bat
```

**方式二：手动启动**

```bash
# 启动后端
uvicorn cpp_tutor_bot.api.main:app --host 0.0.0.0 --port 8000 --reload

# 启动前端
streamlit run cpp_tutor_bot/frontend/app.py
```

### 5. 访问应用

- 前端界面：http://localhost:8501
- 后端API文档：http://localhost:8000/docs

## 📖 使用指南

### 向老师提问

直接输入你的问题，例如：
- "C++怎么输出Hello World呀？"
- "什么是变量呢？"
- "for循环怎么用呀？"

### 让老师帮你调试代码

粘贴你的代码并描述问题：
```
老师，我的代码运行不了，帮我看看哪里错了：

#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    // ... 我的代码
    return 0;
}
```

## 📁 项目结构

```
c++_tutor/
├── cpp_tutor_bot/
│   ├── __init__.py
│   ├── config.py              # 配置管理
│   ├── document_parser.py     # 文档解析模块
│   ├── vector_store.py        # 向量数据库模块
│   ├── intent_classifier.py   # 意图识别模块
│   ├── prompt_builder.py      # Prompt构建器
│   ├── llm_service.py         # LLM调用服务
│   ├── memory_manager.py      # 对话记忆管理
│   ├── api/
│   │   └── main.py            # FastAPI主应用
│   └── frontend/
│       └── app.py             # Streamlit前端
├── knowledge_base/            # 知识库目录
├── requirements.txt           # Python依赖
├── .env.example               # 环境变量示例
├── .env                       # 环境变量配置
├── install.bat                # 安装脚本
├── start_backend.bat          # 启动后端
├── start_frontend.bat         # 启动前端
└── README.md                  # 本文档
```

## 🔧 开发者指南

### 添加新的教学资料

1. 将文件放入 `knowledge_base` 目录
2. 重启后端服务，系统会自动加载

### 修改嵌入模型

编辑 `cpp_tutor_bot/vector_store.py`：

```python
# 使用其他中文嵌入模型
return HuggingFaceEmbeddings(
    model_name="GanymedeNil/text2vec-large-chinese"
)
```

### 调整检索数量

编辑 `.env` 文件：
```bash
TOP_K_RETRIEVAL=5  # 每次检索返回的文档数量
```

### 修改Prompt模板

编辑 `cpp_tutor_bot/prompt_builder.py` 中的系统提示词。

### 添加新的文档解析器

在 `document_parser.py` 中添加：

```python
class CustomParser(DocumentParser):
    def parse(self, file_path: str) -> str:
        # 实现你的解析逻辑
        pass

# 在DocumentProcessor中注册
self.parsers['.your_ext'] = CustomParser()
```

## 🐛 常见问题

### Q: 启动时提示无法连接到后端？
A: 确保先运行 `start_backend.bat`，并检查8000端口是否被占用。

### Q: 知识库没有加载？
A: 检查文件是否放在 `knowledge_base` 目录，重启后端服务查看控制台日志。

### Q: 回答质量不高？
A: 在 `knowledge_base` 目录添加更多相关教学资料。

"""
Prompt构建器模块
"""

from typing import List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from cpp_tutor_bot.intent_classifier import UserIntent


class PromptBuilder:
    """Prompt构建器 - 根据意图和检索结果构造引导式Prompt"""
    
    # 系统提示词模板
    SYSTEM_PROMPTS = {
        UserIntent.ASK_HELP: """你是一位专业的C++竞赛助教老师。你的任务是帮助学生理解C++编程和算法问题，但不要直接给出完整答案。

教学原则：
1. 引导学生思考，绝对不要给出完整可运行的代码答案
2. 提供思路和关键点提示
3. 解释相关知识点
4. 鼓励学生自己写出代码，可以给出伪代码示例，但不要直接给出完整代码
5. 如果学生贴了错误代码，指出错误并给出修改建议，但不要直接修正代码

请用中文回答，伪代码示例用C++。""",

        UserIntent.POST_CODE: """你是一位专业的C++竞赛代码调试助手。你的任务是帮助学生找出代码中的bug和性能问题。

调试原则：
1. 先指出代码中的具体错误
2. 解释为什么会出现这个错误
3. 给出修改建议和小提示，引导学生自己解决问题
4. 绝对不要直接给出完整的修正代码
5. 分析时间/空间复杂度问题（如果有）
6. 鼓励学生自己动手修改代码，如果学生仍失败，可以再给出更具体的提示，但不要直接给出完整代码
请用中文回答，用代码块展示关键修改点。""",

        UserIntent.ASK_CONCEPT: """你是一位C++教学专家。你的任务是清晰易懂地解释C++相关概念。

教学原则：
1. 你面向的是10~15岁的学生，用他们能够理解的简单易懂的语言解释
2. 提供核心模板代码示例，绝对不要给完整可运行的代码
3. 对比相似概念（如果适用）
4. 指出常见误区
5. 给出练习题或思考题

请用中文回答，代码使用c++""",

        UserIntent.GENERAL_CHAT: """你是一位友好的C++竞赛助教。和学生进行友好的对话，保持耐心和鼓励的态度。

原则：
1. 你面向的对象是10~15岁的学生，时刻记住对话风格；友善、耐心、鼓励
2. 鼓励学生继续学习
3. 提供学习建议
4. 引导学生思考

请用中文回答。"""
    }
    
    def __init__(self):
        self.default_system_prompt = self.SYSTEM_PROMPTS[UserIntent.GENERAL_CHAT]
    
    def build_system_prompt(self, intent: UserIntent) -> str:
        """根据意图获取系统提示词"""
        return self.SYSTEM_PROMPTS.get(intent, self.default_system_prompt)
    
    def build_user_prompt(self, 
                          user_input: str,
                          retrieved_context: Optional[str] = None,
                          conversation_history: Optional[List[dict]] = None) -> str:
        """构建用户Prompt"""
        prompt_parts = []
        
        # 添加检索到的参考资料
        if retrieved_context:
            prompt_parts.append(f"""以下是相关的C++教学资料，供你参考：

{retrieved_context}

---
基于以上资料和学生问题，请给出引导性的回答。""")
        
        # 添加学生问题
        prompt_parts.append(f"学生的问题：\n{user_input}")
        
        return "\n\n".join(prompt_parts)
    
    def build_messages(self,
                      user_input: str,
                      intent: UserIntent,
                      retrieved_context: Optional[str] = None,
                      conversation_history: Optional[List[dict]] = None) -> List:
        """
        构建完整的消息列表
        
        Args:
            user_input: 用户输入
            intent: 用户意图
            retrieved_context: 检索到的上下文
            conversation_history: 对话历史
        
        Returns:
            消息列表
        """
        messages = []
        
        # 系统消息
        system_prompt = self.build_system_prompt(intent)
        messages.append(SystemMessage(content=system_prompt))
        
        # 对话历史
        if conversation_history:
            for msg in conversation_history:
                if msg.get("role") == "human":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg.get("role") == "ai":
                    messages.append(AIMessage(content=msg["content"]))
        
        # 当前用户输入
        user_prompt = self.build_user_prompt(user_input, retrieved_context, conversation_history)
        messages.append(HumanMessage(content=user_prompt))
        
        return messages

"""
用户意图识别决策模块
"""

import re
from enum import Enum
from typing import Tuple


class UserIntent(Enum):
    """用户意图枚举"""
    ASK_HELP = "ask_help"          # 求助/问问题
    POST_CODE = "post_code"        # 贴代码求调试
    ASK_CONCEPT = "ask_concept"    # 问概念/知识点
    UPLOAD_FILE = "upload_file"    # 上传文件
    GENERAL_CHAT = "general_chat"  # 一般聊天


class IntentClassifier:
    """意图分类器"""
    
    # 关键词模式
    HELP_PATTERNS = [
        r'帮我', r'帮助', r'怎么做', r'怎么写', r'如何解决',
        r'为什么', r'怎么', r'请教', r'求助', r'不会',
        r'help', r'how to', r'can you'
    ]
    
    CODE_PATTERNS = [
        r'代码', r'程序', r'bug', r'错误', r'报错',
        r'调试', r'运行不了', r'编译失败', r'wa', r'tle',
        r'mle', r're', r'ce', r'超时', r'超内存'
    ]
    
    CONCEPT_PATTERNS = [
        r'什么是', r'解释', r'理解', r'概念', r'原理',
        r'区别', r'联系', r'怎么用', r'用法', r'语法',
        r'what is', r'explain', r'difference'
    ]
    
    def classify(self, user_input: str) -> Tuple[UserIntent, str]:
        """
        分类用户意图
        返回: (意图类型, 提取的关键信息)
        """
        text = user_input.strip().lower()
        
        # 检查是否包含代码块
        if self._contains_code(text):
            return UserIntent.POST_CODE, self._extract_code(text)
        
        # 检查各种意图模式
        for pattern in self.HELP_PATTERNS:
            if re.search(pattern, text):
                return UserIntent.ASK_HELP, self._extract_question(text)
        
        for pattern in self.CODE_PATTERNS:
            if re.search(pattern, text):
                return UserIntent.POST_CODE, self._extract_code_issue(text)
        
        for pattern in self.CONCEPT_PATTERNS:
            if re.search(pattern, text):
                return UserIntent.ASK_CONCEPT, self._extract_concept(text)
        
        # 默认为一般聊天
        return UserIntent.GENERAL_CHAT, text
    
    def _contains_code(self, text: str) -> bool:
        """检测是否包含代码"""
        code_indicators = [
            '```', '#include', 'int main', 'void', 'cout', 'cin',
            'printf', 'scanf', 'for(', 'while(', 'if(', '{', '}'
        ]
        return any(indicator in text for indicator in code_indicators)
    
    def _extract_code(self, text: str) -> str:
        """提取代码内容"""
        # 尝试提取代码块
        code_block_match = re.search(r'```(?:cpp|c\+\+|c)?\n(.*?)```', text, re.DOTALL)
        if code_block_match:
            return code_block_match.group(1).strip()
        return text
    
    def _extract_question(self, text: str) -> str:
        """提取问题内容"""
        return text
    
    def _extract_code_issue(self, text: str) -> str:
        """提取代码问题描述"""
        return text
    
    def _extract_concept(self, text: str) -> str:
        """提取概念关键词"""
        return text

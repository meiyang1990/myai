# -*- coding: utf-8 -*-
"""
注释生成模块 - 基于 LangChain + 火山引擎大模型生成中文代码注释

本模块负责：
1. 初始化 LangChain ChatOpenAI 对接火山引擎 API
2. 构建注释生成的 Prompt 模板
3. 将整个源码文件一次性提交给大模型，生成带有中文注释的完整代码
4. 解析大模型返回结果，提取带注释的代码
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import HumanMessage, SystemMessage

from config import (
    VOLCENGINE_API_KEY,
    VOLCENGINE_API_BASE,
    VOLCENGINE_MODEL_ENDPOINT,
    TEMPERATURE,
    MAX_TOKENS,
    COMMENT_STYLES,
)


# ========== Prompt 模板定义 ==========

SYSTEM_PROMPT = """你是一位资深的代码审阅专家和技术文档工程师。你的任务是为源代码添加高质量的中文注释。

## 硬性规则（不可违反）

以下规则具有最高优先级，MUST 严格遵守，不得以任何理由违反：

1. **绝对禁止修改源码**：你返回的代码逻辑 MUST 与原始代码完全一致。不能改变任何变量名、函数名、逻辑表达式、导入语句或代码结构。你只能添加或修改注释，NEVER 修改代码本身。
2. **跳过简单代码行**：以下类型的代码行不生成注释：
   - import / from 导入语句
   - 简单变量声明（如 `x = 1`、`const name = "hello"` 等）
   - 简单逻辑计算（如 `total = a + b`、`flag = x > 0` 等）
3. **简短函数仅添加函数级注释**：当函数体代码在 5 行以内（不含函数定义行和空行）时，仅在函数定义上方添加一条简洁的中文注释说明函数作用，不对函数体内部逐行注释。
4. **其他代码逐行简洁注释**：不属于上述豁免类别的代码行，MUST 逐行添加中文注释。注释务必简洁，用最短的文字说清楚代码的作用，避免冗长解释和修饰词。
5. **注释简洁性**：所有注释 MUST 简洁明了，能说清代码作用即可，NEVER 使用繁琐冗余的描述。

## 注释原则

1. **使用简体中文**：所有注释内容统一使用简体中文。
2. **注释层级**：
   - **文件级注释**：在文件开头添加，说明文件所属模块、核心职责和主要功能。
   - **类级注释**：在类定义前添加，描述类的设计目的、核心职责和关键协作者。
   - **方法/函数级注释**：在方法定义前添加，解释功能、参数含义、返回值和异常情况。
   - **行内注释**：针对复杂逻辑、算法、非直观代码添加解释性注释。
3. **避免冗余注释**：import/from 导入语句、简单变量声明、简单逻辑计算不生成注释；5 行以内的简短函数仅生成函数级注释而非逐行注释。
4. **注释要体现业务含义**：不仅翻译代码表面逻辑，还要结合上下文说明业务含义。
5. **遵循语言注释规范**：根据编程语言使用对应的标准注释格式（如 Java 用 Javadoc、Python 用 Docstring 等）。

## 输出要求

- 直接输出添加了注释的完整源代码。
- 不要添加任何额外的解释文字或 markdown 格式标记。
- 不要用 ```代码块``` 包裹代码。
- 保持原始代码的缩进、空行和格式完全不变。
- 确保输出的代码可以直接编译/运行。"""


HUMAN_PROMPT_TEMPLATE = """请为以下 {language} 源代码文件添加中文注释。

文件路径：{file_path}

源代码内容：
{source_code}"""


# 项目上下文注入到 System Prompt 的补充节
PROJECT_CONTEXT_SECTION = """

## 项目背景信息

以下是该项目的架构设计和背景概要，请结合这些信息为代码生成更有深度和业务含义的注释：

{project_context}"""


class CommentGenerator(object):
    """
    注释生成器 - 使用 LangChain 对接火山引擎大模型生成代码注释

    工作流程：
    1. 通过 ChatOpenAI（兼容模式）连接火山引擎大模型 API
    2. 构建包含系统指令和源码内容的 Prompt
    3. 将整个文件一次性发送给大模型（可注入项目上下文概要）
    4. 获取带有中文注释的完整代码并返回
    """

    def __init__(self, project_context=None):
        """
        初始化注释生成器，建立与火山引擎大模型的连接

        Args:
            project_context (str or None): 项目上下文概要文档（Markdown 格式）。
                                           如果提供，将追加到 System Prompt 中增强注释质量。
        """
        # 使用 ChatOpenAI 通过兼容 OpenAI 协议接入火山引擎
        self.llm = ChatOpenAI(
            model=VOLCENGINE_MODEL_ENDPOINT,
            openai_api_key=VOLCENGINE_API_KEY,
            openai_api_base=VOLCENGINE_API_BASE,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )

        # 根据是否有项目上下文，构建不同的 System Prompt
        if project_context:
            enhanced_system_prompt = SYSTEM_PROMPT + PROJECT_CONTEXT_SECTION.format(
                project_context=project_context
            )
        else:
            enhanced_system_prompt = SYSTEM_PROMPT

        # 构建 Chat Prompt 模板
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(enhanced_system_prompt),
            HumanMessagePromptTemplate.from_template(HUMAN_PROMPT_TEMPLATE),
        ])

    def generate_comment(self, source_file):
        """
        为单个源码文件生成中文注释

        将整个源码文件内容一次性提交给大模型，由大模型返回添加了注释的完整代码。

        Args:
            source_file: SourceFile 对象，包含文件路径、语言类型和源码内容

        Returns:
            str or None: 添加了中文注释的完整代码内容。
                         如果生成失败则返回 None。
        """
        language = source_file.language
        file_path = source_file.rel_path
        source_code = source_file.content

        try:
            # 格式化 Prompt，填充变量
            messages = self.prompt.format_messages(
                language=language,
                file_path=file_path,
                source_code=source_code,
            )

            # 调用大模型生成注释
            response = self.llm.invoke(messages)

            # 提取生成的代码内容
            commented_code = response.content

            # 后处理：去除大模型可能多余包裹的 markdown 代码块标记
            commented_code = self._clean_response(commented_code)

            return commented_code

        except Exception as e:
            print("[错误] 生成注释失败 (%s): %s" % (file_path, str(e)))
            return None

    def _clean_response(self, text):
        """
        清理大模型返回内容中可能包含的 markdown 代码块标记

        大模型有时会在返回结果中自动添加 ```language ... ``` 包裹，
        这里将其去除，只保留纯代码内容。

        Args:
            text (str): 大模型返回的原始文本

        Returns:
            str: 清理后的纯代码文本
        """
        if text is None:
            return text

        text = text.strip()

        # 检查是否以 ``` 开头（可能带有语言标识）
        if text.startswith("```"):
            # 找到第一个换行符，跳过 ```language 这一行
            first_newline = text.find("\n")
            if first_newline != -1:
                text = text[first_newline + 1:]

            # 去除末尾的 ```
            if text.endswith("```"):
                text = text[:-3]

            text = text.strip()

        return text

    def test_connection(self):
        """
        测试与火山引擎大模型 API 的连接是否正常

        Returns:
            tuple: (是否连接成功, 消息)
        """
        try:
            messages = [
                HumanMessage(content="请回复'连接成功'四个字。")
            ]
            response = self.llm.invoke(messages)
            if response and response.content:
                return True, "API 连接正常: %s" % response.content.strip()
            else:
                return False, "API 返回为空"
        except Exception as e:
            return False, "API 连接失败: %s" % str(e)

# Change: 实现核心代码模块（Python + LangChain + 火山引擎 API）

## Why

项目已完成文档体系搭建和功能规格定义，但缺少实际可运行的代码实现。需要基于 Python 3.6 + LangChain v0.1.16 + 火山引擎大模型 API 实现核心代码模块，使工具具备端到端的代码注释生成能力。

## What Changes

- **新增** `config.py`：统一配置模块，管理火山引擎 API 配置、文件扫描规则和注释风格模板
- **新增** `source_reader.py`：源码读取模块，实现递归目录扫描、编程语言识别、.gitignore 规则支持和文件内容加载
- **新增** `comment_generator.py`：注释生成核心模块，使用 LangChain ChatOpenAI 通过 OpenAI 兼容协议接入火山引擎大模型，整个文件一次性提交大模型生成中文注释
- **新增** `comment_writer.py`：注释回写模块，支持输出到新目录（安全模式）或覆盖原文件两种模式
- **新增** `main.py`：命令行工具入口，支持测试 API、扫描预览、生成注释等多种运行模式
- **新增** `requirements.txt`：Python 依赖管理文件
- **新增** `.env.example`：环境变量配置模板
- **修改** `README.md`：更新项目结构和使用方式说明

## Impact

- Affected specs: `source-code-reader`, `comment-generator`
- Affected code: 新增 5 个 Python 模块、1 个依赖文件、1 个配置模板
- 技术栈选型：Python 3.6、LangChain 0.1.16、langchain-openai 0.1.3、火山引擎 v3 API（OpenAI 兼容协议）

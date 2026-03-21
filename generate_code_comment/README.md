# 🤖 Generate Code Comment（智能代码注释生成器）

> 基于 AI 的智能代码注释生成工具 —— 深度理解项目架构与业务逻辑，自动为源码生成高质量中文注释。

## 📖 项目简介

`generate_code_comment` 是 [myai](https://github.com/meiyang1990/myai) 项目的核心子模块，它利用 AI 的代码理解能力，实现了一套完整的**源码阅读 → 架构梳理 → 注释生成**工作流。

### 解决的核心问题

| 痛点 | 解决方案 |
|------|----------|
| 🆕 新成员接手项目理解成本高 | 自动生成系统性的中文注释，降低阅读门槛 |
| 📜 遗留代码缺少注释 | 批量扫描并为无注释代码补充说明 |
| ⏰ 人工注释耗时且易遗漏 | AI 自动分析并覆盖所有关键代码块 |
| 📊 注释质量参差不齐 | 统一注释风格和质量标准 |

## 🏗️ 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────┐
│                  智能代码注释生成器                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ 源码读取  │ → │ 架构分析  │ → │ 流程解析  │          │
│  │  模块    │  │  模块    │  │  模块    │          │
│  └──────────┘  └──────────┘  └──────────┘          │
│       │              │              │               │
│       ▼              ▼              ▼               │
│  ┌─────────────────────────────────────┐            │
│  │        项目上下文理解引擎             │            │
│  │  (架构模式 / 模块关系 / 业务逻辑)     │            │
│  └─────────────────────────────────────┘            │
│                      │                              │
│                      ▼                              │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │  注释生成模块  │ → │  注释回写模块  │                 │
│  └──────────────┘  └──────────────┘                 │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 核心模块说明

#### 1. 源码读取模块

- 递归扫描目标项目的源码目录
- 识别文件类型和编程语言
- 过滤配置文件、构建产物等非核心文件
- 支持 `.gitignore` 规则

#### 2. 架构分析模块

- 识别项目整体架构模式（MVC、微服务、分层架构等）
- 分析模块划分和包结构
- 梳理模块间的依赖关系
- 识别核心设计模式的使用

#### 3. 流程解析模块

- 追踪核心业务流程和调用链
- 分析数据流转路径
- 识别关键算法和复杂逻辑
- 理解错误处理和异常流程

#### 4. 注释生成模块

- 基于项目上下文生成有意义的中文注释
- 支持多层级注释：文件级 / 类级 / 方法级 / 行内
- 遵循各语言社区注释规范（Javadoc、JSDoc、Docstring 等）
- 确保注释的准确性和可读性

#### 5. 注释回写模块

- 将生成的注释准确插入源码对应位置
- 保持原有代码格式和缩进不变
- 支持幂等操作，避免重复注释
- 提供预览和确认机制

## 🔄 工作流程

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  输入    │    │  扫描    │    │  分析    │    │  生成    │    │  输出    │
│  目标    │ →  │  源码    │ →  │  理解    │ →  │  注释    │ →  │  回写    │
│  项目    │    │  文件    │    │  架构    │    │  内容    │    │  源码    │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

### 详细流程

1. **指定目标项目** → 用户提供需要添加注释的项目路径
2. **源码扫描** → 递归遍历项目目录，识别所有源码文件
3. **架构识别** → 分析项目结构，识别架构模式和分层设计
4. **模块分析** → 梳理模块关系、依赖关系和调用链
5. **逻辑理解** → 深入理解每个文件的业务逻辑和实现细节
6. **注释生成** → 根据分析结果为每个代码块生成中文注释
7. **注释回写** → 将注释插入源码，生成带注释的新版本文件

## 💡 注释生成规范

### 文件级注释

```java
/**
 * 用户认证服务 - 处理用户登录、注册和令牌管理
 * 
 * 本类是认证模块的核心服务，负责：
 * 1. 用户凭证验证和身份认证
 * 2. JWT 令牌的签发与刷新
 * 3. 会话管理和登出处理
 * 
 * 依赖关系：
 * - UserRepository: 用户数据访问
 * - PasswordEncoder: 密码加解密
 * - JwtTokenProvider: JWT 令牌管理
 * 
 * @author AI Code Commenter
 * @since 1.0.0
 */
```

### 方法级注释

```java
/**
 * 验证用户凭证并签发访问令牌
 * 
 * 流程：查询用户 → 校验密码 → 生成令牌 → 记录登录日志
 * 
 * @param username 用户名（不可为空）
 * @param password 明文密码（将与存储的密文进行比对）
 * @return 包含 accessToken 和 refreshToken 的认证响应对象
 * @throws AuthenticationException 当用户名不存在或密码错误时抛出
 */
```

### 行内注释

```java
// 使用 BCrypt 算法校验密码，时间复杂度为 O(2^cost)，防止暴力破解
if (!passwordEncoder.matches(password, user.getPasswordHash())) {
    // 记录失败次数，连续5次失败后锁定账户30分钟
    loginAttemptService.recordFailure(username);
    throw new AuthenticationException("凭证无效");
}
```

## 🎯 支持的语言和框架

| 语言 | 框架/生态 | 注释格式 |
|------|----------|---------|
| Java | Spring Boot, Maven, Gradle | Javadoc (`/** */`) |
| TypeScript/JavaScript | React, Vue, Node.js | JSDoc (`/** */`) |
| Python | Django, Flask, FastAPI | Docstring (`"""  """`) |
| Go | Gin, Echo, 标准库 | GoDoc (`//`) |
| Kotlin | Spring Boot, Android | KDoc (`/** */`) |
| C/C++ | 标准库, Qt | Doxygen (`/** */`) |

## 🛡️ 设计约束

1. **只添加注释，不修改逻辑** — 绝不改变任何一行业务代码
2. **保持代码格式** — 注释插入不破坏原有缩进和排版
3. **幂等操作** — 重复执行不会产生重复注释
4. **本地处理** — 所有源码分析在本地完成，不泄露代码内容
5. **增量支持** — 大型项目可增量处理，无需一次加载全部文件

## 📂 项目结构

```
generate_code_comment/
├── config.py                      # 配置模块（API 配置、扫描规则、注释风格）
├── source_reader.py               # 源码读取模块（目录扫描、语言识别、文件过滤）
├── comment_generator.py           # 注释生成模块（LangChain + 火山引擎大模型）
├── comment_writer.py              # 注释回写模块（文件输出、目录管理）
├── progress_tracker.py            # 进度跟踪模块（断点续传、处理进度管理）
├── project_context.py             # 项目上下文分析模块（架构识别、模块关系）
├── main.py                        # 主程序入口（命令行工具）
├── requirements.txt               # Python 依赖管理
├── setup.sh                       # 环境初始化脚本
├── .env.example                   # 环境变量配置模板
├── openspec/                      # OpenSpec 规格文档
│   ├── AGENTS.md                  # AI 助手指南
│   ├── project.md                 # 项目上下文
│   ├── specs/                     # 功能规格
│   └── changes/                   # 变更提案
├── AGENTS.md                      # 项目级 AI 指南
├── CODEBUDDY.md                   # CodeBuddy 配置入口
└── README.md                      # 本文档
```

## 🚀 使用方式

### 前置要求

- Python >= 3.11.9
- 火山引擎账号，已开通大模型服务（豆包模型）
- 已创建推理接入点（Endpoint）

### 安装依赖

```bash
cd generate_code_comment
pip install -r requirements.txt
```

### 配置火山引擎 API

1. 复制环境变量模板：

```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填写你的火山引擎配置：

```bash
# 火山引擎 API Key（在火山引擎控制台获取）
VOLCENGINE_API_KEY=your-api-key-here

# API 地址（默认即可）
VOLCENGINE_API_BASE=https://ark.cn-beijing.volces.com/api/v3

# 推理接入点 ID（在火山方舟控制台 -> 在线推理 -> 创建推理接入点后获取）
VOLCENGINE_MODEL_ENDPOINT=ep-20240901xxxxx-xxxxx
```

### 快速开始

```bash
# 1. 测试 API 连接
python main.py --test-api

# 2. 扫描项目（预览将处理哪些文件）
python main.py /path/to/your/project --scan-only

# 3. 生成注释（输出到新目录，不影响原文件）
python main.py /path/to/your/project

# 4. 指定输出目录
python main.py /path/to/your/project -o /path/to/output

# 5. 直接覆盖原文件（谨慎使用，建议先 git commit）
python main.py /path/to/your/project --overwrite

# 6. 同时复制非源码文件到输出目录
python main.py /path/to/your/project --copy-others
```

### 命令行参数说明

| 参数 | 说明 |
|------|------|
| `project_path` | 目标项目的根目录路径 |
| `-o, --output` | 输出目录路径（默认为 `<项目路径>_commented`） |
| `--overwrite` | 直接覆盖原始文件（谨慎使用） |
| `--scan-only` | 仅扫描并列出将处理的文件 |
| `--test-api` | 测试火山引擎 API 连接 |
| `--copy-others` | 在输出模式下同时复制非源码文件 |

### 技术栈

| 组件 | 版本 | 说明 |
|------|------|------|
| Python | >= 3.11.9 | 运行环境 |
| LangChain | 0.1.16 | AI 编排框架 |
| langchain-openai | 0.1.3 | OpenAI 兼容接口 |
| 火山引擎 | v3 API | 大模型服务（兼容 OpenAI 协议） |

## 📋 开发计划

- [x] 项目初始化与文档体系搭建
- [x] 源码读取与解析模块
- [x] 注释生成模块（LangChain + 火山引擎）
- [x] 注释回写与格式保持
- [x] 命令行工具入口
- [ ] 架构分析引擎（增强注释上下文理解）
- [ ] 增量处理与性能优化
- [ ] 注释质量评估与反馈机制

## 🤝 贡献指南

1. 通过 OpenSpec Proposal 提出功能变更
2. 等待提案审批后再开始实施
3. 实施完成后通过 OpenSpec Archive 归档变更
4. 详细流程参见 [openspec/AGENTS.md](openspec/AGENTS.md)

## 📄 许可证

本项目为 myai 的一部分，遵循项目统一的开源许可协议。

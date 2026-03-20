# 🧠 myai — AI 辅助开发工具集

> 一组基于 AI 的智能开发辅助工具，旨在提升代码质量、降低理解成本、加速开发效率。

## 📖 项目简介

**myai** 是一个 AI 辅助开发工具集合项目，汇聚了多个面向开发者的智能工具。每个子模块专注于解决开发过程中的特定痛点，通过 AI 的代码理解和生成能力，为开发者提供高效、智能的辅助支持。

## 📦 子模块

### [generate_code_comment](./generate_code_comment/) — 智能代码注释生成器

🤖 基于 AI 的智能代码注释生成工具，核心能力包括：

- **深度源码理解**：自动读取和分析目标项目源代码
- **架构设计梳理**：识别项目的架构模式、分层设计和模块关系
- **流程设计解析**：追踪核心业务流程、调用链路和数据流转
- **中文注释生成**：基于对项目的深刻理解，为代码生成高质量中文注释

详细文档请参见 [generate_code_comment/README.md](./generate_code_comment/README.md)

## 🛠️ 技术栈

- **AI 编排**：CodeBuddy IDE + AI Skill
- **规格管理**：OpenSpec 规格驱动开发
- **版本控制**：Git

## 🚀 快速开始

1. 安装 [CodeBuddy IDE](https://www.codebuddy.ai/)
2. 克隆本仓库
   ```bash
   git clone https://github.com/meiyang1990/myai.git
   ```
3. 在 CodeBuddy 中打开对应子模块目录
4. 按照各子模块的使用说明操作

## 📋 项目路线图

- [x] 项目初始化
- [x] generate_code_comment 子模块 — 文档体系搭建
- [ ] generate_code_comment 子模块 — 核心功能实现
- [ ] 更多 AI 辅助工具（规划中）

## 📄 许可证

MIT License

# 🚀 AI 简历智能解析与岗位匹配系统

> **24小时挑战赛产出**：一套基于 **FastAPI** 与 **通义千问大模型** 的全栈式招聘辅助解决方案。

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![AI Model](https://img.shields.io/badge/AI-Qwen--Turbo-blue?style=flat-square)](https://help.aliyun.com/document_detail/2712214.html)
[![Deployment](https://img.shields.io/badge/Deployment-HuggingFace-FFD21E?style=flat-square&logo=huggingface)](https://huggingface.co/spaces)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](https://opensource.org/licenses/MIT)

---

## 🏗️ 项目架构 (Architecture)
系统采用现代化云原生架构，确保了从解析到交互的高性能表现：
- **前端 (Frontend)**：HTML5 + TailwindCSS 响应式设计，适配多端访问。
- **后端 (Backend)**：FastAPI 异步架构，支持高效的并发请求处理。
- **AI 引擎 (LLM)**：集成 **阿里通义千问 (Qwen-Turbo)**，实现简历文本到结构化 JSON 的深度映射。
- **持久化与缓存**：自研 **MD5 文件哈希指纹** 技术，实现秒级响应的本地缓存逻辑，大幅降低 API 调用成本。

---

## ✨ 功能实现清单 (Task Progress)

| 模块 | 功能描述 | 状态 | 技术实现要点 |
| :--- | :--- | :--- | :--- |
| **模块一/二** | 简历上传与解析 | ✅ 完成 | PyMuPDF (fitz) 高精度提取 + 文本清洗 |
| **模块三** | 智能评分与匹配 | ✅ 完成 | 基于 AI 的语义对标与多维度匹配度评分 |
| **模块四** | 结果缓存 (加分项) | ✅ 完成 | 基于文件哈希的 JSON 持久化存储机制 |
| **模块五** | Web 交互页面 | ✅ 完成 | 响应式 UI + 自动化接口文档 (Swagger UI) |

---

## 🚀 访问与运行 (Quick Start)

### 1. 线上演示 (验收推荐)
- **Web 交互入口**: [点击访问演示页面](https://ceciliayyy-resume-tool-yk.hf.space/)
- **API 自动化文档**: [访问 FastAPI Docs](https://ceciliayyy-resume-tool-yk.hf.space/docs)  

### 2. 本地开发环境部署
```bash
# 1. 克隆并进入目录
git clone <your-repo-url>
cd resume-tool

# 2. 安装核心依赖
pip install -r requirements.txt

# 3. 设置环境变量 (请确保已获取 DashScope API Key)
export DASHSCOPE_API_KEY="your_api_key_here"

# 4. 启动服务
python main.py

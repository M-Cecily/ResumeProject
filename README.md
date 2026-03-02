# 🚀 AI 简历智能解析与岗位匹配系统

本项目是一套基于 **FastAPI** 与 **通义千问大模型** 开发的招聘辅助工具，旨在实现简历自动化处理、结构化提取与智能化评分。

---

## 🏗️ 项目架构 (Architecture)
系统采用前后端分离架构，结合 AI 推理层实现高效处理：
- **前端 (Frontend)**：HTML5 + TailwindCSS 响应式界面。
- **后端 (Backend)**：FastAPI 异步框架，负责路由分发与业务逻辑。
- **AI 层 (LLM)**：集成通义千问 API，负责 JSON 结构化提取与匹配评分。
- **缓存层 (Cache)**：基于 MD5 哈希的文件指纹持久化机制（挑战项实现）。

---

## 🛠️ 技术选型 (Tech Stack)
- **后端**：Python 3.10+, FastAPI, PyMuPDF (fitz)
- **AI 能力**：阿里云百炼 - Qwen-Turbo
- **前端**：TailwindCSS, JavaScript (Fetch API)
- **部署**：Zeabur (云端托管), GitHub (版本控制)

---

## ✨ 核心功能
1. **模块一 & 二**：PDF 文本清洗与关键信息（个人信息、技能、教育）提取。
2. **模块三**：输入岗位描述 (JD) 即可获得 AI 生成的匹配得分与理由。
3. **模块四 (加分项)**：**哈希指纹缓存**。相同文件无需重复调用 API，秒级加载。
4. **模块五**：现代化的 Web 交互页面。

---

## 🚀 部署与运行 (Deployment)
### 1. 在线演示 (推荐)
[点击此处访问在线演示地址](在此填入你的Zeabur链接)

### 2. 本地运行
1. 配置环境变量 `DASHSCOPE_API_KEY`。
2. 执行 `pip install -r requirements.txt`。
3. 运行 `python main.py` 并访问 `http://127.0.0.1:8000`。

---

## 🔒 安全说明
本项目已通过 `os.getenv` 进行 API Key 脱敏处理，源代码中不包含任何私密信息，符合生产安全规范。

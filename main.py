import fitz  # PyMuPDF
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dashscope import Generation
import json
import uvicorn
import re
import os
import hashlib

app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 配置与缓存初始化 ---
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
CACHE_FILE = "/tmp/resume_cache.json"  # 在 Docker 环境中使用 /tmp 目录有写权限

def get_file_hash(content):
    return hashlib.md5(content).hexdigest()

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache_data):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except:
        pass

resume_cache = load_cache()

SYSTEM_PROMPT = """你是一个专业的简历提取助手。请严格返回JSON格式：
{
  "基本信息": {"姓名": "", "电话": "", "邮箱": ""},
  "教育背景": [{"学校": "", "专业": ""}],
  "核心技能": []
}
只返回纯JSON，不要Markdown代码块。"""

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

# --- API 路由定义 (必须放在静态挂载之前) ---

@app.post("/api/upload")
async def upload_and_analyze(file: UploadFile = File(...)):
    try:
        content = await file.read()
        file_hash = get_file_hash(content)

        if file_hash in resume_cache:
            return resume_cache[file_hash]

        doc = fitz.open(stream=content, filetype="pdf")
        raw_text = "".join([page.get_text() for page in doc])
        cleaned_text = clean_text(raw_text)

        response = Generation.call(
            model='qwen-turbo',
            api_key=DASHSCOPE_API_KEY,
            prompt=f"{SYSTEM_PROMPT}\n\n简历：\n{cleaned_text[:2000]}",
            result_format='message'
        )

        ai_msg = response.output.choices[0].message.content
        match = re.search(r'\{.*\}', ai_msg, re.DOTALL)

        if match:
            result = json.loads(match.group())
            resume_cache[file_hash] = result
            save_cache(resume_cache)
            return result
        else:
            return {"error": "AI格式返回异常"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/match")
async def match_resume(resume_data: str = Form(...), job_description: str = Form(...)):
    try:
        prompt = f"""
        对比简历JSON和岗位JD，返回JSON：{{"score": 0-100, "match_reason": ""}}
        简历：{resume_data}
        需求：{job_description}
        """
        response = Generation.call(
            model='qwen-turbo',
            api_key=DASHSCOPE_API_KEY,
            prompt=prompt,
            result_format='message'
        )
        ai_msg = response.output.choices[0].message.content
        match = re.search(r'\{.*\}', ai_msg, re.DOTALL)
        return json.loads(match.group()) if match else {"score": 0, "reason": "解析失败"}
    except Exception as e:
        return {"error": str(e)}

# --- 静态文件处理 (终极版) ---

# 获取当前 main.py 的绝对目录

from fastapi.responses import HTMLResponse

@app.get("/")
async def index():
    # 直接读取文件内容并返回，绕过所有路径映射问题
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return {"error": f"读取失败，请确认 static/index.html 存在。错误: {str(e)}"}

# 依然挂载 static 文件夹，方便加载 CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)

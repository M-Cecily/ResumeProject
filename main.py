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
CACHE_FILE = "resume_cache.json"

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
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)

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

# --- 核心逻辑接口 ---

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
        prompt = f"对比简历JSON和岗位JD，返回JSON：{{\"score\": 0-100, \"match_reason\": \"\"}}\n简历：{resume_data}\n需求：{job_description}"
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

# --- 静态文件与首页路由逻辑 (502 终结者) ---

# 获取当前 main.py 所在的绝对目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

@app.get("/")
async def read_index():
    """强制首页返回 static/index.html"""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "Backend is running", "error": f"Missing index.html in {STATIC_DIR}"}

# 挂载静态资源目录
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")
    print(f"✅ 静态文件挂载成功: {STATIC_DIR}")

if __name__ == "__main__":
    # 强制使用 8080 端口以适配 Zeabur 网关
    uvicorn.run(app, host="0.0.0.0", port=8080)

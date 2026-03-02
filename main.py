import fitz  # PyMuPDF
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dashscope import Generation
import json
import uvicorn
import re
import os
import hashlib  # 用于生成文件指纹 (模块四挑战项)

app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 配置与缓存初始化 ---
# 从环境变量读取，如果读取不到则为空
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
CACHE_FILE = "resume_cache.json"


def get_file_hash(content):
    """生成文件的MD5哈希值，作为唯一标识"""
    return hashlib.md5(content).hexdigest()


def load_cache():
    """从本地文件读取缓存数据"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_cache(cache_data):
    """将缓存数据保存到本地文件"""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)


# 初始化内存缓存变量
resume_cache = load_cache()

# AI 提示词
SYSTEM_PROMPT = """你是一个专业的简历提取助手。请严格返回JSON格式：
{
  "基本信息": {"姓名": "", "电话": "", "邮箱": ""},
  "教育背景": [{"学校": "", "专业": ""}],
  "核心技能": []
}
只返回纯JSON，不要Markdown代码块。"""


# --- 核心逻辑 ---

def clean_text(text):
    """模块一：文本清洗"""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()


@app.post("/api/upload")
async def upload_and_analyze(file: UploadFile = File(...)):
    """模块一 & 二：解析与提取（含缓存检查）"""
    try:
        content = await file.read()
        file_hash = get_file_hash(content)

        # --- 模块四：缓存命中检查 ---
        if file_hash in resume_cache:
            print(f"🚀 命中缓存！文件指纹: {file_hash}")
            return resume_cache[file_hash]

        # 未命中缓存，执行解析
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
            # --- 模块四：存入缓存 ---
            resume_cache[file_hash] = result
            save_cache(resume_cache)
            return result
        else:
            return {"error": "AI格式返回异常"}

    except Exception as e:
        return {"error": str(e)}


@app.post("/api/match")
async def match_resume(resume_data: str = Form(...), job_description: str = Form(...)):
    """模块三：简历评分与岗位匹配"""
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


# --- 静态文件与服务启动 ---
current_dir = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(current_dir, "static")

if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
    print(f"✅ 挂载成功！地址: http://127.0.0.1:8000")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
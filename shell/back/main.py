# back/main.py
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from models import AIModels
from printer import print_ticket


app = FastAPI(title="Emotion Pearl Backend")

# --- CORS，方便本地前端在 8081 / 3000 调用 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段先放开，后面可以限定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR.parent / "static"
PEARL_DIR = STATIC_DIR / "pearls"
PEARL_DIR.mkdir(parents=True, exist_ok=True)

# 挂载静态文件，方便直接访问 /static/pearls/xxx.jpg
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# --------- 请求/响应模型 ---------
class Img2TextRequest(BaseModel):
    username: str
    imgurl: str


class Img2TextResponse(BaseModel):
    prompt: str          # 提示词（英文）
    raw: Dict[str, Any]  # 完整原始返回，方便前端调试


class PearlGenRequest(BaseModel):
    prompt: str
    username: str | None = None


class PearlGenResponse(BaseModel):
    pearl_id: str
    img_url: str         # 返回给前端的图片 URL（相对路径）


class PrintRequest(BaseModel):
    view_url: str        # 前端展示页面链接
    emotion:str          #检测到的情绪
    comfort: str         # 要打印的安慰语
    


# --------- 辅助函数 ---------
def _extract_siliconflow_text(resp: Dict[str, Any]) -> str:
    """
    从 SiliconFlow 的返回 JSON 中尽量提取文本内容。
    兼容 content 为 string 或 list 的情况。
    """
    try:
        message = resp["choices"][0]["message"]["content"]
        # 可能是字符串，可能是多段 content 列表
        if isinstance(message, str):
            return message
        if isinstance(message, list):
            texts = []
            for part in message:
                if isinstance(part, dict) and part.get("type") == "text":
                    texts.append(part.get("text", ""))
            if texts:
                return "".join(texts)
        return str(message)
    except Exception:
        return str(resp)


# --------- 路由实现 ---------
@app.post("/api/img2text", response_model=Img2TextResponse)
async def img2text_endpoint(req: Img2TextRequest):
    """
    前端调用：
    POST /api/img2text
    body: { "username": "...", "imgurl": "http://..." }

    功能：
    调 Qwen3-VL 读取纸条图片，返回用于生成珍珠图像的英文 prompt。
    """
    resp_json = await AIModels.img2text(req.username, req.imgurl)
    prompt = _extract_siliconflow_text(resp_json)
    return Img2TextResponse(prompt=prompt, raw=resp_json)


@app.post("/api/generate_pearl", response_model=PearlGenResponse)
async def generate_pearl_endpoint(req: PearlGenRequest):
    """
    前端调用：
    POST /api/generate_pearl
    body: { "prompt": "英文提示词", "username": "可选" }

    功能：
    调 Stability SD3.5 生成珍珠图片，保存到 static/pearls 下，
    返回 pearl_id 和图片 URL（例如 /static/pearls/xxxx.jpg）。
    """
    img_bytes = await AIModels.pearlGen(req.prompt)

    pearl_id = uuid4().hex[:12]
    filename = f"{pearl_id}.jpg"
    out_path = PEARL_DIR / filename
    with open(out_path, "wb") as f:
        f.write(img_bytes)

    img_url = f"/static/pearls/{filename}"
    return PearlGenResponse(pearl_id=pearl_id, img_url=img_url)


@app.post("/api/print_ticket")
async def print_ticket_endpoint(req: PrintRequest):
    """
    前端或后端其它模块调用：
    POST /api/print_ticket
    body: { "view_url": "...", "emotion":"悲伤","comfort": "..." }

    功能：
    调佳博云打印机，打印一张包含二维码 + 安慰语的小票。
    """
    try:
        result = await print_ticket(req.view_url, req.emotion,req.comfort)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"打印失败: {e!s}")
    return {"status": "ok", "gateway": result}

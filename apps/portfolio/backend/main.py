"""portfolio 作品集站 — FastAPI 后端
公开: 作品墙 / 媒体文件
管理: HMAC cookie 鉴权 + 上传(缩略图) + 编辑 + 删除
"""
import base64
import hashlib
import hmac
import json
import os
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Cookie, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel

from apps.portfolio.backend import config, models

app = FastAPI(title="fake_yuki Portfolio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    config.MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    models.init_db()
    yield


app.router.lifespan_context = lifespan

COOKIE_NAME = "yuki_admin"


# ═══════════════════════════════════════════════
#  Auth — HMAC 签名 token（无状态，7 天过期）
# ═══════════════════════════════════════════════

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _b64url_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _sign_token() -> str:
    payload = json.dumps({"sub": "admin", "exp": int(time.time()) + config.TOKEN_TTL_SECONDS})
    body = _b64url(payload.encode())
    sig = hmac.new(config.AUTH_SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{sig}"


def _verify_token(token: str) -> bool:
    try:
        body, sig = token.split(".", 1)
        expected = hmac.new(config.AUTH_SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return False
        data = json.loads(_b64url_decode(body))
        return data.get("exp", 0) > time.time()
    except Exception:
        return False


def _auth_cookie(token: str, max_age: int) -> dict:
    return {
        "key": COOKIE_NAME, "value": token,
        "httponly": True, "samesite": "lax", "path": "/", "max_age": max_age,
    }


def require_admin(yuki_admin: str | None = Cookie(default=None)):
    if not yuki_admin or not _verify_token(yuki_admin):
        raise HTTPException(401, "未登录或会话已过期")
    return True


# ═══════════════════════════════════════════════
#  Pages
# ═══════════════════════════════════════════════

def _serve_page(filename: str) -> HTMLResponse:
    with open(config.FRONTEND_DIR / filename, encoding="utf-8") as f:
        return HTMLResponse(f.read(), headers={"Cache-Control": "no-store, must-revalidate"})


@app.get("/")
def index():
    return _serve_page("index.html")


@app.get("/admin")
def admin_page():
    return _serve_page("admin.html")


# ═══════════════════════════════════════════════
#  Admin auth API
# ═══════════════════════════════════════════════

class LoginIn(BaseModel):
    password: str


@app.post("/api/admin/login")
async def admin_login(body: LoginIn):
    if not hmac.compare_digest(body.password, config.ADMIN_PASSWORD):
        time.sleep(1)  # 拖慢暴力破解
        raise HTTPException(401, "密码错误")
    resp = JSONResponse({"status": "ok"})
    resp.set_cookie(**_auth_cookie(_sign_token(), config.TOKEN_TTL_SECONDS))
    return resp


@app.post("/api/admin/logout")
def admin_logout():
    resp = JSONResponse({"status": "ok"})
    resp.set_cookie(**_auth_cookie("", 0))
    return resp


@app.get("/api/admin/check")
def admin_check(yuki_admin: str | None = Cookie(default=None)):
    return {"authed": bool(yuki_admin and _verify_token(yuki_admin))}


# ═══════════════════════════════════════════════
#  Upload helpers
# ═══════════════════════════════════════════════

def _classify(ext: str) -> tuple[str, int] | None:
    ext = ext.lower()
    if ext in config.ALLOWED_IMAGE_EXTS:
        return "image", config.MAX_IMAGE_BYTES
    if ext in config.ALLOWED_VIDEO_EXTS:
        return "video", config.MAX_VIDEO_BYTES
    return None


async def _save_upload(file: UploadFile, dest_path, limit: int) -> int:
    """分块流式写盘，超过 limit 抛 413 并清理半成品"""
    size = 0
    try:
        with open(dest_path, "wb") as out:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > limit:
                    raise HTTPException(413, "文件超过大小限制")
                out.write(chunk)
    except HTTPException:
        if os.path.exists(dest_path):
            os.remove(dest_path)
        raise
    except Exception:
        if os.path.exists(dest_path):
            os.remove(dest_path)
        raise HTTPException(500, "写入文件失败")
    return size


def _make_thumbnail(src_path, dest_path) -> tuple[int, int]:
    """生成 800px 缩略图（EXIF 转正 + RGBA 转 RGB），返回 (w, h) 原图尺寸"""
    from PIL import Image, ImageOps
    with Image.open(src_path) as img:
        img = ImageOps.exif_transpose(img)
        width, height = img.size
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGBA")
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")
        img.thumbnail(config.THUMB_MAX_SIZE)
        img.save(dest_path, "JPEG", quality=config.THUMB_QUALITY, progressive=True)
    return width, height


# ═══════════════════════════════════════════════
#  Works API
# ═══════════════════════════════════════════════

@app.get("/api/works")
def list_works():
    return models.list_works()


class WorkEditIn(BaseModel):
    title: str = ""
    description: str = ""


@app.post("/api/works", status_code=201)
async def create_work(
    file: UploadFile = File(...),
    title: str = Form(""),
    description: str = Form(""),
    _: bool = Depends(require_admin),
):
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    kind = _classify(ext)
    if not kind:
        raise HTTPException(400, f"不支持的文件格式: {ext or '(无扩展名)'}")
    media_type, limit = kind

    uid = uuid.uuid4().hex
    rel_path = f"{uid}{ext}"
    abs_path = config.MEDIA_DIR / rel_path
    thumb_rel = None
    width = height = None

    try:
        size = await _save_upload(file, abs_path, limit)
        if size == 0:
            raise HTTPException(400, "文件为空")
        if media_type == "image":
            thumb_rel = f"thumb_{uid}.jpg"
            try:
                width, height = _make_thumbnail(abs_path, config.MEDIA_DIR / thumb_rel)
            except HTTPException:
                raise
            except Exception:
                # 缩略图失败不致命，但图片站点应报错让用户知道
                if os.path.exists(abs_path):
                    os.remove(abs_path)
                raise HTTPException(400, "无法解析图片文件")
        if not title.strip():
            title = os.path.splitext(filename)[0][:80]
        work = models.add_work(
            title=title.strip()[:80], description=description.strip()[:500],
            media_type=media_type, file_path=rel_path, thumb_path=thumb_rel,
            file_size=size, width=width, height=height,
        )
        return work
    except Exception:
        # 清理半成品（含已生成的缩略图）
        if os.path.exists(abs_path):
            os.remove(abs_path)
        if thumb_rel and os.path.exists(config.MEDIA_DIR / thumb_rel):
            os.remove(config.MEDIA_DIR / thumb_rel)
        raise


@app.put("/api/works/{work_id}")
async def update_work(work_id: int, body: WorkEditIn,
                      _: bool = Depends(require_admin)):
    work = models.update_work(work_id, body.title.strip()[:80], body.description.strip()[:500])
    if not work:
        raise HTTPException(404, "作品不存在")
    return work


@app.delete("/api/works/{work_id}")
async def remove_work(work_id: int,
                      _: bool = Depends(require_admin)):
    work = models.delete_work(work_id)
    if not work:
        raise HTTPException(404, "作品不存在")
    for rel in (work["file_path"], work["thumb_path"]):
        if not rel:
            continue
        abs_path = config.MEDIA_DIR / rel
        if os.path.exists(abs_path):
            os.remove(abs_path)
    return {"status": "ok"}


# ═══════════════════════════════════════════════
#  Media serving
# ═══════════════════════════════════════════════

def safe_media_path(rel_path: str) -> str:
    """防目录穿越"""
    abs_path = os.path.realpath(config.MEDIA_DIR / rel_path)
    real_media = os.path.realpath(config.MEDIA_DIR)
    if not abs_path.startswith(real_media + os.sep):
        raise HTTPException(403, "非法的文件路径")
    return abs_path


@app.get("/media/{rel_path:path}")
def serve_media(rel_path: str):
    try:
        abs_path = safe_media_path(rel_path)
    except HTTPException:
        raise
    if not os.path.isfile(abs_path):
        raise HTTPException(404, "文件不存在")
    ext = os.path.splitext(rel_path)[1].lower()
    is_thumb = os.path.basename(rel_path).startswith("thumb_")
    cache = "public, max-age=604800" if is_thumb else "public, max-age=86400"
    return FileResponse(
        abs_path,
        media_type=config.MIME_MAP.get(ext, "application/octet-stream"),
        headers={"Cache-Control": cache},
    )

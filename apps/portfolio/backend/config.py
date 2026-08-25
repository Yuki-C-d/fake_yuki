"""portfolio 站配置 — 路径 / 常量 / 鉴权环境变量"""
import os
from pathlib import Path

# 仓库根目录（config.py 上溯 4 级: backend → portfolio → apps → 根）
BASE_DIR = Path(__file__).resolve().parents[3]

DB_PATH = BASE_DIR / "apps" / "portfolio" / "data" / "portfolio.db"
MEDIA_DIR = BASE_DIR / "apps" / "portfolio" / "media"
FRONTEND_DIR = BASE_DIR / "apps" / "portfolio" / "frontend"

# 鉴权（生产环境由 systemd Environment= 注入）
ADMIN_PASSWORD = os.environ.get("PORTFOLIO_ADMIN_PASSWORD", "yuki-dev-2026")
AUTH_SECRET = os.environ.get("PORTFOLIO_AUTH_SECRET", "yuki-portfolio-dev-secret")
TOKEN_TTL_SECONDS = 7 * 24 * 3600  # 7 天

# 上传限制
MAX_IMAGE_BYTES = 20 * 1024 * 1024   # 20MB
MAX_VIDEO_BYTES = 100 * 1024 * 1024  # 100MB
ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_VIDEO_EXTS = {".mp4", ".webm"}

# 缩略图
THUMB_MAX_SIZE = (800, 800)
THUMB_QUALITY = 82

MIME_MAP = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
}

#配置常量、路径

import os

# 项目根路径 (apps/music/backend/config.py → 上四级)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 音乐文件存放目录
MUSIC_DIR = os.path.join(BASE_DIR, "music-files")

# SQLite 数据库路径
DB_PATH = os.path.join(BASE_DIR, "apps", "music", "data", "music.db")

# 网易云音乐 API 代理地址
NCM_API_BASE_URL = "http://127.0.0.1:3000"

# 支持的音频格式
SUPPORTED_FORMATS = {".flac", ".m4a"}
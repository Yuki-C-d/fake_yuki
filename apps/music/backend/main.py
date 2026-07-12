from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from contextlib import asynccontextmanager, closing
import os
import shutil
import subprocess
from apps.music.backend import config
from apps.music.backend import models
from apps.music.backend import scanner

# MIME 类型映射
MIME_MAP = {
    "flac": "audio/flac",
    "mp3": "audio/mpeg",
    "mp4": "audio/mp4",
    "m4a": "audio/mp4",
    "ogg": "audio/ogg",
    "wav": "audio/wav",
    "aac": "audio/aac",
    "wma": "audio/x-ms-wma",
}


def safe_file_path(rel_path: str) -> str:
    """校验相对路径，防止目录穿越攻击"""
    abs_path = os.path.realpath(os.path.join(config.MUSIC_DIR, rel_path))
    real_music_dir = os.path.realpath(config.MUSIC_DIR)
    if not abs_path.startswith(real_music_dir + os.sep):
        raise ValueError("非法的文件路径")
    return abs_path


@asynccontextmanager
async def lifespan(_app: FastAPI):
    models.init_db()
    scanner.scan()
    yield


app = FastAPI(title="fake_yuki", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    with open("apps/music/frontend/index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read(), headers={"Cache-Control": "no-cache, no-store, must-revalidate"})


@app.get("/test")
def test_page():
    with open("apps/music/frontend/test.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/api/songs")
def list_songs():
    with closing(models.get_connection()) as conn:
        cursor = conn.cursor()
        rows = models.get_all_songs(cursor)

    songs = []
    for row in rows:
        songs.append({
            "id": row[0],
            "title": row[1],
            "artist": row[2],
            "album": row[3],
            "duration": row[4],
            "file_path": row[5],
            "file_format": row[6],
        })
    return songs


@app.get("/api/songs/{song_id}")
def get_song(song_id: int):
    with closing(models.get_connection()) as conn:
        cursor = conn.cursor()
        row = models.get_song_by_id(cursor, song_id)

    if row is None:
        return {"error": "Song not found"}, 404

    return {
        "id": row[0],
        "title": row[1],
        "artist": row[2],
        "album": row[3],
        "duration": row[4],
        "file_path": row[5],
        "file_format": row[6],
        "file_size": row[7],
        "added_at": row[8],
    }


@app.get("/api/stream/{song_id}")
def stream_song(song_id: int):
    with closing(models.get_connection()) as conn:
        cursor = conn.cursor()
        row = models.get_song_by_id(cursor, song_id)

    if row is None:
        return {"error": "Song not found"}, 404

    try:
        abs_path = safe_file_path(row[5])
    except ValueError:
        return {"error": "Forbidden"}, 403

    file_format = (row[6] or "mp3").lower()
    mime_type = MIME_MAP.get(file_format, "application/octet-stream")

    return FileResponse(abs_path, media_type=mime_type, filename=row[1])


# 允许上传的音频格式（含加密格式）
ALLOWED_UPLOAD_EXTENSIONS = {".m4a", ".flac", ".mp3", ".ogg", ".wav", ".aac", ".wma", ".mp4", ".ncm"}

# ncmdump 解密工具路径
NCMDUMP = os.path.join(config.BASE_DIR, "tools", "ncmdump.exe")


def _is_real_audio_file(filepath: str) -> bool:
    """
    检查文件是否为浏览器可播放的真实音频格式。
    排除伪装的 AV3A/MP4 文件（head 为 ftyp/isom 但实际上需要转码）。
    """
    ext = os.path.splitext(filepath)[1].lower()
    # 已知安全格式（浏览器原生支持）
    if ext in {".m4a", ".mp3", ".ogg", ".wav", ".aac"}:
        return True
    # .flac 需要验证：真正的 FLAC 以 "fLaC" 开头，AV3A 以 MP4 ftyp box 开头
    if ext == ".flac":
        try:
            with open(filepath, "rb") as f:
                header = f.read(12)
            # 真 FLAC: 前4字节 "fLaC"
            if header[:4] == b"fLaC":
                return True
            # MP4 容器 (AV3A 伪装): offset 4-8 为 "ftyp"
            if len(header) >= 12 and header[4:8] == b"ftyp":
                return False
        except Exception:
            pass
    # 未识别格式，保守起见返回 True（让 scanner 处理）
    return True


def _find_existing_file(filename: str) -> str | None:
    """在 music/ 目录树中查找同名文件，返回相对路径或 None"""
    for root, dirs, files in os.walk(config.MUSIC_DIR):
        # 跳过 originals 目录
        dirs[:] = [d for d in dirs if d != "originals"]
        if filename in files:
            return os.path.relpath(os.path.join(root, filename), config.MUSIC_DIR)
    return None


@app.post("/api/upload")
async def upload_song(file: UploadFile = File(...)):
    """上传音频文件到 music/ 目录并自动入库。支持 .ncm 自动解密。"""

    # 1. 格式校验
    filename = file.filename or "unknown"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(400, f"不支持的格式: {ext}")

    # 2. 安全文件名（防路径穿越）
    safe_name = os.path.basename(filename)

    # 3. 去重（检查整个 music 目录树，排除 originals）
    existing = _find_existing_file(safe_name)
    if existing:
        raise HTTPException(409, f"文件已存在: {existing}")

    dest = os.path.join(config.MUSIC_DIR, safe_name)

    # 4. 写入磁盘
    try:
        with open(dest, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(500, f"写入文件失败: {e}")

    # 5. NCM 解密（如果是 .ncm 文件）
    scanned_path = dest
    if ext == ".ncm":
        try:
            result = subprocess.run(
                [NCMDUMP, "-o", config.MUSIC_DIR, dest],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode != 0:
                os.remove(dest)
                raise HTTPException(400, f"NCM 解密失败: {result.stderr or result.stdout}")
        except subprocess.TimeoutExpired:
            os.remove(dest)
            raise HTTPException(400, "NCM 解密超时")
        except HTTPException:
            raise
        except Exception as e:
            if os.path.exists(dest):
                os.remove(dest)
            raise HTTPException(500, f"NCM 解密出错: {e}")

        # 解密后删除 .ncm 源文件，找到解密出的文件
        try:
            os.remove(dest)
        except Exception:
            pass

        # 查找解密出的文件（同目录下同主文件名 + flac/mp3/m4a 等）
        base_noext = os.path.splitext(safe_name)[0]
        decrypted_exts = [".flac", ".mp3", ".m4a", ".ogg", ".wav"]
        scanned_path = None
        for try_ext in decrypted_exts:
            candidate = os.path.join(config.MUSIC_DIR, base_noext + try_ext)
            if os.path.exists(candidate):
                scanned_path = candidate
                break

        if scanned_path is None:
            raise HTTPException(400, "NCM 解密完成但未找到输出文件")

    # 6. AV3A 检测：排除伪装的 FLAC 文件
    if not _is_real_audio_file(scanned_path):
        # AV3A/MP4 伪装文件，文件已保存在 music/ 根目录
        # 后台自动启动转码流水线
        filename = os.path.basename(scanned_path)
        convert_script = os.path.join(config.BASE_DIR, "tools", "convert_to_m4a.sh")

        def _run_convert():
            subprocess.Popen(
                ["bash", convert_script],
                cwd=config.BASE_DIR,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        import threading
        threading.Thread(target=_run_convert, daemon=True).start()

        return {
            "status": "converting",
            "filename": filename,
            "message": f"转码已启动，预计 30-50 分钟。完成后自动入库，届时刷新页面即可。",
        }

    # 7. 扫描入库
    result = scanner.scan_single_file(scanned_path)
    if result is None:
        # 无法识别，清理文件
        try:
            os.remove(scanned_path)
        except Exception:
            pass
        raise HTTPException(400, "无法读取音频信息，文件已删除")

    # 8. 返回新歌信息
    return {
        "status": "ok",
        "song": {
            "id": result.get("id"),
            "title": result["title"],
            "artist": result["artist"],
            "album": result["album"],
            "duration": result["duration"],
            "file_path": result["file_path"],
            "file_format": result["file_format"],
            "file_size": result["file_size"],
        },
    }


@app.get("/api/conversions")
def list_conversions():
    """列出正在转码/待转码的 AV3A 文件及其状态"""
    conversions = []
    m4a_dir = os.path.join(config.MUSIC_DIR, "m4a")
    try:
        files = os.listdir(config.MUSIC_DIR)
    except Exception:
        return conversions

    for f in sorted(files):
        fpath = os.path.join(config.MUSIC_DIR, f)
        if not os.path.isfile(fpath):
            continue
        if not f.lower().endswith(".flac"):
            continue
        # 检查是否为 AV3A（非真 FLAC）
        if _is_real_audio_file(fpath):
            continue

        base = os.path.splitext(f)[0]
        av3a_tmp = os.path.join(m4a_dir, f".tmp_{base}.av3a")
        wav_tmp = os.path.join(m4a_dir, f".tmp_{base}.wav")
        m4a_out = os.path.join(m4a_dir, f"{base}.m4a")

        has_m4a = os.path.exists(m4a_out)
        has_wav = os.path.exists(wav_tmp)
        has_av3a = os.path.exists(av3a_tmp)

        if has_m4a:
            status = "done"          # 转码完成，等待扫描入库
        elif has_av3a and has_wav:
            status = "decoding"      # 解码中（av3a_decoder 正在写 WAV）
        elif has_wav:
            status = "encoding"      # 解码完成，ffmpeg 编码中（~30 秒）
        elif has_av3a:
            status = "decoding"      # 提取完成，av3a_decoder 刚启动
        else:
            status = "queued"        # 排队等待中

        conversions.append({
            "filename": f,
            "title": base,
            "status": status,
            "size": os.path.getsize(fpath),
        })

    return conversions


@app.post("/api/scan")
def trigger_scan():
    """手动触发重新扫描音乐目录"""
    try:
        count = scanner.scan()
        return {"status": "ok", "message": f"扫描完成，共处理 {count} 首歌曲"}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500


# ═══════════════════════════════════════
#  歌单 API
# ═══════════════════════════════════════

class PlaylistCreate(BaseModel):
    name: str
    description: str = ""


class PlaylistUpdate(BaseModel):
    name: str


class PlaylistSongAdd(BaseModel):
    song_id: int


class PlaylistReorder(BaseModel):
    song_ids: list[int]


@app.get("/api/playlists")
def list_playlists():
    """获取所有歌单（含歌曲数量）"""
    with closing(models.get_connection()) as conn:
        cursor = conn.cursor()
        rows = models.get_all_playlists(cursor)
    playlists = []
    for row in rows:
        playlists.append({
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "created_at": row[3],
        })
    return playlists


@app.post("/api/playlists")
def create_playlist(body: PlaylistCreate):
    """创建新歌单"""
    name = body.name.strip()
    if not name:
        raise HTTPException(400, "歌单名称不能为空")
    with closing(models.get_connection()) as conn:
        cursor = conn.cursor()
        playlist_id = models.create_playlist(cursor, name, body.description)
        conn.commit()
    return {"id": playlist_id, "name": name, "description": body.description}


@app.put("/api/playlists/{playlist_id}")
def update_playlist(playlist_id: int, body: PlaylistUpdate):
    """更新歌单名称"""
    name = body.name.strip()
    if not name:
        raise HTTPException(400, "歌单名称不能为空")
    with closing(models.get_connection()) as conn:
        cursor = conn.cursor()
        models.update_playlist(cursor, playlist_id, name)
        conn.commit()
    return {"status": "ok"}


@app.delete("/api/playlists/{playlist_id}")
def delete_playlist(playlist_id: int):
    """删除歌单"""
    with closing(models.get_connection()) as conn:
        cursor = conn.cursor()
        models.delete_playlist(cursor, playlist_id)
        conn.commit()
    return {"status": "ok"}


@app.get("/api/playlists/{playlist_id}/songs")
def get_playlist_songs(playlist_id: int):
    """获取歌单内歌曲列表"""
    with closing(models.get_connection()) as conn:
        cursor = conn.cursor()
        rows = models.get_playlist_songs(cursor, playlist_id)
    songs = []
    for row in rows:
        songs.append({
            "id": row[0],
            "title": row[1],
            "artist": row[2],
            "album": row[3],
            "duration": row[4],
            "file_path": row[5],
            "file_format": row[6],
            "file_size": row[7],
            "added_at": row[8],
            "position": row[9],
        })
    return songs


@app.post("/api/playlists/{playlist_id}/songs")
def add_song_to_playlist(playlist_id: int, body: PlaylistSongAdd):
    """添加歌曲到歌单"""
    with closing(models.get_connection()) as conn:
        cursor = conn.cursor()
        # 验证歌曲存在
        song = models.get_song_by_id(cursor, body.song_id)
        if song is None:
            raise HTTPException(404, "歌曲不存在")
        models.add_song_to_playlist(cursor, playlist_id, body.song_id)
        conn.commit()
    return {"status": "ok"}


@app.delete("/api/playlists/{playlist_id}/songs/{song_id}")
def remove_song_from_playlist(playlist_id: int, song_id: int):
    """从歌单移除歌曲"""
    with closing(models.get_connection()) as conn:
        cursor = conn.cursor()
        models.remove_song_from_playlist(cursor, playlist_id, song_id)
        conn.commit()
    return {"status": "ok"}


@app.put("/api/playlists/{playlist_id}/songs/reorder")
def reorder_playlist_songs(playlist_id: int, body: PlaylistReorder):
    """重新排序歌单歌曲"""
    with closing(models.get_connection()) as conn:
        cursor = conn.cursor()
        models.reorder_playlist_songs(cursor, playlist_id, body.song_ids)
        conn.commit()
    return {"status": "ok"}

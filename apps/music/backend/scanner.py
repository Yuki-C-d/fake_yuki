"""遍历 music/ 文件夹 → 识别音频文件 → 用 mutagen 读标签 → 调 models.insert_song() 写入数据库"""

import os
import logging
import mutagen
import sqlite3
from . import models
from .config import MUSIC_DIR, SUPPORTED_FORMATS

logger = logging.getLogger(__name__)


def get_tag(audio, *keys):
    """尝试多个 key 名，返回第一个找到的值"""
    for key in keys:
        try:
            val = audio[key]
            if isinstance(val, list):
                return str(val[0])
            return str(val)
        except (KeyError, IndexError, TypeError):
            continue
    return ""


def _is_real_flac(filepath: str) -> bool:
    """检查 .flac 文件是否为真 FLAC（非 AV3A/MP4 伪装）"""
    try:
        with open(filepath, "rb") as f:
            header = f.read(4)
        return header == b"fLaC"
    except Exception:
        return True  # 读不了就放行，避免误删


def scan_single_file(abs_path: str) -> dict | None:
    """
    扫描单个音频文件，读取元数据并写入数据库。
    返回入库的歌曲数据 dict；如果格式不支持、已存在、或读取失败则返回 None。
    """
    filename = os.path.basename(abs_path)
    rel_path = os.path.relpath(abs_path, MUSIC_DIR)

    # 格式检查
    if not any(filename.lower().endswith(ext) for ext in SUPPORTED_FORMATS):
        return None

    # AV3A 伪装 FLAC 检查
    if filename.lower().endswith(".flac") and not _is_real_flac(abs_path):
        logger.info("跳过 AV3A 伪装 FLAC: %s", filename)
        return None

    # 读取音频元数据
    audio = None
    try:
        audio = mutagen.File(abs_path)
    except Exception:
        logger.warning("mutagen.File 读取失败: %s，尝试 MP4 fallback", filename)

    if audio is None:
        try:
            from mutagen.mp4 import MP4
            audio = MP4(abs_path)
        except Exception:
            logger.warning("MP4 fallback 也失败: %s，跳过", filename)
            return None

    try:
        duration = audio.info.length if audio.info else 0
    except Exception:
        duration = 0

    song_data = {
        "title": get_tag(audio, "title", "\xa9nam"),
        "artist": get_tag(audio, "artist", "\xa9ART"),
        "album": get_tag(audio, "album", "\xa9alb"),
        "duration": duration,
        "file_path": rel_path,
        "file_format": filename.rsplit(".", 1)[-1].lower(),
        "file_size": os.path.getsize(abs_path),
    }

    conn = models.get_connection()
    cursor = conn.cursor()
    try:
        models.insert_song(cursor, song_data)
        conn.commit()
        # 获取自增 ID
        song_data["id"] = cursor.lastrowid
        return song_data
    except sqlite3.IntegrityError:
        logger.info("文件已入库，跳过: %s", filename)
        return None
    except Exception:
        logger.exception("入库失败: %s", filename)
        return None
    finally:
        conn.close()


def scan():
    """
    扫描 MUSIC_DIR 下的所有音频文件，写入数据库。
    返回本次扫描新发现的歌曲数量。
    """
    new_count = 0

    # 排除的目录名（不扫描这些子目录）
    EXCLUDED_DIRS = {"originals"}

    for root, dirs, files in os.walk(MUSIC_DIR):
        # 原地修改 dirs 列表，跳过排除的目录
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for filename in files:
            abs_path = os.path.join(root, filename)
            result = scan_single_file(abs_path)
            if result is not None:
                new_count += 1

    logger.info("扫描完成，新入库 %d 首歌曲", new_count)
    return new_count

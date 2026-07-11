import sqlite3
import os
from .config import DB_PATH

CREATE_SONGS_TABLE = """
CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    artist TEXT,
    album TEXT,
    duration REAL,
    file_path TEXT NOT NULL UNIQUE,
    file_format TEXT NOT NULL,
    file_size INTEGER,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_PLAYLISTS_TABLE = """
CREATE TABLE IF NOT EXISTS playlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_PLAYLIST_SONGS_TABLE = """
CREATE TABLE IF NOT EXISTS playlist_songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    playlist_id INTEGER NOT NULL,
    song_id INTEGER NOT NULL,
    position INTEGER NOT NULL DEFAULT 0,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE,
    UNIQUE (playlist_id, song_id)
)
"""

def init_db():
    #创建 data/ 目录（如果不存在），连上 SQLite，执行建表 SQL
    # 如果 data/ 目录不存在就创建
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    # 打开 music.db（文件不存在会自动新建）
    conn = sqlite3.connect(DB_PATH)
    # 启用外键约束（SQLite 默认关闭，需要每次连接都设置）
    conn.execute("PRAGMA foreign_keys = ON")
    # 执行建表 SQL
    conn.execute(CREATE_SONGS_TABLE)
    conn.execute(CREATE_PLAYLISTS_TABLE)
    conn.execute(CREATE_PLAYLIST_SONGS_TABLE)
    # 保存到磁盘
    conn.commit()
    # 关掉连接
    conn.close()

def get_connection():
    #返回数据库连接（方便其他地方调用）
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def insert_song(cursor, song_data):
    #插入一条歌曲记录（参数用 dict）
    # 从 dict 拆成 tuple
    values = (
        song_data['title'], song_data['artist'], song_data['album'],
        song_data['duration'], song_data['file_path'],
        song_data['file_format'], song_data['file_size']
    )
    #?是占位符，Python 会自动把你的数据填进去，自动防 SQL 注入
    cursor.execute(
        "INSERT OR IGNORE INTO songs  (title, artist, album, duration, file_path, file_format, file_size) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        values
    )

def get_all_songs(cursor):
    #查询所有歌曲
    cursor.execute("SELECT * FROM songs")
    # 拿结果
    return cursor.fetchall()

def get_song_by_id(cursor, song_id):
    #根据 ID 查询歌曲
    # (song_id,) 是单元素 tuple
    cursor.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
    #
    return cursor.fetchone()


# ═══════════════════════════════════════
#  歌单相关
# ═══════════════════════════════════════

def create_playlist(cursor, name, description=""):
    """新建歌单，返回新歌单的 id"""
    cursor.execute(
        "INSERT INTO playlists (name, description) VALUES (?, ?)",
        (name, description)
    )
    return cursor.lastrowid


def get_all_playlists(cursor):
    """查询所有歌单，返回 (id, name, description, created_at) 列表"""
    cursor.execute("SELECT id, name, description, created_at FROM playlists ORDER BY created_at")
    return cursor.fetchall()


def get_playlist_song_count(cursor, playlist_id):
    """查询歌单中的歌曲数量"""
    cursor.execute(
        "SELECT COUNT(*) FROM playlist_songs WHERE playlist_id = ?",
        (playlist_id,)
    )
    return cursor.fetchone()[0]


def update_playlist(cursor, playlist_id, name):
    """重命名歌单"""
    cursor.execute(
        "UPDATE playlists SET name = ? WHERE id = ?",
        (name, playlist_id)
    )


def delete_playlist(cursor, playlist_id):
    """删除歌单（CASCADE 自动清理 playlist_songs）"""
    cursor.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))


def add_song_to_playlist(cursor, playlist_id, song_id):
    """将歌曲加入歌单（自动算 position 为末尾）"""
    cursor.execute(
        "SELECT COALESCE(MAX(position), -1) FROM playlist_songs WHERE playlist_id = ?",
        (playlist_id,)
    )
    next_pos = cursor.fetchone()[0] + 1
    cursor.execute(
        "INSERT OR IGNORE INTO playlist_songs (playlist_id, song_id, position) VALUES (?, ?, ?)",
        (playlist_id, song_id, next_pos)
    )


def remove_song_from_playlist(cursor, playlist_id, song_id):
    """从歌单移除歌曲"""
    cursor.execute(
        "DELETE FROM playlist_songs WHERE playlist_id = ? AND song_id = ?",
        (playlist_id, song_id)
    )


def get_playlist_songs(cursor, playlist_id):
    """查询歌单内所有歌曲（JOIN songs 获取完整元数据），按 position 排序"""
    cursor.execute("""
        SELECT s.id, s.title, s.artist, s.album, s.duration,
               s.file_path, s.file_format, s.file_size, s.added_at,
               ps.position, ps.added_at
        FROM playlist_songs ps
        JOIN songs s ON s.id = ps.song_id
        WHERE ps.playlist_id = ?
        ORDER BY ps.position
    """, (playlist_id,))
    return cursor.fetchall()


def reorder_playlist_songs(cursor, playlist_id, song_ids):
    """批量更新歌曲在歌单中的顺序"""
    for pos, song_id in enumerate(song_ids):
        cursor.execute(
            "UPDATE playlist_songs SET position = ? WHERE playlist_id = ? AND song_id = ?",
            (pos, playlist_id, song_id)
        )
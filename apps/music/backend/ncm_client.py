"""NeteaseCloudMusicApi 异步客户端"""

import httpx
from apps.music.backend import config


class NCMClient:
    """封装 NeteaseCloudMusicApi (127.0.0.1:3000) 的异步代理。

    单实例复用 cookie —— 扫码登录后自动保持会话。
    """

    def __init__(self, base_url: str = ""):
        self.base_url = base_url or config.NCM_API_BASE_URL
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url, timeout=httpx.Timeout(15.0)
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    # ── Auth ──────────────────────────────────────────

    async def get_login_status(self) -> dict:
        r = await self.client.get("/login/status")
        return r.json()

    async def get_qr_key(self) -> dict:
        r = await self.client.get("/login/qr/key")
        return r.json()

    async def create_qr_code(self, key: str) -> dict:
        r = await self.client.get(
            "/login/qr/create", params={"key": key, "qrimg": "true"}
        )
        return r.json()

    async def check_qr_login(self, key: str) -> dict:
        r = await self.client.get("/login/qr/check", params={"key": key})
        return r.json()

    async def logout(self) -> dict:
        r = await self.client.get("/logout")
        return r.json()

    # ── User Data ─────────────────────────────────────

    async def get_user_playlists(self, uid: str) -> dict:
        r = await self.client.get("/user/playlist", params={"uid": uid})
        return r.json()

    async def get_playlist_tracks(self, playlist_id: str) -> dict:
        r = await self.client.get(
            "/playlist/track/all", params={"id": playlist_id}
        )
        return r.json()

    # ── Search ────────────────────────────────────────

    async def search(self, keywords: str, page: int = 1, limit: int = 30) -> dict:
        offset = (page - 1) * limit
        r = await self.client.get(
            "/cloudsearch",
            params={"keywords": keywords, "offset": offset, "limit": limit},
        )
        return r.json()

    # ── Song ──────────────────────────────────────────

    async def get_song_url(self, song_id: str, level: str = "standard") -> dict:
        """level: standard / higher / exhigh / lossless / hires"""
        r = await self.client.get(
            "/song/url/v1", params={"id": song_id, "level": level}
        )
        return r.json()

    async def get_song_detail(self, song_id: str) -> dict:
        r = await self.client.get("/song/detail", params={"ids": song_id})
        return r.json()

    async def get_likelist(self, uid: str) -> dict:
        r = await self.client.get("/likelist", params={"uid": uid})
        return r.json()

    async def playlist_track_add(self, pid: str, ids: str, op: str = "add") -> dict:
        """添加/移除歌曲 op=add|del, pid=歌单id, ids=歌曲id(逗号分隔)"""
        r = await self.client.get(
            "/playlist/track/add",
            params={"op": op, "pid": pid, "ids": ids},
        )
        return r.json()

    async def get_lyric(self, song_id: str) -> dict:
        r = await self.client.get("/lyric", params={"id": song_id})
        return r.json()

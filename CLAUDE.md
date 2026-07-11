# fake_yuki

此方的个人网站项目集合。

## 目录结构

```
apps/music/     - 🎵 音乐播放器 (FastAPI + SQLite)
apps/nav/       - 🔗 导航站 (GitHub Pages → fake-star.xyz)
server/         - ☁️ ECS + frp 服务器配置
music-files/    - 🎵 音乐文件 (不入 git)
tools/          - 🔧 转码工具
docs/           - 📄 项目文档
```

## 启动命令

```bash
cd D:\fake_yuki
python -m uvicorn apps.music.backend.main:app --host 0.0.0.0 --port 8080
```

## 关键配置

- **服务器**: 阿里云 ECS 8.166.119.185 (Ubuntu 22.04)
- **SSH**: `server/keys/id_ed25519`
- **frpc**: `server/frpc/frpc.toml` (开机自启)
- **外网**: `http://8.166.119.185:8080`

## 查看项目

- **`docs/PROJECT.md`** — 📋 项目手册（总文档，含所有模块、API、时间线、命令）
- `docs/SERVER.md` — 服务器详细文档
- `docs/archive/` — 旧版文档（仅参考）
- GitHub: `Yuki-C-d/fake_yuki`

## 记忆文件

- `.claude/memory/MEMORY.md` — 项目记忆索引

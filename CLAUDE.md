# music-vault

此方的个人网站项目，包含音乐播放器、导航站等模块。

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
cd D:\music-vault
python -m uvicorn apps.music.backend.main:app --host 0.0.0.0 --port 8080
```

## 关键配置

- **服务器**: 阿里云 ECS 8.166.119.185 (Ubuntu 22.04)
- **SSH**: `server/keys/id_ed25519`
- **frpc**: `server/frpc/frpc.toml` (开机自启)
- **外网**: `http://8.166.119.185:8080`

## 查看进度

- `docs/PROGRESS.md` — 开发进度和踩坑记录
- `docs/README.md` — 项目方案和 API 设计
- `docs/DEV_GUIDE.html` — 操作手册
- `docs/SERVER.md` — 服务器文档

# fake_yuki

此方的个人网站项目集合。

## 目录结构

```
apps/home/      - 🏠 个人主站（Hero + 功能卡片 + 随手记）
apps/music/     - 🎵 音乐播放器（本地+网易云双源，yuki_风格）
apps/bookmarks/ - 🔗 书签站 (ECS :8081)
yuki_风格/      - 🎨 全站视觉设计规范（利兹与青鸟 × 玻璃童话）
server/         - ☁️ ECS + frp 服务器配置
music-files/    - 🎵 音乐文件 (不入 git)
tools/          - 🔧 转码工具
docs/           - 📄 项目文档
```

## 启动命令

```bash
# 音乐站
cd D:\fake_yuki
python -m uvicorn apps.music.backend.main:app --host 0.0.0.0 --port 8080

# 主站（本地预览）
cd D:\fake_yuki\apps\home
python -m http.server 3000
```

## 关键配置

- **服务器**: 阿里云 ECS 8.166.119.185 (Ubuntu 22.04)
- **SSH**: `server/keys/id_ed25519`
- **ECS 服务**: 
  - `fake-yuki-music` — FastAPI :8080
  - `ncmapi` — NeteaseCloudMusicApi :3000 (网易云代理)
  - `frps` — frp 服务端
- **外网**: `http://8.166.119.185:8080`

## 查看项目

- **`docs/PROJECT.md`** — 📋 项目手册（总文档，含所有模块、API、时间线、命令）
- `docs/SERVER.md` — 服务器详细文档
- `docs/archive/` — 旧版文档（仅参考）
- GitHub: `Yuki-C-d/fake_yuki`

## 记忆文件

- `.claude/memory/MEMORY.md` — 项目记忆索引

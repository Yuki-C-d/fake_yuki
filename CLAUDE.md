# fake_yuki

此方的个人网站项目集合。（最后更新: 2026-08-25）

## 目录结构

```
apps/home/      - 🏠 个人主站（Hero + 功能卡片 + 随手记）
apps/music/     - 🎵 音乐播放器（本地+网易云双源，yuki_风格，含 Chrome 扩展）
apps/bookmarks/ - 🔗 书签站 (ECS :8081)
apps/portfolio/ - 🖼️ 作品集（照片+短视频，密码管理页，ECS :8082）
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

# 书签站
cd D:\fake_yuki
python -m uvicorn apps.bookmarks.backend.main:app --host 0.0.0.0 --port 8081

# 作品集
cd D:\fake_yuki
python -m uvicorn apps.portfolio.backend.main:app --host 0.0.0.0 --port 8082

# 主站（本地预览）
cd D:\fake_yuki\apps\home
python -m http.server 3000
```

## 关键配置

- **服务器**: 阿里云 ECS 8.166.119.185 (Ubuntu 22.04)
- **SSH**: `server/keys/id_ed25519`
- **ECS 服务**: 
  - `caddy` — 反向代理 + HTTPS（80/443）
  - `fake-yuki-music` — FastAPI :8080（127.0.0.1）
  - `fake-star-nav` — FastAPI 书签 :8081（127.0.0.1）
  - `fake-star-portfolio` — FastAPI 作品集 :8082（127.0.0.1）
  - `ncmapi` — NeteaseCloudMusicApi :3000（127.0.0.1）
  - `frps` — frp 服务端
- **外网**: `https://fake-star.xyz` / `https://music.fake-star.xyz` / `https://bookmarks.fake-star.xyz` / `https://portfolio.fake-star.xyz`
- **作品集管理密码**: `systemctl edit fake-star-portfolio` → `PORTFOLIO_ADMIN_PASSWORD`（本地开发默认 `yuki-dev-2026`）

## 查看项目

- **`docs/PROJECT.md`** — 📋 项目手册（总文档，含所有模块、API、时间线、命令）
- `docs/SERVER.md` — 服务器详细文档
- `docs/archive/` — 旧版文档（仅参考）
- GitHub: `Yuki-C-d/fake_yuki`

## 记忆文件

- `C:\Users\31848\.claude\projects\D--fake-yuki\memory\MEMORY.md` — 项目记忆索引

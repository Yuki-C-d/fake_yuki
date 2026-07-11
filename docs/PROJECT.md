# fake_yuki 项目手册

> 个人网站项目集合 — 此方 & Yuki ❄️  
> 最后更新: 2026-07-11

---

## 项目地图

| 模块 | 路径 | 状态 | 说明 |
|------|------|------|------|
| 🎵 音乐播放器 | `apps/music/` | ✅ 运行中 | 自建音乐云，浏览器听歌 |
| 🔗 导航站 | `apps/nav/` | ✅ 已上线 | fake-star.xyz，存常用链接 |
| ☁️ 服务器 | `server/` | ✅ 运行中 | 阿里云 ECS + frp 内网穿透 |
| 🔧 工具集 | `tools/` | ✅ | AV3A 转码 / ncmdump 解密 |

**启动命令**: `cd D:\fake_yuki && python -m uvicorn apps.music.backend.main:app --host 0.0.0.0 --port 8080`

---

## 🎵 音乐播放器

### 基本信息

| 项目 | 详情 |
|------|------|
| 后端 | FastAPI (Python 3.13) |
| 数据库 | SQLite (`apps/music/data/music.db`) |
| 前端 | 纯 HTML + JS（暗色 Spotify 风格） |
| 本地地址 | `http://localhost:8080` |
| 外网地址 | `http://8.166.119.185:8080` |
| API 文档 | `http://localhost:8080/docs` |

### 数据库

**songs 表**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增 |
| title | TEXT | 歌名 |
| artist | TEXT | 歌手 |
| album | TEXT | 专辑 |
| duration | REAL | 时长（秒） |
| file_path | TEXT UNIQUE | 相对路径 |
| file_format | TEXT | m4a / flac / mp3 |
| file_size | INTEGER | 字节 |
| added_at | TIMESTAMP | 入库时间 |

**playlists 表** — id / name / description / created_at

**playlist_songs 表** — id / playlist_id (FK) / song_id (FK) / position

### API 端点 (16 个)

**歌曲**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/songs` | 全部歌曲 |
| GET | `/api/songs/{id}` | 单曲详情 |
| GET | `/api/stream/{id}` | 音频流 (Range 支持) |
| POST | `/api/upload` | 上传 (支持 .ncm 解密 + AV3A 检测) |
| POST | `/api/scan` | 手动扫描入库 |
| GET | `/api/conversions` | 转码进度 |

**歌单**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/playlists` | 全部歌单 |
| POST | `/api/playlists` | 创建歌单 |
| PUT | `/api/playlists/{id}` | 重命名 |
| DELETE | `/api/playlists/{id}` | 删除 |
| GET | `/api/playlists/{id}/songs` | 歌单内歌曲 |
| POST | `/api/playlists/{id}/songs` | 添加歌曲 |
| DELETE | `/api/playlists/{id}/songs/{sid}` | 移除歌曲 |
| PUT | `/api/playlists/{id}/songs/reorder` | 排序 |

**支持的音频格式**: `.m4a` `.mp3` `.flac` `.ogg` `.wav` `.aac`

### 关键代码文件

| 文件 | 作用 |
|------|------|
| `apps/music/backend/main.py` | FastAPI 入口，16 个路由 |
| `apps/music/backend/models.py` | SQLite 操作，3 张表，外键级联 |
| `apps/music/backend/scanner.py` | 遍历 music-files/ → mutagen 读标签 → 入库 |
| `apps/music/backend/config.py` | BASE_DIR / MUSIC_DIR / DB_PATH |
| `apps/music/frontend/index.html` | 播放器 + 上传 + 歌单 + 搜索 + 右键菜单 |

### 已实现功能

- 播放器：切歌、搜索、键盘快捷键、进度条拖动、暗色主题
- 上传：拖拽/点击、去重、NCM 自动解密
- 转码：AV3A 自动检测、后台转码队列、完成后自动入库
- 歌单：创建/重命名/删除、右键添加/移除、排序
- 安全：路径穿越防护 (`safe_file_path`)、数据库连接管理 (`closing()`)

---

## 🔗 导航站

| 项目 | 详情 |
|------|------|
| 域名 | `https://fake-star.xyz` |
| 部署 | GitHub Pages (`Yuki-C-d/nav-site`) |
| 代码 | `apps/nav/index.html` (独立 Git 仓库) |
| 功能 | 常用网站链接导航，暗色主题 |

### 更新方法

```bash
cd D:\fake_yuki\apps\nav
# 编辑 index.html
git add . && git commit -m "更新链接" && git push
# 1 分钟内自动部署到 fake-star.xyz
```

### DNS 配置

阿里云 DNS: `@` CNAME → `yuki-c-d.github.io`, `www` CNAME → `yuki-c-d.github.io`

---

## ☁️ 服务器

### ECS 信息

| 项目 | 详情 |
|------|------|
| 厂商 | 阿里云 ECS 经济型 e 实例 |
| 公网 IP | `8.166.119.185` |
| 配置 | 2核2G / 40G / 3Mbps |
| 系统 | Ubuntu 22.04.5 LTS |
| 地域 | 华南 广州 |
| 价格 | 99 元/年 (续费同价至 2030) |

### 登录

```bash
ssh -i D:\fake_yuki\server\keys\id_ed25519 root@8.166.119.185
```

### 端口与安全组

| 端口 | 用途 |
|------|------|
| 22 | SSH |
| 7000 | frp 控制 |
| 7500 | frp 面板 (admin / musicvault2026) |
| 8080 | 音乐站 |
| 18790 | OpenClaw WebSocket |

### frp 内网穿透

```
外网 → 8.166.119.185:8080 → frps (ECS) → frpc (本地) → localhost:8080
```

| 组件 | 位置 | 管理 |
|------|------|------|
| frps | ECS `/opt/frp/` | `systemctl {start\|stop\|restart\|status} frps` |
| frpc | 本地 `server/frpc/` | 开机自启 (`server/start-frpc.bat`) |

**frp 面板**: `http://8.166.119.185:7500`

### 机房软件

| 软件 | 版本 | 路径 |
|------|------|------|
| Node.js | v24.16.0 | `/usr/local/node-v24.16.0-linux-x64/` |
| npm | 11.13.0 | 源: `registry.npmmirror.com` |
| Python | 3.10.12 | 系统自带 |

### Node.js 安装（国内镜像）

```bash
cd /tmp && curl -L -o node.tar.xz "https://npmmirror.com/mirrors/node/v<VERSION>/node-v<VERSION>-linux-x64.tar.xz"
cd /usr/local && tar -xJf /tmp/node.tar.xz
ln -sf /usr/local/node-v<VERSION>-linux-x64/bin/{node,npm,npx} /usr/local/bin/
npm config set registry https://registry.npmmirror.com
```

---

## 🚀 操作速查

### 日常

| 操作 | 命令 |
|------|------|
| 启动音乐服务 | `cd D:\fake_yuki && python -m uvicorn apps.music.backend.main:app --host 0.0.0.0 --port 8080` |
| 手动扫描歌曲 | `curl -X POST http://127.0.0.1:8080/api/scan` |
| 查看曲库 | `curl http://127.0.0.1:8080/api/songs` |

### frp

| 操作 | 命令 | 在哪跑 |
|------|------|--------|
| 启动 frpc | `D:\fake_yuki\server\frpc\frpc.exe -c D:\fake_yuki\server\frpc\frpc.toml` | 本地 |
| frps 状态 | `systemctl status frps` | ECS |
| 重启 frps | `systemctl restart frps` | ECS |
| 查看隧道 | `http://8.166.119.185:7500` | 浏览器 |

### AV3A 转码

| 操作 | 命令 |
|------|------|
| 批量转码 | `bash tools/convert_to_m4a.sh`（需要在 Git Bash 下跑） |

**流水线**: Python 提取 mdat box → av3a_decoder.exe (30-50分/首) → ffmpeg → M4A (AAC 256k)

---

## 📅 开发时间线

| 日期 | 里程碑 |
|------|--------|
| **2026-06-30** | 项目启动，命名 music-vault，技术选型 FastAPI + SQLite |
| **2026-07-01** | 后端三大模块完工 (config / models / scanner) |
| **2026-07-02** | MVP 跑通，FastAPI + HTML 播放器上线，发现测试曲是 AV3A |
| **2026-07-04** | 代码审查 + 安全加固（路径穿越 / 连接泄漏 / 前端错误处理） |
| **2026-07-05** | AV3A 转码流水线完工，3 首测试曲转 M4A 可播 |
| **2026-07-06** | Phase 2 完工（切歌/搜索/UI/Range），网页上传 + 自动转码 |
| **2026-07-07** | 歌单管理上线（8 个 API + 侧边栏 + 右键菜单），Phase 3 基本完工 |
| **2026-07-10** | 阿里云 ECS 购入，frp 内网穿透上线，外网可访问 |
| **2026-07-11** | OpenClaw ECS node 部署，导航站 fake-star.xyz 上线，项目重命名 fake_yuki + 模块化 + 推 GitHub |

### 下一步

| 优先级 | 事项 |
|--------|------|
| ⭐ | 加歌（往 music-files/m4a/ 放文件 → POST /api/scan） |
| ⭐ | 用户认证 (JWT) |
| ⭐⭐ | 移动端适配 |
| ⭐⭐ | 域名备案 + 绑到 ECS（就不用记 IP 了） |
| ⭐⭐⭐ | 音质切换 (FLAC ↔ M4A) |
| 💤 | Agent 接入接口（设计方案已有，功能稳定后实施） |

---

## ⚠️ 注意事项

1. **frpc.exe 被 Defender 误杀** — 已将 `D:\fake_yuki` 加入排除项
2. **音乐文件不入 Git** — `music-files/` 在 `.gitignore` 中
3. **服务器凭证不入 Git** — `server/server.env` 和 `server/keys/` 在 `.gitignore` 中
4. **导航站独立仓库** — `apps/nav/` 有自己的 Git 仓库，不跟主仓库混合
5. **换设备恢复** — `git clone git@github.com:Yuki-C-d/fake_yuki.git` + 拷入 music-files/ + tools/*.exe + server/keys/

---

## 📄 详细文档

| 文档 | 内容 | 位置 |
|------|------|------|
| 旧 README | music-vault 原始方案 | `docs/archive/README-old.md` |
| 旧 PROGRESS | 开发日记（踩坑记录） | `docs/archive/PROGRESS-old.md` |
| 旧 DEV_GUIDE | 操作手册（详细版） | `docs/archive/DEV_GUIDE-old.html` |
| 服务器文档 | ECS/frp 详细配置 | `docs/SERVER.md`（保留不归档） |

---

*本文档是 fake_yuki 项目手册的唯一入口。加新模块时，在"项目地图"中加一行，在下方加对应章节。*

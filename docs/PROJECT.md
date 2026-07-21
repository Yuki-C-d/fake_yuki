# fake_yuki 项目手册

> 个人网站项目集合 — 此方 & Yuki ❄️  
> 最后更新: 2026-07-21

---

## 项目地图

| 模块 | 路径 | 状态 | 说明 |
|------|------|------|------|
| 🏠 **个人主站** | `apps/home/` | 🔨 骨架搭建 | 站点入口，Hero + 功能卡片 + 随手记 |
| 🎵 音乐播放器 | `apps/music/` | ✅ 运行中 | 自建音乐云，浏览器听歌 |
| 🔗 导航站 | `apps/nav/` | ✅ 已上线 | fake-star.xyz，存常用链接（将迁至子域名） |
| 🎨 **设计系统** | `yuki_风格/` | ✅ **定稿** | **全站视觉规范，所有功能站风格统一依据** |
| ☁️ 服务器 | `server/` | ✅ 运行中 | 阿里云 ECS + frp 内网穿透 |
| 🔧 工具集 | `tools/` | ✅ | AV3A 转码 / ncmdump 解密 |

**启动命令**: `cd D:\fake_yuki && python -m uvicorn apps.music.backend.main:app --host 0.0.0.0 --port 8080`

---

## 🎨 设计系统（v1 已定稿）

> **所有功能站视觉风格统一依据，开发新站前必须先参考此文件夹。**

| 文件 | 说明 | 用途 |
|------|------|------|
| `yuki_风格/STYLE_GUIDE.md` | 设计规范文档 | Claude Code 开发参考 |
| `yuki_风格/预览.html` | 视觉预览页面 | 浏览器打开看实际效果 |

### 设计语言

- **风格：** 利兹与青鸟 × 蜡笔颗粒感 × 玻璃童话
- **配色：** 青蓝为基底 + 夕阳橙红/草绿/麦秆黄暖色点缀
- **纹理：** SVG 噪点颗粒，模拟画纸质感
- **字体：** Noto Serif SC / 仿宋
- **组件：** 毛玻璃卡片 (backdrop-filter blur) + 极简按钮
- **背景：** Pixiv 画师插画固定壁纸，半透明内容层
- **装饰主题：** 青鸟 + 勿忘我（素材待添加）

> ⚠️ **重要：** 以后新增任何功能站（音乐、导航、摄影等），前端设计必须先参考 `yuki_风格/` 下的规范，确保整体风格统一。

---

## 🎵 音乐播放器

### 基本信息

| 项目 | 详情 |
|------|------|
| 后端 | FastAPI (Python 3.13) |
| 数据库 | SQLite (`apps/music/data/music.db`) |
| 前端 | 纯 HTML + JS（yuki_风格 玻璃童话） |
| 音源 | 本地文件 + 网易云音乐（扫码登录流播放） |
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

### API 端点 (27 个)

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

**网易云代理**（通过 NeteaseCloudMusicApi 侧车，ECS :3000）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/ncm/status` | 登录状态 |
| GET | `/api/ncm/qr/key` | 获取扫码 key |
| GET | `/api/ncm/qr/create` | 生成二维码 |
| POST | `/api/ncm/qr/check` | 轮询扫码结果 |
| POST | `/api/ncm/logout` | 退出登录 |
| GET | `/api/ncm/playlists` | 用户歌单 |
| GET | `/api/ncm/playlist/{id}/tracks` | 歌单歌曲 |
| GET | `/api/ncm/search` | 搜索 |
| GET | `/api/ncm/song/{id}/url` | 获取播放链接 |
| GET | `/api/ncm/song/{id}/detail` | 歌曲详情 |
| GET | `/api/ncm/song/{id}/lyric` | 歌词 |

### 关键代码文件

| 文件 | 作用 |
|------|------|
| `apps/music/backend/main.py` | FastAPI 入口，27 个路由 |
| `apps/music/backend/ncm_client.py` | 网易云 API 异步代理（httpx） |
| `apps/music/backend/models.py` | SQLite 操作，3 张表，外键级联 |
| `apps/music/backend/scanner.py` | 遍历 music-files/ → mutagen 读标签 → 入库 |
| `apps/music/backend/config.py` | BASE_DIR / MUSIC_DIR / DB_PATH / NCM_API_BASE_URL |
| `apps/music/frontend/index.html` | yuki_风格 SPA：双源切换 + 播放器 + 歌单 + 上传 |

### 已实现功能

- 播放器：切歌、搜索、键盘快捷键、底部浮动进度条、yuki_风格玻璃童话 UI
- 统一播放器：本地+网易云混合展示，无标签切换
- 网易云：扫码登录 → 歌单浏览 → CDN 流播放（不下载）
- 上传：拖拽/点击、去重、NCM 自动解密
- 转码：AV3A 自动检测（仅本地 Windows 支持）
- 歌单：创建/重命名/删除、＋按钮统一添加/移除、排序
- 安全：路径穿越防护 (`safe_file_path`)、数据库连接管理 (`closing()`)
- PWA：manifest + service worker，手机可安装

---

## 🏠 个人主站

| 项目 | 详情 |
|------|------|
| 域名 | `https://fake-star.xyz`（备案后上线） |
| 代码 | `apps/home/index.html` |
| 风格 | yuki_风格（毛玻璃 / 噪点 / 青鸟 / 勿忘我） |
| 状态 | 🔨 骨架搭建中 |

### 结构

```
Hero 全屏壁纸 → 功能站入口卡片（3 栏毛玻璃）→ 随手记 → Footer
```

### 预览

```bash
cd D:\fake_yuki\apps\home
python -m http.server 3000
# 浏览器打开 http://localhost:3000
```

---

## 🔗 导航站（书签）

| 项目 | 详情 |
|------|------|
| 域名 | `https://fake-star.xyz` |
| 部署 | GitHub Pages (`Yuki-C-d/nav-site`) |
| 代码 | `apps/nav/index.html` (独立 Git 仓库) |
| 功能 | 常用网站链接导航，yuki_风格毛玻璃 |
| 计划 | 备案后迁至 `nav.fake-star.xyz` 子域名 |

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
外网 → 8.166.119.185:8080 → FastAPI 直跑 (ECS)
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
| 启动音乐服务（本地） | `cd D:\fake_yuki && python -m uvicorn apps.music.backend.main:app --host 0.0.0.0 --port 8080` |
| 手动扫描歌曲 | `curl -X POST http://127.0.0.1:8080/api/scan` |
| 查看曲库 | `curl http://127.0.0.1:8080/api/songs` |

### ECS 服务管理

| 操作 | 命令 | 在哪跑 |
|------|------|--------|
| 查看音乐站状态 | `systemctl status fake-yuki-music` | ECS |
| 重启音乐站 | `systemctl restart fake-yuki-music` | ECS |
| 查看 NCM API 状态 | `systemctl status ncmapi` | ECS |
| 重启 NCM API | `systemctl restart ncmapi` | ECS |
| 音乐站日志 | `journalctl -u fake-yuki-music -f` | ECS |

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
| **2026-07-12** | yuki_风格 设计系统定稿（利兹与青鸟 × 蜡笔颗粒感 × 玻璃童话） |
| **2026-07-13** | 个人主站骨架搭建（Hero + 功能卡片 + 随手记），yuki_风格 首次落地 |
| **2026-07-14** | 音乐站重构：yuki_风格前端 + 网易云双音源（NeteaseCloudMusicApi侧车 + 扫码登录流播放），PWA 支持，ECS 全栈部署 |
| **2026-07-15** | Bug 修复：歌单右键菜单完善（添加/移除/重命名/删除）、网易云登录修复 |
| **2026-07-16** | 统一搜索（本地+NCM 双源，本地优先）；收藏菜单重构（＋按钮统一交互）；NCM 收藏到账号歌单；参考 Mineradio 架构优化 |
| **2026-07-20** | 合并标签页为统一播放器；搜索缓存+播放修复；底部浮动进度条（yuki_风格）；frp 架构文档修正 |
| **2026-07-21** | ECS 宕机恢复；书签站 yuki_风格重设计；主站+书签+音乐三站风格统一 |

### 下一步

| 优先级 | 事项 |
|--------|------|
| ⭐ | 域名备案 → 绑 DNS，主站上线 fake-star.xyz |
| ⭐ | 导航站迁至 `nav.fake-star.xyz` + yuki_风格 重构 |
| ⭐⭐ | 随手接后端（碎碎念 + 图片上传） |
| ⭐⭐ | 移动端适配 |
| ⭐⭐ | 音乐站绑域名 + yuki_风格 重构 |
| ⭐⭐⭐ | 摄影站搭建 |
| ⭐⭐⭐ | 音质切换 (FLAC ↔ M4A) |
| 💤 | 用户认证 / Agent 接入 |

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

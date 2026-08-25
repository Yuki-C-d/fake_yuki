# fake_yuki 项目手册

> 个人网站项目集合 — 此方 & Yuki ❄️  
> 最后更新: 2026-08-25

---

## 项目地图

| 模块 | 路径 | 状态 | 说明 |
|------|------|------|------|
| 🏠 **个人主站** | `apps/home/` | ✅ 运行中 | 站点入口，Hero + 功能卡片 + 随手记 |
| 🎵 音乐播放器 | `apps/music/` | ✅ 运行中 | 自建音乐云 + Chrome 扩展迷你面板 |
| 🔌 音乐扩展 | `apps/music/extension/` | ✅ 运行中 | Chrome MV3，工具栏弹出控制面板 |
| 🔗 书签站 | `apps/bookmarks/` | ✅ 运行中 | ECS :8081 + SQLite，标签分类+增删改 |
| 🖼️ 作品集 | `apps/portfolio/` | ✅ 运行中 | ECS :8082 + SQLite，照片/短视频 + 密码管理页 |
| 🎨 **设计系统** | `yuki_风格/` | ✅ **定稿** | **全站视觉规范，所有功能站风格统一依据** |
| ☁️ 服务器 | `server/` | ✅ 运行中 | 阿里云 ECS + Caddy 反代 + HTTPS |
| 🔧 工具集 | `tools/` | ✅ | AV3A 转码 / ncmdump 解密 |

**域名**: `https://fake-star.xyz`（ICP 已备案）
**子域名**: `music.fake-star.xyz` / `bookmarks.fake-star.xyz` / `portfolio.fake-star.xyz`

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
| 外网地址 | `https://music.fake-star.xyz` |
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
- 插队播放：`[＋]` 菜单"下一首播放"，`nextQueue` FIFO 队列，播完后自动回到原歌单继续

---

## 🏠 个人主站

| 项目 | 详情 |
|------|------|
| 域名 | `https://fake-star.xyz`（ICP 已备案） |
| 代码 | `apps/home/index.html` |
| 风格 | yuki_风格（毛玻璃 / 噪点 / 青鸟 / 勿忘我） |
| 状态 | ✅ 已上线（ECS + Caddy 静态托管） |

### 结构

```
Hero 全屏壁纸 → 功能站入口卡片（3 栏毛玻璃）→ 随手记 → Footer
```

### 访问

```
https://fake-star.xyz        ← 主站
https://music.fake-star.xyz   ← 音乐站（弹出窗）
https://bookmarks.fake-star.xyz ← 书签站
https://portfolio.fake-star.xyz ← 作品集
```

---

## 🔗 书签站

| 项目 | 详情 |
|------|------|
| 地址 | `https://bookmarks.fake-star.xyz` |
| 后端 | FastAPI + SQLite (`apps/bookmarks/data/nav.db`) |
| 前端 | yuki_风格 SPA：标签页切换 + fadeSlide 动画 + 增删改 |
| 部署 | ECS systemd `fake-star-nav`，开机自启 |
| 功能 | 分类管理书签，多设备同步 |

### 组件规范（新增）

| 组件 | 位置 | 说明 |
|------|------|------|
| 标签页 `.tab` | 顶部水平 tab 栏 | 圆角 30px，非激活半透明，激活态 `--c-blue` 实色 |
| 添加按钮 `.btn-add-link` | 卡片底部居中 | 虚线边框 + 半透明底，hover 实色 |
| 链接列表 `.link-item` | 毛玻璃行 | 编辑/删除操作按钮、emoji 图标 |
| 弹窗 `.modal-overlay/.modal-box` | 居中浮动 | 毛玻璃底 + backdrop-filter blur(6px) |
| 过渡动画 `fadeSlide` | 标签切换 | 0.3s，opacity 0→1 + translateY(8px→0) |

### 更新方法

编辑书签直接在网页上操作（增删改），无需改代码。部署更新：

```bash
cd D:\fake_yuki
scp apps/bookmarks/backend/*.py apps/bookmarks/frontend/* root@8.166.119.185:/opt/fake_yuki/apps/bookmarks/
ssh root@8.166.119.185 "systemctl restart fake-star-nav"
```

---

## 🖼️ 作品集

| 项目 | 详情 |
|------|------|
| 地址 | `https://portfolio.fake-star.xyz`（面试直接发这个链接） |
| 后端 | FastAPI + SQLite (`apps/portfolio/data/portfolio.db`) |
| 前端 | yuki_风格 作品墙 + lightbox + 密码管理页 (`/admin`) |
| 部署 | ECS systemd `fake-star-portfolio` (:8082)，开机自启 |
| 功能 | 照片(jpg/png/webp ≤20MB) + 短视频(mp4/webm ≤100MB)，拖拽上传、缩略图、编辑描述、删除 |

### 架构

- **公开**：作品墙（懒加载缩略图 + lightbox 原图/视频），无需登录
- **管理**：`/admin` 密码登录（HMAC cookie 7 天），上传队列带进度条
- **存储**：UUID 文件名，media/ 原图 + thumb_ 缩略图；media/ 与 data/ 均不入 git
- **鉴权**：`PORTFOLIO_ADMIN_PASSWORD` 环境变量（ECS systemd 注入），密码错误 sleep 1s 防爆破
- **安全**：目录穿越防护、扩展名白名单、分块流式上传超限清理

### API 端点

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| GET | `/` | — | 公开作品墙 |
| GET | `/admin` | — | 管理页 |
| GET | `/api/works` | — | 作品列表 |
| POST | `/api/admin/login` | — | 密码登录 → cookie |
| POST | `/api/admin/logout` | cookie | 退出 |
| GET | `/api/admin/check` | — | 登录状态 |
| POST | `/api/works` | ✅ | multipart 上传（title+description+file） |
| PUT | `/api/works/{id}` | ✅ | 编辑标题/描述 |
| DELETE | `/api/works/{id}` | ✅ | 删除（连文件一起） |
| GET | `/media/{path}` | — | 媒体文件（Range 支持视频拖动） |

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
| 80 | HTTP（Caddy 自动跳转 HTTPS） |
| 443 | HTTPS（Caddy TLS） |
| 7000 | frp 控制 |
| 7500 | frp 面板 (admin / musicvault2026) |

### 反向代理

```
外网 → Caddy(:443) → fake-star.xyz     → /opt/fake_yuki/apps/home/
                    → music.fake-star.xyz    → 127.0.0.1:8080
                    → bookmarks.fake-star.xyz → 127.0.0.1:8081
                    → portfolio.fake-star.xyz → 127.0.0.1:8082
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
| Pillow | 9.0.1 | apt `python3-pil`（作品集缩略图） |

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
| 重启作品集 | `systemctl restart fake-star-portfolio` | ECS |
| 改作品集管理密码 | `systemctl edit fake-star-portfolio` 改 `PORTFOLIO_ADMIN_PASSWORD` | ECS |

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
| **2026-07-22** | 书签站重构：FastAPI+SQLite 后端，标签页切换+动画，增删改书签，ECS :8081 部署；apps/nav→apps/bookmarks 重命名 |
| **2026-07-23** | 书签站新分类修复；音乐站队列逻辑修复（手动播放锁定，auto-advance 跟随）；STYLE_GUIDE 组件规范完善；跨站播放方案讨论（备案后统一架构） |
| **2026-07-24** | 🎉 域名备案通过，DNS 切至 ECS；三站统一部署（Caddy 反代 + Let's Encrypt HTTPS）；主站上线 https://fake-star.xyz；端口收敛（8080/8081 仅本地监听）；书签站 nav→bookmarks 路径修正 |
| **2026-07-25** | 🔌 Chrome 扩展迷你播放器（MV3，popup+content+background）；NCM 封面 picUrl 修复；跨站弹窗简化（主站恢复普通链接）；清理旧迷你弹窗代码；OpenClaw 卸载+frp 隧道清空；全部文档+记忆文件同步 |
| **2026-08-01** | 🐛 修复 M4A 误判 bug（`_is_real_audio_file` with 块提前关闭）+ NCM 扫码 cookie 误写 nickname；✨ 新增插队播放功能（`nextQueue` 优先级队列，`[＋]` 菜单"下一首播放"，播完后自动回到原歌单继续）；Cache-Control 改为 `no-store` |
| **2026-08-25** | 🖼️ 作品集站上线（面试用）：FastAPI+SQLite :8082，作品墙+lightbox（图片/视频，Range 拖动），密码管理页（HMAC cookie 鉴权、拖拽上传队列、Pillow 缩略图）；portfolio.fake-star.xyz 上线；主站摄影卡片→作品集入口 |

### 下一步

| 优先级 | 事项 |
|--------|------|
| ⭐⭐ | 随手记后端（碎碎念 + 图片上传） |
| ⭐⭐ | 移动端适配 |
| 💤 | 用户认证 / Agent 接入 |

---

## ⚠️ 注意事项

1. **frpc.exe 被 Defender 误杀** — 已将 `D:\fake_yuki` 加入排除项
2. **音乐文件不入 Git** — `music-files/` 在 `.gitignore` 中
2b. **作品集媒体/数据不入 Git** — `apps/portfolio/media/` 和 `apps/portfolio/data/` 在 `.gitignore` 中
3. **服务器凭证不入 Git** — `server/server.env` 和 `server/keys/` 在 `.gitignore` 中
4. **导航站独立仓库** — `apps/bookmarks/` 有自己的 Git 仓库，不跟主仓库混合
5. **换设备恢复** — `git clone git@github.com:Yuki-C-d/fake_yuki.git` + 拷入 music-files/ + tools/*.exe + server/keys/

---

## 📄 详细文档

| 文档 | 内容 | 位置 |
|------|------|------|
| 旧 README | music-vault 原始方案 | `docs/archive/README.md` |
| 旧 PROGRESS | 开发日记（踩坑记录） | `docs/archive/PROGRESS.md` |
| 旧 DEV_GUIDE | 操作手册（详细版） | `docs/archive/DEV_GUIDE.html` |
| 服务器文档 | ECS/frp 详细配置 | `docs/SERVER.md`（保留不归档） |

---

*本文档是 fake_yuki 项目手册的唯一入口。加新模块时，在"项目地图"中加一行，在下方加对应章节。*

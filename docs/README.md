# 🎵 music-vault

> 自建音乐云服务 — 把自己的音乐库放到网络上，随时随地听

_项目启动：2026-06-30 | 作者：此方 | 技术顾问：Yuki ❄️_

---

## 🎯 项目目标

打造一个**迷你网易云**：本地存储音乐文件 → Python 后端提供统一 API → 多终端播放

```
                    ┌─ 个人网站（作品展示 + 外网听歌）
FastAPI 后端 ───────┼─ 浏览器网页（MVP 阶段先用）
  (一直跑着)        └─ Electron 桌面软件（后期主力客户端）
```

核心思路：一套后端 API，多种前端形态，互不冲突。

---

## 🏗️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端框架 | **FastAPI** | Python 异步 Web 框架，自带 API 文档 |
| 数据库 | **SQLite** | 内置库，单文件，够用 |
| 音频元数据 | **mutagen** | 读取 FLAC/MP3/M4A 标签 |
| 前端 | **HTML + JS** | 简单播放器页面 |
| 音频转码 | **FFmpeg + av3a_decoder** | AV3A/MP4 → AAC/M4A 批量转换 |
| 音频解密 | **ncmdump** (C++) | 外部工具，解密 .ncm 文件 |

---

## 📁 目录结构

```
music-vault/
├── app/
│   ├── __init__.py
│   ├── main.py             # ⭐ FastAPI 入口，16 个路由
│   ├── models.py           # 数据库模型（songs + playlists + playlist_songs）
│   ├── scanner.py          # 文件扫描器
│   └── config.py           # 路径配置（支持 flac, m4a）
├── static/                 # 前端文件
│   └── index.html          # ✅ 播放器页面（歌单 + 播放 + 错误提示）
├── music/                  # 🎵 音乐文件放这里
│   ├── m4a/                # ✅ 转码后的 AAC/M4A 文件（浏览器可播）
│   └── originals/          # 📦 原始 AV3A/MP4 文件（不删，备份）
├── tools/                  # 转码工具
│   ├── av3a_decoder/       # AV3A 解码器（av3a_decoder.exe）
│   └── extract_av3a.py     # MP4 → raw AV3A 流提取脚本
├── data/                   # SQLite 数据库
│   └── music.db            # 已入库 3 首 m4a
├── convert_to_m4a.sh       # 🔧 批量转码脚本（AV3A/MP4 → AAC/M4A）
├── ncmdump/                # ncm 解密工具
├── .gitignore              # Git 忽略规则
├── requirements.txt
└── README.md
```

---

## 🗄️ 数据库设计（SQLite）

### songs 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增 ID |
| title | TEXT | 歌曲标题 |
| artist | TEXT | 艺人 |
| album | TEXT | 专辑 |
| duration | REAL | 时长（秒） |
| file_path | TEXT | 相对于 music/ 的路径 |
| file_format | TEXT | flac / m4a / mp3 |
| file_size | INTEGER | 文件大小（字节） |
| added_at | TIMESTAMP | 入库时间 |

---

## 🔌 API 设计（当前版本）

### 歌曲

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/songs` | 获取所有歌曲列表 |
| GET | `/api/songs/{id}` | 获取单曲详情 |
| GET | `/api/stream/{id}` | 音频流播放（动态 MIME + Range 支持） |

### 上传 & 转码

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/upload` | 上传音频文件（支持 .ncm 自动解密） |
| GET | `/api/conversions` | 查看转码队列和进度 |

### 管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/scan` | 触发重新扫描 music/ 目录 |

### 歌单

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/playlists` | 获取所有歌单 |
| POST | `/api/playlists` | 创建歌单 |
| PUT | `/api/playlists/{id}` | 重命名歌单 |
| DELETE | `/api/playlists/{id}` | 删除歌单 |
| GET | `/api/playlists/{id}/songs` | 获取歌单内歌曲 |
| POST | `/api/playlists/{id}/songs` | 添加歌曲到歌单 |
| DELETE | `/api/playlists/{id}/songs/{sid}` | 从歌单移除歌曲 |
| PUT | `/api/playlists/{id}/songs/reorder` | 重新排序 |

### 支持的音频格式

| 格式 | MIME | 浏览器兼容 |
|------|------|------------|
| `.m4a` (AAC) | audio/mp4 | ✅ 全平台 |
| `.mp3` | audio/mpeg | ✅ 全平台 |
| `.flac` | audio/flac | ⚠️ 部分支持 |
| `.ogg` | audio/ogg | ✅ |
| `.wav` | audio/wav | ✅ |
| `.aac` | audio/aac | ✅ |

---

## 🔧 AV3A/MP4 转码

部分音乐平台下载的文件实际是 MP4 容器 + AV3A (Audio Vivid/菁彩声) 编码。浏览器无法解码此格式。

### 一键转码

```bash
# 前置：tools/av3a_decoder/ 下有 av3a_decoder.exe
./convert_to_m4a.sh
```

### 流水线

```
源文件 (MP4/AV3A, 12ch)
    │  [1] Python 提取 mdat box → raw .av3a
    ▼  [2] av3a_decoder.exe → 12ch WAV (临时)
    ▼  [3] ffmpeg → 立体声 AAC 256k + 元数据注入
  music/m4a/xxx.m4a  ✅
```

- 原始文件移至 `music/originals/`，不删除
- 元数据（歌手、专辑、标题、音轨号）自动保留
- 已存在文件自动跳过，可安全重复执行

### 获取解码器

蓝奏云: `https://wwp.lanzn.com/b05f4b0xe`  密码: `6jj4`

---

## 🚀 开发路线图

### Phase 1：MVP（最小可行版本）✅ 已完成

- [x] 搞定 3~5 首测试音频放入 music/
- [x] 搭建 FastAPI 项目骨架
- [x] 实现 scanner.py（扫描文件 → 读元数据 → 写入 SQLite）
- [x] 实现 config.py + models.py（路径配置 + 数据库层）
- [x] 实现 GET /api/songs（返回歌曲列表）
- [x] 实现 GET /api/stream/{id}（音频流播放）
- [x] 写一个最简单的 HTML 播放器页面（列表 + 播放按钮）
- [x] 本地跑通：浏览器打开 → 看到歌曲 → 点击播放
- [x] 安全加固：路径穿越防护 + 数据库连接管理
- [x] 新增 GET /api/songs/{id}（单曲详情）+ POST /api/scan（手动扫描）
- [x] 前端错误处理（加载失败/播放失败提示）
- [x] 配置 .gitignore 忽略规则
- [x] AV3A 转码 → AAC/M4A，浏览器可播
- [x] 数据库仅保留可播放格式，原文件归档至 originals/

### Phase 2：体验完善 ✅ 已完成

- [x] 进度条拖动（HTTP Range 请求支持）
- [x] 切歌（上一首/下一首 + 键盘快捷键 + 自动下一首）
- [x] 播放队列（歌单即队列，搜索过滤不影响队列顺序）
- [x] 搜索功能（实时过滤歌名/歌手/专辑）
- [x] UI 美化（暗色主题，Spotify 风格）

### Phase 3：进阶功能 ✅ 基本完工

- [x] 歌单管理（创建/编辑/删除歌单，右键菜单添加歌曲）
- [ ] 后台自动扫描（文件变更自动更新数据库）
- [x] 格式转换（FFmpeg + av3a_decoder 流水线）
- [ ] 音质切换（FLAC ↔ M4A 多版本）

### Phase 4：外网访问 🚧 进行中

- [x] frp 内网穿透 — 阿里云 ECS 广州 2核2G，99元/年
- [ ] 用户认证（token/jwt）
- [ ] 移动端适配
- [ ] DDNS 动态域名

---

## ☁️ 外网访问

```
外网 → 8.166.119.185:8080 → frps(阿里云) → frpc(你电脑) → FastAPI:8080
                              ↑
                      8.166.119.185:7500 (frp管理面板)
```

---

## ⚠️ 已知坑 & 注意事项

1. ~~**FLAC 浏览器兼容**~~ — ✅ 已解决。测试曲实为 AV3A 编码，已批量转码为 AAC/M4A
2. ~~**AV3A 格式问题**~~ — ✅ 已解决。`convert_to_m4a.sh` 一键转码流水线，支持保留元数据
3. **HTTP Range 请求** — ✅ Starlette FileResponse 内置支持，进度条拖动正常
4. **scanner 扫描逻辑** — 新加歌曲不会自动入库，调 `POST /api/scan` 手动触发即可
5. ~~**文件路径安全**~~ — ✅ 已加固：`safe_file_path()` 校验所有路径，防止目录穿越
6. ~~**数据库连接泄漏**~~ — ✅ 已修复：`contextlib.closing()` 包裹连接，确保每次请求后释放
7. **音频大小** — M4A 一首 7-15MB，FLAC 一首 30-50MB，注意 D 盘空间
8. **frpc.exe 被 Defender 拦截** — D:\music-vault 已加杀毒排除

---

_Last updated: 2026-07-10_

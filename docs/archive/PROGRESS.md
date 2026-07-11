# music-vault 项目记忆

> 此方的自建音乐云 — 进度跟踪、设计决策、踩坑记录
> 需要 Yuki 回忆时提醒她读这个文件

_创建：2026-07-01_

## ⚙️ 维护规则

- **什么时候更新本文件：** 做了新的功能、改了设计、踩了坑、做了重要决定
- **什么时候更新 DEV_GUIDE.html：** 命令变了、目录结构变了、操作流程变了
- **什么时候更新 README.md：** 架构变了、API 接口变了、路线图调整了
- **不需要每天更新** — 没变化就不写，避免废话文档

---

## 📅 2026-06-30 晚 ~ 07-01 凌晨（项目启动）

### 完成事项
- ✅ 项目命名：music-vault
- ✅ 技术选型：FastAPI + SQLite + mutagen + ncmdump
- ✅ pip 依赖安装（fastapi 0.138 / uvicorn 0.49 / mutagen 1.48）
- ✅ 目录结构搭建（app/ / static/ / data/ / music/ / ncmdump/）
- ✅ ncmdump v1.5.1 下载 + 解密测试
- ✅ 3 首测试 FLAC 解密成功
  - ONE OK ROCK - The Pilot 3 (DETOX JAPAN TOUR 2025)
  - 坂本龍一 - Merry Christmas Mr. Lawrence
  - Michael Dulin - Simply Satie
- ✅ DEV_GUIDE.html 操作手册
- ✅ README.md 设计方案
- ✅ requirements.txt 填写

### 设计决策
- 公网方案选 frp 内网穿透（不用云服务器，省钱）
- 电脑一直开着当服务器
- 先用 MP3/FLAC 混合存储（受限于 D 盘空间）
- 不使用 Notion 等外网平台存文档（用 HTML 本地）
- **多端架构（2026-07-01 晚）**：一套 FastAPI 后端 → 网页版 + 后期 Electron 桌面版 + 个人网站展示，所有客户端共享同一套 API

### 当前项目结构
```
D:\music-vault\
├── README.md          ← 方案设计
├── DEV_GUIDE.html     ← 操作手册
├── PROGRESS.md        ← 本文件
├── requirements.txt
├── app\               ← 后端代码（config/models/scanner 待写）
├── music\             ← 3首 FLAC
├── ncmdump\           ← ncmdump.exe
├── static\            ← 空
└── data\              ← 空（数据库待生成）
```

### 下一步（已完成 ✅）
- [x] 写 apps/music/backend/config.py
- [x] 写 apps/music/backend/models.py
- [x] 写 apps/music/backend/scanner.py（核心）

---

## 📅 2026-07-01 晚上（后端三大模块完工）

### 完成事项
- ✅ **apps/music/backend/config.py** — 路径常量（BASE_DIR / MUSIC_DIR / DB_PATH / SUPPORTED_FORMATS）
- ✅ **apps/music/backend/models.py** — SQLite 数据库层
  - `init_db()` 建表
  - `get_connection()` 返回数据库连接
  - `insert_song()` 入库（INSERT OR IGNORE 防重复）
  - `get_all_songs()` / `get_song_by_id()` 查询
- ✅ **apps/music/backend/scanner.py** — 文件扫描器
  - `os.walk()` 遍历 music/ 目录
  - 格式自动检测（FLAC + MP4 双兼容）
  - `get_tag()` 跨格式读标签（适配 FLAC/MP4 不同 key 名）
  - try/except 双重防重复插入

### 踩坑记录
1. **测试文件是 AV3A（Audio Vivid）封装，不是 FLAC**  
   - ~~2026-07-01 误判为 M4A~~ → **2026-07-02 此方发现并纠正**
   - header 是 `ftypisom`（MP4 容器），扩展名 `.flac` 但实际编码是 **av3a（菁彩声/AVS3-P3）**
   - 三个文件的 stsd format 码全是 `av3a`，确认是中国 AVS3 音频标准
   - 用 `mutagen.mp4.MP4()` 手动 fallback 依然可用，因为容器是标准 MP4
   - **⚠️ 教训：** 不要只看容器格式就说是什么编码，要看 stsd 的 4CC 码
2. **MP4 标签 key 名不同**
   - FLAC 用 `title`/`artist`/`album`
   - MP4 用 `©nam`/`©ART`/`©alb`
   - 写了 `get_tag()` 函数统一处理
3. **Python 三引号字符串 ≠ 注释**
   - 此方看到 `"""..."""` 以为是被注释掉的代码，实际是 SQL 字符串模板
4. **相对路径 vs 绝对路径**
   - 数据库存 `file_path` 应存相对路径（`os.path.relpath`），方便以后换 MUSIC_DIR

### 当前项目结构
```
D:\music-vault\
├── README.md
├── DEV_GUIDE.html
├── PROGRESS.md
├── requirements.txt
├── app\
│   ├── __init__.py         ← 空
│   ├── config.py           ← ✅ 路径配置
│   ├── models.py           ← ✅ 数据库层
│   ├── scanner.py          ← ✅ 文件扫描器
│   └── main.py             ← ✅ FastAPI 入口
├── music\                 ← 3 首 AV3A（伪装成 .flac，实际是 MP4 容器包裹 av3a 编码）
├── ncmdump\
├── static\                ← ✅ index.html 播放器
└── data\
    └── music.db            ← ✅ 已生成，3 首歌入库
```

### 数据库验证
```
ID:1 | Simply Satie | Michael Dulin | 242s
ID:2 | The Pilot </3 | ONE OK ROCK | 464s
ID:3 | Merry Christmas Mr. Lawrence | 坂本龍一 | 347s
```

### 下一步
- [x] 写 apps/music/backend/main.py（FastAPI 入口 + /api/songs + /api/stream/{id}）
- [x] 写 static/index.html（简易播放器）
- [x] 浏览器跑通：看到歌单 → 点击播放

### 学习记录
- 此方学到了：sqlite3 是什么、`"""` 多行字符串 ≠ 注释、相对导入（`.config`）、INSERT OR IGNORE 防重复

---

## 📅 2026-07-02 晚上（MVP 全线跑通 🎉）

### 完成事项
- ✅ **apps/music/backend/main.py** — FastAPI 入口
  - `lifespan` 模式启动时自动 init_db + scan
  - CORS 跨域配置
  - `GET /api/songs` — 返回全部歌单（tuple→dict 转换）
  - `GET /api/stream/{song_id}` — FileResponse 流式播放
- ✅ **static/index.html** — 浏览器播放器
  - fetch 歌单 + 渲染列表
  - `<audio>` 控件播放
  - 当前播放高亮（li.active）
  - 歌手名金色小字
- 踩坑：
  - 相对导入 `from . import config` 不行，改 `from app import config`
  - `app.mount("/", StaticFiles...)` 会和 API 路由冲突，改 `HTMLResponse` 读取
  - 测试曲是 AV3A 格式，浏览器不认，无法播放（代码没问题）

---

## 📅 2026-07-04（代码审查 + 安全加固，Yuki 协助 ❄️）

### 修复内容

#### 🔴 严重 Bug
- ✅ **重复路由 `/`** — 删除了覆盖 index() 的 read_root()，播放器页面恢复正常
- ✅ **路径穿越漏洞** — 新增 `safe_file_path()` 函数，用 `os.path.realpath` 校验所有流媒体请求，防止 `../` 读取系统文件
- ✅ **数据库连接泄漏** — `list_songs` / `get_song` / `stream_song` 改用 `contextlib.closing()` 包裹连接，确保每次请求后释放

#### 🟡 功能完善
- ✅ **新增 `GET /api/songs/{id}`** — 单曲详情端点（含 file_size、added_at）
- ✅ **新增 `POST /api/scan`** — 手动触发扫描，返回入库数量 → 加歌后不需要重启服务
- ✅ **动态 MIME 类型** — `stream_song` 根据 file_format 自动匹配正确的 Content-Type（不再写死 audio/flac）
- ✅ **scanner 异常日志** — mutagen 读取失败时用 `logging.warning` 记录，不再静默吞错
- ✅ **`get_tag()` 返回空字符串** — 无标签时返回 `""` 而非 `'Unknown'`
- ✅ **扩展名统一小写** — `file_format` 强制 `.lower()` 入库

#### 🟢 前端 & 工程化
- ✅ **前端错误处理** — fetch 失败时显示具体错误信息；空歌单有提示
- ✅ **音频播放失败提示** — `<audio>` error 事件监听，播放失败时当前歌曲变红 + ❌
- ✅ **新建 `.gitignore`** — 排除 `__pycache__/`、`data/`、`music/`、`ncmdump/` 等
- ✅ **scanner 死代码清理** — 删除未使用的 `before_count` 变量

### 踩坑记录
1. **sqlite3 的 `with conn:` 不自动 close** — Python sqlite3 的 `__exit__` 只提交/回滚事务，不关闭连接。必须用 `contextlib.closing()` 包裹。
2. **`<li onerror>` 无效** — `error` 事件只在加载外部资源的元素上触发（`<img>`、`<audio>`、`<video>`），`<li>` 永远不会触发。改为 `player.addEventListener('error', ...)`。
3. **`os.path.join` 的安全边界** — 即使 `rel_path` 是绝对路径或含盘符，`realpath` + `startswith` 双重校验仍然能防住。

### 当前 API 端点
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 播放器页面 |
| GET | `/api/songs` | 全部歌单 |
| GET | `/api/songs/{id}` | 单曲详情 |
| GET | `/api/stream/{id}` | 音频流（动态 MIME + 路径安全校验） |
| POST | `/api/scan` | 手动扫描入库 |

### 下一步
- [ ] 转码测试曲（AV3A → MP3），让浏览器能播放
- [ ] HTTP Range 请求支持（进度条拖动）
- [ ] UI 美化
- [ ] 搜索功能

---

---

## 📅 2026-07-05（AV3A 转码 + 浏览器播放上线 🎉）

### 背景
3 首测试曲实际是 MP4 容器 + AV3A (Audio Vivid/菁彩声) 编码，浏览器完全不支持。社区没有预编译的 ffmpeg AV3A 解码器。

### 完成事项
- ✅ **获取 AV3A 解码器** — 从蓝奏云下载 `av3a_decoder_v0.2.zip`（含 `av3a_decoder.exe`）
  - 绕过蓝奏云反爬 JS 挑战（踩坑记录见下）
  - 码率 832 kbps / 12 声道 / 44100 Hz
- ✅ **三步转码流水线 `/convert_to_m4a.sh`**
  1. Python 提取 MP4 `mdat` box → raw AV3A 流
  2. `av3a_decoder.exe` → 12ch WAV（~9 fps，约 30-50 分钟/首）
  3. `ffmpeg` → 立体声 AAC 256kbps M4A + `-map_metadata` 注入标签
  - 原文件移至 `music/originals/`，不删除
  - 已存在文件自动跳过
- ✅ **全部 3 首转码成功**
  - Michael Dulin - Simply Satie (7.4 MB, 4:01)
  - ONE OK ROCK - The Pilot 3 (15 MB, 7:44)
  - 坂本龍一 - Merry Christmas Mr. Lawrence (11 MB, 5:46)
- ✅ **Web 播放器上线** — `http://localhost:8080` 浏览器直接播放
- ✅ **`.m4a` 加入 `SUPPORTED_FORMATS`** — scanner 扫描 m4a 文件
- ✅ **数据库清理** — 删除无法播放的 flac 记录，仅保留 m4a
- ✅ **元数据修复** — 初版脚本元数据丢失，改用 `-map_metadata` 从源文件直接注入
- ✅ **脚本 bug 修复**
  - `set -e` + `((counter++))` 在 counter=0 时返回 1 导致脚本退出 → 去掉 `-e`
  - 元数据提取 `TAG:` 前缀未过滤 → 改用 `-map_metadata` 方案

### 踩坑记录
1. **蓝奏云反爬 JS 挑战** — 文件页返回 `acw_sc__v2` 反爬，`lanzou-api` 库的 `lanzou[a-z]` 正则不认 `lanzn.com` 域名。最终绕过：用 `lanzouc.com` 域名 + 手动追踪 iframe→ajaxm.php→developer3.lanrar.com→直链。
2. **`av3a_decoder.exe` 不接受 MP4 容器** — 必须先从 mdat box 提取 raw AV3A 流（Python 解析 ISOBMFF 结构），直接丢 MP4 会报 `ZeroDivisionError`。
3. **解码速度** — `av3a_decoder.exe` 仅 ~8-9 fps，24548~47177 帧，单首需 30-50 分钟。
4. **`((SUCCESS++))` 与 `set -e` 冲突** — bash 中 `((0++))` 返回 1 触发退出，导致脚本在第一首完成后崩溃。

### 当前项目结构
```
D:\music-vault\
├── app\                    ← 后端代码
├── static\                 ← index.html 播放器
├── music\                  ← 🎵
│   ├── m4a\               ← ✅ 3 首 AAC/M4A（浏览器可播）
│   └── originals\          ← 📦 原始 AV3A/MP4 文件（备份，不删）
├── tools\
│   ├── av3a_decoder\       ← av3a_decoder.exe
│   └── extract_av3a.py    ← MP4→raw AV3A 提取脚本
├── data\                   ← music.db（3 首 m4a）
├── convert_to_m4a.sh       ← 🔧 批量转码脚本
└── ...
```

### 当前 API 端点
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 播放器页面 |
| GET | `/api/songs` | 全部歌单（当前 3 首 m4a） |
| GET | `/api/songs/{id}` | 单曲详情 |
| GET | `/api/stream/{id}` | 音频流（支持 m4a/flac/mp3 等） |
| POST | `/api/scan` | 手动扫描入库 |

### 下一步
- [ ] HTTP Range 请求支持（进度条拖动）
- [ ] 切歌 / 播放队列
- [ ] UI 美化
- [ ] 搜索功能

---

_Last updated: 2026-07-05_

---

## 📅 2026-07-06（Phase 2 完工 + 转码优化，Yuki 协助 ❄️）

### Phase 2 完成事项
- ✅ **HTTP Range 请求支持** — Starlette `FileResponse` 内置 Range 处理，浏览器进度条拖动正常
  - 经排查：代码不需要额外改动，Starlette 1.3.1 自动处理 `Range`/`206`/`Content-Range`
  - VS Code 内置浏览器不支持 M4A 解码，用外部浏览器打开 `http://localhost:8080` 即可
- ✅ **切歌** — ⏮ ⏭ 按钮 + 键盘 `←` `→` + 播放结束自动下一首
- ✅ **搜索** — 顶部搜索框，实时过滤歌名/歌手/专辑
- ✅ **UI 美化** — 暗色主题（Spotify 风格），圆角卡片、蓝色强调色、键盘快捷键提示

### Bug 修复
- ✅ **scanner 跳过 originals/** — 添加 `EXCLUDED_DIRS = {"originals"}`，避免备份文件重复入库
- ✅ **数据库清理** — 删除 3 条 originals FLAC 记录，歌单仅显示 3 首 M4A

### 转码优化
- ✅ **并行转码** — `convert_to_m4a.sh` 支持同时处理多文件
  - 默认并行数 = CPU 核心数，可 `MAX_JOBS=2` 覆盖
  - 3 首歌总时间从 ~2 小时缩短到 ~50 分钟（最长那首的时间）
  - 新增源文件自动归档到 `music/originals/`
  - 每文件独立日志，避免并行输出交错

### 当前状态
- 服务: `python -m uvicorn apps.music.backend.main:app --host 0.0.0.0 --port 8080`
- 曲库: 3 首 M4A/AAC
- Phase 1 ✅ | Phase 2 ✅ | Phase 3 待开始

### 下一步
- [ ] 歌单管理（创建/编辑/删除歌单）
- [ ] 后台自动扫描（文件变更自动更新数据库）
- [ ] 音质切换
- [ ] 外网访问（frp 内网穿透）

---

## 📅 2026-07-06 晚间（网页导入 + 自动转码，Yuki 协助 ❄️）

### 完成事项
- ✅ **网页端上传歌曲** — 拖拽/点击上传，支持 `.m4a .flac .mp3 .ogg .wav .aac .mp4 .ncm`
  - POST /api/upload 端点：格式校验、去重、安全文件名
  - scanner.py 重构：抽取 `scan_single_file()` 函数
- ✅ **NCM 自动解密** — 上传 .ncm → ncmdump 自动解密 → 扫描入库
- ✅ **AV3A 伪装检测** — 检测 .flac 文件头（真 FLAC = `fLaC`，AV3A = `ftyp`），避免浏览器播放失败
- ✅ **后台自动转码** — 检测到 AV3A 后自动启动 `convert_to_m4a.sh` 后台转码，不阻塞上传
- ✅ **转码进度可视化** — GET /api/conversions 接口 + 网页转码队列区域
  - 状态：⏳排队中 → 🔓解码中 → 🎚️即将完成 → ✅已完成自动入库
  - 每 30 秒自动轮询
  - 未转码文件带 `.flac [状态]` 标记，转码完成后自动消失
- ✅ **转码脚本自动扫描** — convert_to_m4a.sh 结尾自动调 POST /api/scan

### 上传流程
```
网页拖入文件
  ├─ .m4a/.mp3/.ogg 等 → 直接入库 → ✅ 可播
  ├─ .ncm → ncmdump 解密 → 检测格式
  │    ├─ 真音频 → 入库 → ✅ 可播
  │    └─ AV3A → 后台转码 → 50min 后自动入库 → ✅ 可播
  └─ .flac → 检测文件头
       ├─ 真 FLAC (fLaC) → 入库 → ✅ 可播
       └─ AV3A (ftyp) → 后台转码 → 自动入库 → ✅ 可播
```

### 当前状态
- 服务: `python -m uvicorn apps.music.backend.main:app --host 0.0.0.0 --port 8080`
- 曲库: 3 首 M4A（originals/ 内备份 AV3A 源文件，非待转码队列）
- Phase 1 ✅ | Phase 2 ✅ | Phase 3 部分完成（上传导入）

### 下一步
- [ ] 转码完成后自动刷新前端（WebSocket 或 SSE 推送）
- [ ] 外网访问（frp 内网穿透）

---

## 📅 2026-07-07（歌单管理上线，Yuki 协助 ❄️）

### 完成事项
- ✅ **歌单管理** — Phase 3 核心功能完工
  - 数据库：新增 `playlists` + `playlist_songs` 两张表，外键级联
  - API：8 个新端点（CRUD + 添加/移除歌曲 + 排序）
  - 前端：左侧边栏切换歌单、右键菜单添加歌曲、重命名/删除歌单
  - "全部歌曲" 为虚拟歌单，始终显示所有入库歌曲
  - 播放队列逻辑不变，始终以当前显示列表为队列

### 设计决策
- 选择**左侧边栏**而非 Tab 栏（用户偏好网易云桌面版布局）
- 选择**右键菜单**添加歌曲（不破坏现有交互）
- 歌单存在 playlists 表，但"全部歌曲"是虚拟的（不存数据库）
- 删除歌单不删歌曲（CASCADE 只清理关联表）
- 小屏（<768px）侧边栏折叠

### 当前 API 端点 (16 个)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 播放器页面 |
| GET | `/api/songs` | 全部歌单 |
| GET | `/api/songs/{id}` | 单曲详情 |
| GET | `/api/stream/{id}` | 音频流 |
| POST | `/api/upload` | 上传音频 |
| POST | `/api/scan` | 手动扫描 |
| GET | `/api/conversions` | 转码进度 |
| GET | `/api/playlists` | 歌单列表 |
| POST | `/api/playlists` | 创建歌单 |
| PUT | `/api/playlists/{id}` | 重命名歌单 |
| DELETE | `/api/playlists/{id}` | 删除歌单 |
| GET | `/api/playlists/{id}/songs` | 歌单歌曲 |
| POST | `/api/playlists/{id}/songs` | 添加歌曲 |
| DELETE | `/api/playlists/{id}/songs/{sid}` | 移除歌曲 |
| PUT | `/api/playlists/{id}/songs/reorder` | 排序 |

### 下一步
- [ ] 音质切换（FLAC ↔ M4A 多版本）
- [ ] 后台自动扫描（文件变更自动更新）
- [ ] 转码完成推送（SSE）— 可与 Agent 远程控制共用 SSE 通道
- [x] 外网访问（frp 内网穿透）✅ 2026-07-10
- [📋] Agent 接入接口 — 设计方案已存记忆，待功能稳定后实施（见 [[agent-integration-design]]）

---

## 📅 2026-07-10（frp 内网穿透上线 🚀）

### 完成事项
- ✅ **阿里云 ECS 购入** — 华南广州，2核2G，3Mbps 固定带宽，Ubuntu 22.04
  - 99元/年，续费同价锁定到 2030 年
  - SSH 密钥认证（密码已废弃）
- ✅ **frps 服务端** — `/opt/frp/frps` + systemd 开机自启
  - bindPort=7000, dashboard=7500
  - 日志 `/var/log/frps.log`，保留 7 天
- ✅ **frpc 客户端** — `D:\music-vault\.server\frpc_local\`
  - 开机自启（启动文件夹 `start-frpc.bat`）
  - 本地 8080 → 公网 8.166.119.185:8080
- ✅ **安全组已开端口**: 7000(frp), 7500(面板), 8080(音乐站)
- ✅ **外网访问验证通过** — `curl http://8.166.119.185:8080/api/songs` 正常

### 架构
```
外网 → 8.166.119.185:8080 → frps(阿里云) → frpc(你电脑) → FastAPI:8080
                                    ↑
                          8.166.119.185:7500 (管理面板)
```

### 相关文件
| 文件 | 用途 |
|------|------|
| `.server.env` | ECS IP + frp 凭证 |
| `.server/id_ed25519` | SSH 私钥 |
| `.server/frpc_local/frpc.toml` | frpc 配置 |
| `.server/start-frpc.bat` | frpc 开机启动脚本 |

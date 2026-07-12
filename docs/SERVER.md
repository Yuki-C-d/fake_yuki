# ☁️ fake_yuki 服务器文档

> 最后更新: 2026-07-11

---

## 1. 服务器基本信息

| 项目 | 详情 |
|------|------|
| **厂商** | 阿里云 ECS 经济型 e 实例 |
| **公网 IP** | `8.166.119.185` |
| **配置** | 2核 CPU / 2GB 内存 / 40GB SSD |
| **带宽** | 3 Mbps 固定（不限流量） |
| **系统** | Ubuntu 22.04.5 LTS (kernel 5.15) |
| **地域** | 华南 广州 |
| **主机名** | `iZ7xvj7oastyctmmjavq19Z` |
| **价格** | 99 元/年，续费同价锁定至 2030 年 |
| **购入日期** | 2026-07-10 |

---

## 2. 登录方式

### SSH 密钥登录（唯一方式）

```bash
# 私钥位置（本地）
ssh -i D:\fake_yuki\server\keys\id_ed25519 root@8.166.119.185
```

| 文件 | 说明 |
|------|------|
| `server/keys/id_ed25519` | SSH 私钥（勿泄露） |
| `server/keys/id_ed25519.pub` | SSH 公钥 |

> ⚠️ 密码认证已废弃。密钥通过阿里云控制台绑定到 ECS 实例。若重装系统需重新绑定。

---

## 3. 端口映射

### 阿里云安全组入方向规则

| 端口 | 协议 | 用途 | 说明 |
|------|------|------|------|
| 22 | TCP | SSH | 服务器管理 |
| 7000 | TCP | frp 控制端口 | frpc ↔ frps 通信 |
| 7500 | TCP | frp 管理面板 | 浏览器查看隧道状态 |
| 8080 | TCP | 音乐站 | 外网访问 fake_yuki |
| 18790 | TCP | OpenClaw WebSocket | ECS node ↔ 本地 Gateway |

---

## 4. 已安装软件

| 软件 | 版本 | 安装方式 | 路径 |
|------|------|----------|------|
| **frps** | v0.69.1 | 二进制下载 | `/opt/frp/frps` |
| **Node.js** | v24.16.0 LTS | npmmirror 镜像 | `/usr/local/node-v24.16.0-linux-x64/` |
| **npm** | 11.13.0 | 随 Node.js | — |
| **OpenClaw** | v2026.6.11 | npm 全局安装 | `/usr/local/node-v24.16.0-linux-x64/bin/openclaw` |
| **Python** | 3.10.12 | 系统自带 | `/usr/bin/python3` |

### npm 源

已切换至国内镜像: `https://registry.npmmirror.com`

---

## 5. 服务一览

| 服务 | 状态 | 管理方式 | 开机自启 |
|------|------|----------|----------|
| **frps** | ✅ active | `systemctl {start\|stop\|restart\|status} frps` | ✅ |
| **SSH** | ✅ active | `systemctl {start\|stop\|restart} sshd` | ✅ |
| **OpenClaw node** | ⚠️ 手动启动 | 见下方 | ❌ |

### OpenClaw node 启动命令

```bash
# ECS 上执行
OPENCLAW_GATEWAY_TOKEN=0daca09b2655e4aee5f686b59b9143f7428c5806dcfe5f66 \
  nohup openclaw node run > /tmp/oc-node.log 2>&1 &

# 停止
pkill -f openclaw-node
```

> ⚠️ node 未配置 systemd 服务，服务器重启后需手动启动。

---

## 6. frp 内网穿透

### 架构

```
外网请求
    │
    ▼
8.166.119.185:8080 (阿里云 ECS)
    │
    ▼ frps (systemd 开机自启)
    │
    ▼ frpc (你电脑，开机自启)
    │
    ▼
localhost:8080 (FastAPI 音乐站)
```

### frps 配置（服务器端）

- 配置文件: `/opt/frp/frps.toml`
- Token: `mv-frp-token-2026-07-10`
- 管理面板: http://8.166.119.185:7500（admin / musicvault2026）
- 日志: `/var/log/frps.log`（保留 7 天）
- systemd 服务: `/etc/systemd/system/frps.service`

### frpc 配置（本地）

- 配置文件: `D:\fake_yuki\server\frpc\frpc.toml`
- 开机自启: `D:\fake_yuki\server\start-frpc.bat` → 启动文件夹

### 隧道列表

| 名称 | 类型 | 本地端口 | 远程端口 | 用途 |
|------|------|----------|----------|------|
| music-vault | TCP | 8080 | 8080 | 音乐站 |
| gw-ws | TCP | 18789 | 18790 | OpenClaw Gateway ↔ ECS Node |

### 常用命令

| 操作 | 命令 | 在哪跑 |
|------|------|--------|
| 查看 frps 状态 | `systemctl status frps` | 服务器 |
| 重启 frps | `systemctl restart frps` | 服务器 |
| 查看隧道 | 浏览器打开 `http://8.166.119.185:7500` | 任意 |
| frps 日志 | `tail -f /var/log/frps.log` | 服务器 |
| 启动 frpc | `D:\fake_yuki\server\frpc\frpc.exe -c D:\fake_yuki\server\frpc\frpc.toml` | 本地 |
| 杀 frpc | `taskkill /f /im frpc.exe` | 本地 |

---

## 7. Node.js 安装方法（备忘）

由于 GFW 无法访问 `deb.nodesource.com`，使用 npmmirror 国内镜像下载预编译包：

```bash
# 1. 下载（以 v24.16.0 为例）
cd /tmp
curl -L -o node.tar.xz "https://npmmirror.com/mirrors/node/v24.16.0/node-v24.16.0-linux-x64.tar.xz"

# 2. 解压到 /usr/local
cd /usr/local
tar -xJf /tmp/node.tar.xz

# 3. 创建软链接
ln -sf /usr/local/node-v24.16.0-linux-x64/bin/node /usr/local/bin/node
ln -sf /usr/local/node-v24.16.0-linux-x64/bin/npm /usr/local/bin/npm
ln -sf /usr/local/node-v24.16.0-linux-x64/bin/npx /usr/local/bin/npx

# 4. 切换 npm 源
npm config set registry https://registry.npmmirror.com

# 5. 清理
rm /tmp/node.tar.xz
```

---

## 8. 本地相关文件

所有服务器相关文件位于 `D:\fake_yuki\server\`（已加入 `.gitignore`）：

| 文件 | 用途 |
|------|------|
| `server.env` | ECS IP + frp 凭证汇总 |
| `keys/id_ed25519` | SSH 私钥 |
| `keys/id_ed25519.pub` | SSH 公钥 |
| `frpc/frpc.toml` | frpc 配置 |
| `frpc/frpc.exe` | frpc 可执行文件 |
| `start-frpc.bat` | frpc 开机启动脚本 |

### Windows Defender 排除

已排除 `D:\fake_yuki` 整个文件夹，防止 Defender 误杀 `frpc.exe`。

---

## 9. 故障排查

| 问题 | 排查方法 |
|------|----------|
| 外网访问不了音乐站 | `curl http://8.166.119.185:8080/api/songs` |
| frp 隧道断了 | 浏览器打开 `http://8.166.119.185:7500` 查看 |
| frps 挂了 | `ssh root@8.166.119.185 "systemctl status frps"` |
| frpc 挂了 | 本地 `tasklist \| findstr frpc`，没有就手动启动 |
| SSH 连不上 | 检查 `id_ed25519` 文件是否在、阿里云安全组 22 端口是否开放 |
| ECS node 离线 | `ssh root@8.166.119.185 "ps aux \| grep openclaw"`，必要时手动启动 |

---

## 10. 费用

| 项目 | 费用 | 周期 |
|------|------|------|
| 阿里云 ECS 经济型 e | 99 元 | 每年 |
| frp 隧道 | 免费 | — |
| 域名（待购） | 0 元 | 暂无 |

---

*本文档涵盖截至 2026-07-11 的所有服务器配置。OpenClaw node 部署问题详见 `docs/archive/PROGRESS.md`。*

---
name: deploy
description: Deploy fake_yuki code to Alibaba Cloud ECS. Use when the user asks to deploy, upload, 部署, or update the server.
---

## ECS Deploy

Deploy updated files to the ECS server at `8.166.119.185`.

### Music Station

```bash
scp -i "D:/fake_yuki/server/keys/id_ed25519" D:/fake_yuki/apps/music/frontend/index.html root@8.166.119.185:/opt/fake_yuki/apps/music/frontend/index.html
scp -i "D:/fake_yuki/server/keys/id_ed25519" D:/fake_yuki/apps/music/backend/main.py root@8.166.119.185:/opt/fake_yuki/apps/music/backend/main.py
ssh -i "D:/fake_yuki/server/keys/id_ed25519" root@8.166.119.185 "systemctl restart fake-yuki-music"
```

### Home Page

```bash
scp -i "D:/fake_yuki/server/keys/id_ed25519" D:/fake_yuki/apps/home/index.html root@8.166.119.185:/opt/fake_yuki/apps/home/index.html
```

### Bookmarks

```bash
scp -i "D:/fake_yuki/server/keys/id_ed25519" D:/fake_yuki/apps/bookmarks/frontend/index.html root@8.166.119.185:/opt/fake_yuki/apps/bookmarks/frontend/index.html
scp -i "D:/fake_yuki/server/keys/id_ed25519" D:/fake_yuki/apps/bookmarks/backend/main.py root@8.166.119.185:/opt/fake_yuki/apps/bookmarks/backend/main.py
```

### Services

| Service | Restart |
|---------|---------|
| Music | `systemctl restart fake-yuki-music` |
| Nav | `systemctl restart fake-star-nav` |
| Caddy | `systemctl reload caddy` |

### Verify

```bash
curl -s -w '%{http_code}' https://fake-star.xyz/ -o /dev/null && echo " home"
curl -s -w '%{http_code}' https://music.fake-star.xyz/api/songs -o /dev/null && echo " music"
curl -s -w '%{http_code}' https://bookmarks.fake-star.xyz/api/bookmarks -o /dev/null && echo " bookmarks"
```

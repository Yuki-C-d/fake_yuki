from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
from apps.bookmarks.backend import models


class BookmarkIn(BaseModel):
    name: str
    url: str
    icon: str = ""
    tag: str = "工具"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    models.init_db()
    yield


app = FastAPI(title="fake-star 书签", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/")
def index():
    with open("apps/nav/frontend/index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read(), headers={"Cache-Control": "no-cache, no-store, must-revalidate"})


@app.get("/wallpaper.jpg")
def wallpaper():
    path = "apps/nav/frontend/wallpaper.jpg"
    if os.path.exists(path):
        return FileResponse(path, headers={"Cache-Control": "public, max-age=86400"})
    return HTMLResponse("", status_code=404)


@app.get("/api/bookmarks")
def list_bookmarks():
    return models.list_all()


@app.post("/api/bookmarks")
def add_bookmark(body: BookmarkIn):
    bid = models.add(body.name, body.url, body.icon, body.tag)
    return {"id": bid, "status": "ok"}


@app.put("/api/bookmarks/{bid}")
def update_bookmark(bid: int, body: BookmarkIn):
    models.update(bid, body.name, body.url, body.icon, body.tag)
    return {"status": "ok"}


@app.delete("/api/bookmarks/{bid}")
def delete_bookmark(bid: int):
    models.delete(bid)
    return {"status": "ok"}

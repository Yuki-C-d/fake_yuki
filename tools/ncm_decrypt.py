#!/usr/bin/env python3
"""NCM 解密工具 — Linux 版"""
import sys, os, struct, json, base64
from Crypto.Cipher import AES

MAGIC = b"CTENFDAM"
CORE_KEY = bytes.fromhex("687A4852416D736F356E496769723230")  # hzHRAmso5nIgir20
META_KEY = bytes.fromhex("2331346C6A6B5F215C5D2630553C2728")  # #14ljk_!\]&0U<'(


def unpad(s: bytes) -> bytes:
    pad = s[-1]
    if 0 < pad <= 16:
        return s[:-pad]
    return s


def dump(filepath: str) -> str:
    with open(filepath, "rb") as f:
        data = f.read()

    if data[:8] != MAGIC:
        raise ValueError("不是有效的 NCM 文件")

    # 2. 读取加密密钥长度和数据
    key_len = struct.unpack_from("<I", data, 10)[0]
    key_data = bytearray(data[14 : 14 + key_len])

    # RC4-KSA 解密密钥
    for i in range(len(key_data)):
        key_data[i] ^= 0x64

    # AES-128-ECB 解密得到实际密钥
    cipher = AES.new(CORE_KEY, AES.MODE_ECB)
    decrypt_data = bytearray(cipher.decrypt(bytes(key_data)))
    # 去掉 "neteasecloudmusic" 前缀 (17 bytes)
    key_box = decrypt_data[17:]

    # 3. 解析 meta info
    offset = 14 + key_len
    meta_len = struct.unpack_from("<I", data, offset)[0]
    offset += 4
    meta = json.loads(data[offset : offset + meta_len])
    offset += meta_len

    # 4. 跳过封面 (5 = 1 byte gap + 4 bytes size)
    offset += 5
    cover_size = struct.unpack_from("<I", data, offset)[0]
    offset += 4 + cover_size

    # 5. AES-128-CBC 解密音乐数据
    music_data = data[offset:]
    iv = b"0102030405060708"
    cipher2 = AES.new(bytes(key_box), AES.MODE_CBC, iv=iv)
    decrypted = unpad(bytearray(cipher2.decrypt(music_data)))

    # 6. 根据 meta 判断格式
    out_format = meta.get("format", "flac")
    out_ext = {"mp3": ".mp3", "flac": ".flac"}.get(out_format, ".flac")
    base = os.path.splitext(filepath)[0]
    out_path = base + out_ext

    with open(out_path, "wb") as f:
        f.write(decrypted)

    return out_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"用法: {sys.argv[0]} <文件.ncm>", file=sys.stderr)
        sys.exit(1)
    out = dump(sys.argv[1])
    print(out)

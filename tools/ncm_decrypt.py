#!/usr/bin/env python3
"""NCM 解密工具 — Linux 版 (取代 ncmdump.exe)"""
import sys, os, json, struct
from Crypto.Cipher import AES

MAGIC = b"CTENFDAM"


def dump(filepath: str) -> str:
    """解密 .ncm 文件，返回解密后的文件路径"""
    with open(filepath, "rb") as f:
        data = f.read()

    # 1. 验证魔数
    if data[:8] != MAGIC:
        raise ValueError("不是有效的 NCM 文件")

    # 2. 读取 key 长度和加密的 key 数据
    key_len = struct.unpack_from("<I", data, 8)[0]
    key_data = bytearray(data[12 : 12 + key_len])
    for i in range(len(key_data)):
        key_data[i] ^= 0x64

    cipher = AES.new(b"687a4852416d736f356e496769723230", AES.MODE_ECB)
    decrypt_key = cipher.decrypt(bytes(key_data))

    # 3. 跳过 meta 信息
    offset = 12 + key_len
    meta_len = struct.unpack_from("<I", data, offset)[0]
    offset += 4 + meta_len

    # 4. 跳过封面图 (5 字节长度 + 数据)
    offset += 5
    cover_size = struct.unpack_from("<I", data, offset)[0]
    offset += 4 + cover_size

    # 5. 解密音乐数据
    music_data = data[offset:]
    cipher2 = AES.new(decrypt_key[17:], AES.MODE_CBC, iv=b"0102030405060708")
    decrypted = bytearray(cipher2.decrypt(music_data))

    # 6. 去 padding
    pad = decrypted[-1]
    if pad > 0 and pad <= 16:
        decrypted = decrypted[:-pad]

    # 7. 写入输出文件（同目录，改后缀）
    base = os.path.splitext(filepath)[0]
    out_path = base + ".flac"  # NCM 源基本都是 FLAC
    with open(out_path, "wb") as f:
        f.write(decrypted)

    # 8. 尝试验证输出格式，非 FLAC 则试 mp3
    with open(out_path, "rb") as f:
        header = f.read(4)
    if header[:4] != b"fLaC":
        new_path = base + ".mp3"
        os.rename(out_path, new_path)
        out_path = new_path

    return out_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"用法: {sys.argv[0]} <文件.ncm>")
        sys.exit(1)
    out = dump(sys.argv[1])
    print(out)

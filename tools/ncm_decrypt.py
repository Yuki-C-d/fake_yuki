#!/usr/bin/env python3
"""NCM 解密 — 基于 ncmdump 库"""
import sys, os
sys.path.insert(0, '/usr/local/lib/python3.10/dist-packages')
from ncmdump import dump as ncm_dump

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: ncm_decrypt.py <文件>', file=sys.stderr)
        sys.exit(1)
    src = sys.argv[1]
    if not os.path.exists(src):
        print(f'文件不存在: {src}', file=sys.stderr)
        sys.exit(1)
    try:
        out = ncm_dump(src)
        # ncmdump 输出同目录同名 .m4a
        base = os.path.splitext(src)[0]
        for ext in ['.m4a', '.flac', '.mp3']:
            candidate = base + ext
            if os.path.exists(candidate):
                print(candidate)
                sys.exit(0)
        print(f'解密完成但未找到输出文件 (base={base})', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'解密失败: {e}', file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

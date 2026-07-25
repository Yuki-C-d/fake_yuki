import struct, zlib, os

def create_png(size, color):
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    header = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0))

    raw = b''
    r, g, b = color
    for y in range(size):
        raw += b'\x00'  # filter none
        for x in range(size):
            cx, cy = x - size//2, y - size//2
            d = (cx*cx + cy*cy) ** 0.5
            r2 = size * 0.38
            if d < r2:
                raw += bytes([min(r+50, 255), min(g+50, 255), min(b+50, 255)])
            elif d < r2 + size * 0.05:
                raw += bytes([200, 200, 200])
            else:
                raw += bytes([r, g, b])

    idat = chunk(b'IDAT', zlib.compress(raw))
    iend = chunk(b'IEND', b'')

    path = os.path.join(os.path.dirname(__file__), f'icon{size}.png')
    with open(path, 'wb') as f:
        f.write(header + ihdr + idat + iend)

base = (42, 52, 72)  # #2A3448 dark blue
create_png(16, base)
create_png(48, base)
create_png(128, base)
print('icons done')

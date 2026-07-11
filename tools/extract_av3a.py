"""从 MP4 容器中提取 raw AV3A 流 (mdat box)"""
import struct, sys, os

def extract_mdat(filepath, outpath):
    with open(filepath, 'rb') as f:
        data = f.read()
    pos = 0
    while pos + 8 <= len(data):
        size, boxtype = struct.unpack('>I4s', data[pos:pos+8])
        name = boxtype.decode('ascii', errors='replace')
        if size == 1:
            size = struct.unpack('>Q', data[pos+8:pos+16])[0]
            hdr = 16
        elif size == 0:
            size = len(data) - pos
            hdr = 8
        else:
            hdr = 8
        if name == 'mdat':
            offset = pos + hdr
            length = size - hdr
            with open(outpath, 'wb') as out:
                out.write(data[offset:offset+length])
            return length
        pos += size
    raise RuntimeError(f"No mdat box found in {filepath}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.mp4> <output.av3a>")
        sys.exit(1)
    size = extract_mdat(sys.argv[1], sys.argv[2])
    print(f"Extracted {size} bytes")

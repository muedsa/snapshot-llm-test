#!/usr/bin/env python3
"""Minimal PNG RGBA8 decoder + sampling helpers (no third-party deps)."""
import struct, zlib
from pathlib import Path

class PNG:
    def __init__(self, path):
        data = Path(path).read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
        pos = 8
        self.idat = b""
        self.w = self.h = self.bitdepth = self.colortype = None
        while pos < len(data):
            length = struct.unpack(">I", data[pos:pos + 4])[0]
            typ = data[pos + 4:pos + 8]
            chunk = data[pos + 8:pos + 8 + length]
            if typ == b"IHDR":
                self.w, self.h, self.bitdepth, self.colortype, comp, filt, inter = struct.unpack(">IIBBBBB", chunk)
                assert self.bitdepth == 8 and self.colortype == 6 and inter == 0, (self.bitdepth, self.colortype, inter)
            elif typ == b"IDAT":
                self.idat += chunk
            elif typ == b"IEND":
                break
            pos += 12 + length
        raw = zlib.decompress(self.idat)
        bpp = 4
        stride = self.w * bpp
        self.px = bytearray(self.w * self.h * bpp)
        prev = bytearray(stride)
        p = 0
        for y in range(self.h):
            f = raw[p]; p += 1
            line = bytearray(raw[p:p + stride]); p += stride
            if f == 1:
                for i in range(bpp, stride):
                    line[i] = (line[i] + line[i - bpp]) & 255
            elif f == 2:
                for i in range(stride):
                    line[i] = (line[i] + prev[i]) & 255
            elif f == 3:
                for i in range(stride):
                    a = line[i - bpp] if i >= bpp else 0
                    line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
            elif f == 4:
                for i in range(stride):
                    a = line[i - bpp] if i >= bpp else 0
                    b = prev[i]
                    c = prev[i - bpp] if i >= bpp else 0
                    pp = a + b - c
                    pa, pb, pc = abs(pp - a), abs(pp - b), abs(pp - c)
                    pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                    line[i] = (line[i] + pr) & 255
            self.px[y * stride:(y + 1) * stride] = line
            prev = line

    def pixel(self, x, y):
        i = (y * self.w + x) * 4
        return tuple(self.px[i:i + 4])

def color_bbox(png, x0, y0, x1, y1, colors, tol=14, alpha_min=200):
    xs, ys = [], []
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b, a = png.pixel(x, y)
            if a < alpha_min:
                continue
            for cr, cg, cb in colors:
                if abs(r - cr) <= tol and abs(g - cg) <= tol and abs(b - cb) <= tol:
                    xs.append(x); ys.append(y); break
    if not xs:
        return None
    return [min(xs), min(ys), max(xs) + 1, max(ys) + 1]

def rgb(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))

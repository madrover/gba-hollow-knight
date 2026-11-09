#!/usr/bin/env python3
"""Generates placeholder art (4bpp indexed BMPs) into graphics/.

Run from the project root: python3 tools/make_placeholder_art.py
Replace the generated BMPs with real art whenever you like; keep them 4bpp
(16 colors) with color 0 as the transparent color.
"""

import os
import struct

GRAPHICS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'graphics')


def write_bmp_4bpp(path, width, height, palette, pixels):
    """pixels: list of rows (top to bottom), each a list of palette indices (0-15)."""
    assert len(palette) == 16, 'palette must have 16 colors'
    assert len(set(palette)) == 16, 'palette colors must be unique'
    assert len(pixels) == height and all(len(row) == width for row in pixels)

    row_size = ((width * 4 + 31) // 32) * 4
    image = bytearray()

    for row in reversed(pixels):  # BMP rows are stored bottom-up
        packed = bytearray()
        for x in range(0, width, 2):
            hi = row[x]
            lo = row[x + 1] if x + 1 < width else 0
            packed.append((hi << 4) | lo)
        packed.extend(b'\0' * (row_size - len(packed)))
        image.extend(packed)

    palette_data = b''.join(struct.pack('<BBBB', b, g, r, 0) for (r, g, b) in palette)
    offset = 14 + 40 + len(palette_data)

    with open(path, 'wb') as f:
        f.write(struct.pack('<2sIHHI', b'BM', offset + len(image), 0, 0, offset))
        f.write(struct.pack('<IiiHHIIiiII', 40, width, height, 1, 4, 0, len(image), 2835, 2835, 16, 16))
        f.write(palette_data)
        f.write(image)


def grid(rows, legend):
    return [[legend[c] for c in row] for row in rows]


def filler_colors(used, count):
    # Unused palette slots still need unique colors.
    return [(1, 1 + i, 2 + i) for i in range(count - len(used))]


# ---------------------------------------------------------------------------------------------------------------------
# Knight: 16x32 frames stacked vertically. Faces right; the cloak tail trails to the left.
# ---------------------------------------------------------------------------------------------------------------------

KNIGHT_PALETTE = [
    (255, 0, 255),    # 0 transparent
    (10, 10, 20),     # 1 K black (eyes, legs, outline)
    (240, 240, 236),  # 2 W mask
    (172, 178, 196),  # 3 G mask shade
    (36, 40, 66),     # 4 C cloak dark
    (60, 68, 108),    # 5 M cloak mid
]
KNIGHT_PALETTE += filler_colors(KNIGHT_PALETTE, 16)

KNIGHT_LEGEND = {'.': 0, 'K': 1, 'W': 2, 'G': 3, 'C': 4, 'M': 5}

HEAD = [
    "...W........W...",
    "...WW......WW...",
    "...WW......WW...",
    "...WWW....WWW...",
    "...WWWWWWWWWW...",
    "..WWWWWWWWWWWW..",
    "..WWWWWWWWWWWW..",
    "..WWKKWWWWKKWW..",
    "..WWKKWWWWKKWW..",
    "..WWKKWWWWKKWW..",
    "..GWWWWWWWWWWG..",
    "...GWWWWWWWWG...",
    "....GGWWWWGG....",
]

BODY = [
    "....CCCCCCCC....",
    "...CCMMMMMMCC...",
    "..CCMMMMMMMMCC..",
    "..CMMMMMMMMMMC..",
    "..CMMMMMMMMMMC..",
    ".CCMMMMMMMMMMC..",
    ".CCMMMMMMMMMCC..",
    "CCCCMMMMMMMCCC..",
    ".CCCCMMMMMCCC...",
    "...CCCCCCCCCC...",
    "....CCCCCCCC....",
]

BODY_FLARED = [  # falling: cloak billows outwards
    "....CCCCCCCC....",
    "...CCMMMMMMCC...",
    "..CCMMMMMMMMCC..",
    "..CMMMMMMMMMMC..",
    ".CCMMMMMMMMMMCC.",
    ".CMMMMMMMMMMMMC.",
    "CCMMMMMMMMMMMMCC",
    "CCCMMMMMMMMMMCCC",
    "CC.CCCMMMMCCC.CC",
    "....CCCCCCCC....",
    "................",
]

LEGS = {
    'stand': ["....KK....KK....", "....KK....KK....", "....KK....KK....", "....KKK...KKK..."],
    'run0':  ["....KK....KK....", "...KK......KK...", "..KK........KKK.", "..K............."],
    'run1':  ["....KK...KK.....", "....KK...KK.....", "....KK....KK....", "....KKK...KKK..."],
    'run2':  ["....KK....KK....", "...KK......KK...", ".KKK........KK..", "..............K."],
    'run3':  [".....KK..KK.....", ".....KK..KK.....", "....KK....KK....", "....KKK...KKK..."],
    'jump':  ["...KKK....KKK...", "....KKK..KKK....", "................", "................"],
    'fall':  ["...KK......KK...", "..KK........KK..", "..K..........K..", "................"],
}

TOP_PADDING = 4  # empty rows above the horns


def knight_frame(legs, body=BODY, bob=0):
    rows = ["." * 16] * (TOP_PADDING + bob) + HEAD + body + LEGS[legs]
    rows = rows[:32]
    assert len(rows) == 32, len(rows)
    for row in rows:
        assert len(row) == 16, row
    return rows


# Frame order must match the knight_frames constants in include/knight.h.
KNIGHT_FRAMES = [
    knight_frame('stand'),                 # 0 idle
    knight_frame('stand', bob=1),          # 1 idle (breathing)
    knight_frame('run0'),                  # 2 run
    knight_frame('run1', bob=1),           # 3 run
    knight_frame('run2'),                  # 4 run
    knight_frame('run3', bob=1),           # 5 run
    knight_frame('jump'),                  # 6 jump (rising)
    knight_frame('fall', body=BODY_FLARED),  # 7 fall
]


# ---------------------------------------------------------------------------------------------------------------------
# Room tiles: 8x8 each, laid out horizontally. Index order must match room.cpp.
# ---------------------------------------------------------------------------------------------------------------------

BG_PALETTE = [
    (16, 20, 34),     # 0 transparent (backdrop color is set in code)
    (14, 16, 28),     # 1 D deep shadow
    (30, 36, 58),     # 2 R rock
    (46, 54, 84),     # 3 L rock light
    (104, 116, 156),  # 4 E edge highlight
    (160, 172, 210),  # 5 H bright highlight
]
BG_PALETTE += filler_colors(BG_PALETTE, 16)

BG_LEGEND = {'.': 0, 'D': 1, 'R': 2, 'L': 3, 'E': 4, 'H': 5}

TILES = [
    [  # 0 empty
        "........", "........", "........", "........",
        "........", "........", "........", "........",
    ],
    [  # 1 rock fill
        "RRRRDRRR", "RLRRRRRR", "RRRRRRDR", "RRDRRRRR",
        "RRRRRLRR", "DRRRRRRR", "RRRRDRRR", "RRLRRRRD",
    ],
    [  # 2 rock fill (variation)
        "RRRRRRRR", "RRDRRRLR", "RRRRRRRR", "RLRRRDRR",
        "RRRRRRRR", "RRRDRRRR", "RLRRRRRR", "RRRRRRDR",
    ],
    [  # 3 rock surface (exposed top)
        "HEHEEHEH", "EEEEEEEE", "LLLLLLLL", "RLRRRRLR",
        "RRRDRRRR", "RRRRRRRR", "RRRRRDRR", "DRRRRRRR",
    ],
    [  # 4 rock underside (exposed bottom)
        "RRRDRRRR", "RRRRRRLR", "RRRRRRRR", "RDRRRRRR",
        "RRRRRRRR", "DRRDRRRD", "DDDDDDDD", "D.D.DD.D",
    ],
]


def main():
    os.makedirs(GRAPHICS_DIR, exist_ok=True)

    knight_rows = [row for frame in KNIGHT_FRAMES for row in frame]
    write_bmp_4bpp(os.path.join(GRAPHICS_DIR, 'knight.bmp'), 16, 32 * len(KNIGHT_FRAMES), KNIGHT_PALETTE,
                   grid(knight_rows, KNIGHT_LEGEND))

    tile_rows = [''.join(tile[y] for tile in TILES) for y in range(8)]
    write_bmp_4bpp(os.path.join(GRAPHICS_DIR, 'room_tiles.bmp'), 8 * len(TILES), 8, BG_PALETTE,
                   grid(tile_rows, BG_LEGEND))

    palette_rows = ["01234567", "89abcdef"] * 4
    write_bmp_4bpp(os.path.join(GRAPHICS_DIR, 'room_palette.bmp'), 8, 8, BG_PALETTE,
                   [[int(c, 16) for c in row] for row in palette_rows])

    print('Wrote knight.bmp, room_tiles.bmp, room_palette.bmp to', os.path.normpath(GRAPHICS_DIR))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Generates the game's pixel art (4bpp indexed BMPs) into graphics/.

Run from the project root: python3 tools/make_art.py

Everything is drawn from text grids or simple procedural rules, so the art is reproducible and easy to tweak.
Generated files:
  knight.bmp        32x32 Knight frames stacked vertically (frame order must match src/knight.cpp)
  slash.bmp         32x32 nail slash frames stacked vertically (frame order must match src/knight.cpp)
  room_tiles.bmp    8x8 rock tiles laid out horizontally (order must match src/room.cpp)
  room_palette.bmp  palette for room_tiles
  cave_bg.bmp       256x256 horizontally tileable far background (parallax layer)

All images are 4bpp (16 colors); color 0 is transparent.
"""

import math
import os
import random
import struct

GRAPHICS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'graphics')


def write_bmp_4bpp(path, width, height, palette, pixels):
    """pixels: list of rows (top to bottom), each a list of palette indices (0-15)."""
    palette = palette + filler_colors(palette)
    assert len(palette) == 16, 'palette must have at most 16 colors'
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


def filler_colors(used):
    # Unused palette slots still need unique colors.
    return [(1, 1 + i, 2 + i) for i in range(16 - len(used))]


def grid(rows, legend):
    return [[legend[c] for c in row] for row in rows]


def row(start, content, width=32):
    """A row of `width` pixels with `content` placed at column `start`."""
    result = '.' * start + content
    assert len(result) <= width, (start, content)
    return result + '.' * (width - len(result))


def mirrored(half_rows):
    """Builds symmetric rows from their left halves."""
    return [half + half[::-1] for half in half_rows]


# ---------------------------------------------------------------------------------------------------------------------
# Knight: 32x32 frames. Faces right; the cloak tail trails to the left.
# Big horned mask, tall oval eyes, small bell-shaped cloak, thin legs.
# ---------------------------------------------------------------------------------------------------------------------

KNIGHT_PALETTE = [
    (255, 0, 255),    # 0 transparent
    (12, 10, 22),     # 1 K outline, eyes, legs
    (238, 238, 232),  # 2 W mask
    (188, 190, 206),  # 3 S mask shade
    (34, 38, 62),     # 4 C cloak dark
    (54, 60, 96),     # 5 M cloak mid
    (82, 92, 136),    # 6 L cloak light rim
]

KNIGHT_LEGEND = {'.': 0, 'K': 1, 'W': 2, 'S': 3, 'C': 4, 'M': 5, 'L': 6}

# Left halves (16 px) of the head rows 0..22; the right half is mirrored.
HEAD = mirrored([
    "................",
    ".......K........",
    ".......KK.......",
    ".......KWK......",
    ".......KWK......",
    ".......KWWK.....",
    "........KWWK....",
    "........KWWK....",
    "........KWWWKKKK",
    ".......KWWWWWWWW",
    "......KWWWWWWWWW",
    "......KWWWWWWWWW",
    "......KWWWWWWWWW",
    "......KWWWKKWWWW",
    "......KWWKKKKWWW",
    "......KWWKKKKWWW",
    "......KWWKKKKWWW",
    "......KSWKKKKWWW",
    ".......KSWKKWWWW",
    ".......KSSWWWWWW",
    "........KSSSWWWW",
    ".........KKSSSSS",
    "...........KKKKK",
])

EYE_ROWS = range(13, 19)
EYE_SHIFT = 2


def face_right(head):
    """Shifts the eyes toward the facing side so the horizontal flip reads as turning around.

    Far-side eye pixels that would touch the mask outline are dropped, leaving that eye slightly narrower.
    """
    result = list(head)
    for y in EYE_ROWS:
        r = head[y]
        first, last = r.index('K'), r.rindex('K')
        eyes = [x for x in range(first + 1, last) if r[x] == 'K']
        cleared = list(r[:first + 1] + r[first + 1:last].replace('K', 'W') + r[last:])
        shifted = list(cleared)
        for x in eyes:
            nx = x + EYE_SHIFT
            if cleared[nx] == 'W' and cleared[nx + 1] == 'W':
                shifted[nx] = 'K'
        result[y] = ''.join(shifted)
    return result


HEAD = face_right(HEAD)

# Cloak rows 23..28 (6 rows).
CLOAKS = {
    'rest': [
        row(11, "KCCCCCCCCK"),
        row(10, "KCMMMMMMLLCK"),
        row(9, "KCMMMMMMMMLLCK"),
        row(8, "KCCMMMMMMMMMLCK"),
        row(7, "KCCCMMMMMMMMMCCK"),
        row(6, "KCCKCCMMMMMMCCCK"),
    ],
    'run_a': [  # cloak tail swept back
        row(11, "KCCCCCCCCK"),
        row(9, "KCCMMMMMMLLCK"),
        row(7, "KCCCMMMMMMMMLLCK"),
        row(5, "KCCCCMMMMMMMMMLCK"),
        row(4, "KCCKKCCMMMMMMMCCK"),
        row(8, "KKCCCMMMMMCCCK"),
    ],
    'run_b': [  # cloak tail settling
        row(11, "KCCCCCCCCK"),
        row(10, "KCMMMMMMLLCK"),
        row(8, "KCCMMMMMMMMLLCK"),
        row(6, "KCCCMMMMMMMMMLCK"),
        row(6, "KCCCCMMMMMMMCCCK"),
        row(7, "KKKCCMMMMMCCCK"),
    ],
    'jump': [  # hem pulled up and narrow
        row(11, "KCCCCCCCCK"),
        row(10, "KCMMMMMMLLCK"),
        row(9, "KCMMMMMMMMLLCK"),
        row(9, "KCCMMMMMMMLCCK"),
        row(10, "KCCCCCCCCCCK"),
        row(11, "KK.KKKK.KK"),
    ],
    'fall': [  # cloak billows upwards and outwards
        row(11, "KCCCCCCCCK"),
        row(8, "KKCMMMMMMLLCKK"),
        row(5, "KCCCMMMMMMMMMMLCCCK"),
        row(4, "KCCMMMMMMMMMMMMMCCK"),
        row(4, "KC..KCCMMMMMMCCK..CK"),
        row(4, "K......KKKKKK.....K"),
    ],
}

# Leg rows 29..31 (3 rows).
LEGS = {
    'stand': [row(12, "KK....KK"), row(12, "KK....KK"), row(11, "KKK....KKK")],
    'run0':  [row(12, "KK....KK"), row(10, "KK........KK"), row(9, "KK..........KK")],
    'run1':  [row(13, "KK..KK"), row(13, "KK..KK"), row(12, "KKK.KKK")],
    'run2':  [row(11, "KK.....KK"), row(13, "KK.....KK"), row(14, "KK.....KKK")],
    'run3':  [row(14, "KKKK"), row(13, "KK..KK"), row(12, "KKK.KKK")],
    'jump':  [row(12, "KKK..KKK"), row(13, "KK..KK"), row(0, "")],
    'fall':  [row(11, "KK......KK"), row(11, "KK......KK"), row(10, "K..........K")],
}


def knight_frame(cloak, legs, bob=False):
    head = HEAD
    body = CLOAKS[cloak]

    if bob:
        # Breathing / stride squash: head drops 1 px, the cloak loses its top (collar) row.
        head = [row(0, "")] + head
        body = body[1:]

    rows = head + body + LEGS[legs]
    assert len(rows) == 32, len(rows)
    for r in rows:
        assert len(r) == 32, r
    return rows


def overlay(rows, y, x, content):
    """Draws `content` over `rows` at (x, y); '.' in `content` keeps the pixel below."""
    rows = list(rows)
    r = list(rows[y])
    for i, c in enumerate(content):
        if c != '.':
            r[x + i] = c
    rows[y] = ''.join(r)
    return rows


def with_nail(rows):
    """The nail held out in front at cloak height, gripped at the cloak edge."""
    rows = overlay(rows, 24, 22, "KKKKKKKKK")
    rows = overlay(rows, 25, 21, "KSWWWWWWWWK")
    return overlay(rows, 26, 22, "KKKKKKKKK")


# Frame order must match the frame constants in src/knight.cpp.
KNIGHT_FRAMES = [
    knight_frame('rest', 'stand'),             # 0 idle
    knight_frame('rest', 'stand', bob=True),   # 1 idle (breathing)
    knight_frame('run_a', 'run0'),             # 2 run
    knight_frame('run_b', 'run1', bob=True),   # 3 run
    knight_frame('run_a', 'run2'),             # 4 run
    knight_frame('run_b', 'run3', bob=True),   # 5 run
    knight_frame('jump', 'jump'),              # 6 jump (rising)
    knight_frame('fall', 'fall'),              # 7 fall
    with_nail(knight_frame('run_a', 'run0')),  # 8 attack (grounded lunge)
    with_nail(knight_frame('jump', 'jump')),   # 9 attack (airborne)
]


# ---------------------------------------------------------------------------------------------------------------------
# Nail slash: 32x32 frames of a white crescent swinging top to bottom, opening towards the Knight (drawn facing right).
# ---------------------------------------------------------------------------------------------------------------------

SLASH_PALETTE = [
    (255, 0, 255),    # 0 transparent
    (244, 244, 238),  # 1 core
    (184, 194, 220),  # 2 pale
    (112, 122, 164),  # 3 fading
]

SLASH_SIZE = 32


def slash_frame(min_angle, max_angle, fading):
    """Crescent pixels whose angle (degrees, -90 top .. 90 bottom) around the arc center is in range."""
    cx, cy = 4, 16
    pixels = [[0] * SLASH_SIZE for _ in range(SLASH_SIZE)]
    for y in range(SLASH_SIZE):
        for x in range(SLASH_SIZE):
            outer = ((x - cx) / 26) ** 2 + ((y - cy) / 15) ** 2
            inner = ((x - cx + 5) / 24) ** 2 + ((y - cy) / 12) ** 2
            if outer > 1 or inner <= 1:
                continue
            angle = math.degrees(math.atan2(y - cy, x - cx))
            if not min_angle <= angle <= max_angle:
                continue
            edge = outer > 0.8 or inner < 1.15
            pixels[y][x] = (3 if edge else 2) if fading else (2 if edge else 1)
    return pixels


# Frame order must match the slash constants in src/knight.cpp.
SLASH_FRAMES = [
    slash_frame(-90, -15, False),  # 0 swing starts above
    slash_frame(-90, 90, False),   # 1 full arc
    slash_frame(15, 90, True),     # 2 tail fades below
]


# ---------------------------------------------------------------------------------------------------------------------
# Room tiles: Forgotten Crossroads style rock (dark blue-gray with a pale outline on exposed edges).
# Only left-facing variants are drawn; right-facing ones use the map cell's horizontal flip.
# ---------------------------------------------------------------------------------------------------------------------

ROOM_PALETTE = [
    (16, 19, 32),     # 0 transparent
    (10, 12, 22),     # 1 K outline
    (20, 23, 38),     # 2 D deep
    (34, 40, 62),     # 3 R rock
    (48, 56, 86),     # 4 L rock light
    (100, 112, 150),  # 5 E edge
    (176, 188, 222),  # 6 H highlight
]

ROOM_LEGEND = {'.': 0, 'K': 1, 'D': 2, 'R': 3, 'L': 4, 'E': 5, 'H': 6}

# Order must match the tile constants in src/room.cpp.
ROOM_TILES = [
    [  # 0 empty
        "........", "........", "........", "........", "........", "........", "........", "........",
    ],
    [  # 1 fill
        "RRRRDRRR", "RLRRRRRR", "RRRRRRDR", "RRDRRRRR", "RRRRRLRR", "DRRRRRRR", "RRRRDRRR", "RRLRRRRD",
    ],
    [  # 2 fill (variation)
        "RRRRRRRR", "RRDRRRLR", "RRRRRRRR", "RLRRRDRR", "RRRRRRRR", "RRRDRRRR", "RLRRRRRR", "RRRRRRDR",
    ],
    [  # 3 top surface
        "HHHHHHHH", "EEEEEEEE", "LLLLLLLL", "RLRRRRLR", "RRRRRRRR", "RRDRRRRR", "RRRRRRDR", "RRRRRRRR",
    ],
    [  # 4 underside
        "RRRDRRRR", "RRRRRRLR", "RRRRRRRR", "RDRRRRRR", "RRRRRRRR", "DRRDRRRD", "DDDDDDDD", "KKKKKKKK",
    ],
    [  # 5 left wall face
        "ELRRRRRR", "ELRRRDRR", "ELRRRRRR", "ELRRRRRR", "ELRDRRRR", "ELRRRRRR", "ELRRRRDR", "ELRRRRRR",
    ],
    [  # 6 top-left rounded corner
        "...HHHHH", "..HEEEEE", ".HELLLLL", "HELRRRLR", "HLRRRRRR", "ELRDRRRR", "ELRRRRDR", "ELRRRRRR",
    ],
    [  # 7 bottom-left rounded corner
        "ELRRRRRR", "ELRRRDRR", "ELRRRRRR", "EDRRRRRR", ".KDRRRRR", "..KDDDDD", "...KKKKK", "........",
    ],
    [  # 8 thin platform (exposed top and bottom)
        "HHHHHHHH", "EEEEEEEE", "LLLLLLLL", "RRLRRRRR", "RRRRRDRR", "DRRRRRRD", "DDDDDDDD", "KKKKKKKK",
    ],
    [  # 9 thin platform left end
        "..HHHHHH", ".HEEEEEE", "HELLLLLL", "ELRRLRRR", "ELRRRRDR", ".DRRRRRD", "..DDDDDD", "...KKKKK",
    ],
]


# ---------------------------------------------------------------------------------------------------------------------
# Cave background: far, dim stalactites and stalagmites, horizontally tileable (the bg wraps while scrolling).
# Large flat color areas keep the number of unique 8x8 tiles low.
# ---------------------------------------------------------------------------------------------------------------------

CAVE_PALETTE = [
    (16, 19, 32),     # 0 transparent (never used: the far wall is fully opaque)
    (13, 15, 26),     # 1 far wall
    (19, 22, 37),     # 2 distant rock
    (25, 29, 48),     # 3 nearer rock
    (31, 36, 58),     # 4 nearer rock rim
    (96, 120, 170),   # 5 lumafly glow
    (52, 64, 98),     # 6 lumafly halo
]

CAVE_SIZE = 256


def draw_cave_bg():
    rng = random.Random(1337)
    size = CAVE_SIZE
    pixels = [[1] * size for _ in range(size)]

    def column_span(x0, half_width, length, from_top, color, rim):
        for dy in range(length):
            # Taper towards the tip.
            t = dy / max(1, length - 1)
            w = max(0, round(half_width * (1 - t) ** 0.8))
            y = dy if from_top else size - 1 - dy
            for dx in range(-w, w + 1):
                x = (x0 + dx) % size
                is_rim = rim is not None and dx == w and w > 0
                pixels[y][x] = rim if is_rim else color

    # Two depth layers: distant first, nearer on top.
    for color, rim, count, widths, lengths in (
        (2, None, 14, (6, 18), (40, 120)),
        (3, 4, 9, (4, 12), (30, 90)),
    ):
        for _ in range(count):
            x0 = rng.randrange(size)
            column_span(x0, rng.randint(*widths), rng.randint(*lengths), True, color, rim)
        for _ in range(count):
            x0 = rng.randrange(size)
            column_span(x0, rng.randint(*widths), rng.randint(*lengths) // 2, False, color, rim)

    # A few lumaflies (glowing bugs) scattered in the dark.
    for _ in range(10):
        x, y = rng.randrange(size), rng.randrange(40, size - 40)
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            pixels[(y + dy) % size][(x + dx) % size] = 6
        pixels[y][x] = 5

    return pixels


def main():
    os.makedirs(GRAPHICS_DIR, exist_ok=True)

    knight_rows = [r for frame in KNIGHT_FRAMES for r in frame]
    write_bmp_4bpp(os.path.join(GRAPHICS_DIR, 'knight.bmp'), 32, 32 * len(KNIGHT_FRAMES), KNIGHT_PALETTE,
                   grid(knight_rows, KNIGHT_LEGEND))

    slash_rows = [r for frame in SLASH_FRAMES for r in frame]
    write_bmp_4bpp(os.path.join(GRAPHICS_DIR, 'slash.bmp'), SLASH_SIZE, SLASH_SIZE * len(SLASH_FRAMES), SLASH_PALETTE,
                   slash_rows)

    tile_rows = [''.join(tile[y] for tile in ROOM_TILES) for y in range(8)]
    write_bmp_4bpp(os.path.join(GRAPHICS_DIR, 'room_tiles.bmp'), 8 * len(ROOM_TILES), 8, ROOM_PALETTE,
                   grid(tile_rows, ROOM_LEGEND))

    palette_rows = ["01234567", "89abcdef"] * 4
    write_bmp_4bpp(os.path.join(GRAPHICS_DIR, 'room_palette.bmp'), 8, 8, ROOM_PALETTE,
                   [[int(c, 16) for c in r] for r in palette_rows])

    write_bmp_4bpp(os.path.join(GRAPHICS_DIR, 'cave_bg.bmp'), CAVE_SIZE, CAVE_SIZE, CAVE_PALETTE, draw_cave_bg())

    print('Wrote knight.bmp, slash.bmp, room_tiles.bmp, room_palette.bmp, cave_bg.bmp to', os.path.normpath(GRAPHICS_DIR))


if __name__ == '__main__':
    main()

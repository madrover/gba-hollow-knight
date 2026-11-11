# Hollow GBA

A Hollow Knight–inspired fan platformer for the Game Boy Advance, built with [Butano](https://github.com/GValiente/butano) on top of devkitPro's devkitARM.

Hollow Knight is © Team Cherry. This is an unofficial fan project and is not affiliated with Team Cherry.

## Setup (macOS, once)

1. Install devkitPro pacman: download `devkitpro-pacman-installer.pkg` from https://github.com/devkitPro/pacman/releases and run it.
2. Install the GBA toolchain: `sudo dkp-pacman -Sy && sudo dkp-pacman -S gba-dev`
3. Install the mGBA emulator: `brew install --cask mgba`

No shell profile changes are needed: the Makefile defaults `DEVKITPRO` to `/opt/devkitpro`.

## Build and run

```sh
make -j8                       # produces hollow-gba.gba
open -a mGBA hollow-gba.gba
make clean                     # removes build artifacts
```

## Controls

- D-pad left/right: run
- A: nail attack (slashes in the facing direction; works in the air too)
- B: jump (hold for higher jumps)

mGBA's default keyboard mapping is arrow keys for the D-pad, X for A and Z for B. To jump with X and attack with Space, remap A to Space and B to X in mGBA's Settings > Controllers (or set `keyA=32` and `keyB=88` under `[gba.input.QT_K]` in `~/.config/mgba/config.ini` while mGBA is closed).

## Art

`tools/make_art.py` generates all the art in `graphics/` from text pixel grids and simple procedural rules:

- `knight.bmp`: 32x32 Knight frames stacked vertically (idle, run, jump, fall)
- `room_tiles.bmp` + `room_palette.bmp`: Crossroads-style rock tiles; `src/room.cpp` picks tiles (edges, rounded corners, platforms) from the ASCII layout
- `cave_bg.bmp`: 256x256 horizontally tileable far background, scrolled at half speed for parallax

Re-run it after editing the script, or replace the BMPs with hand-made art (4bpp indexed, 16 colors, color 0 = transparent), keeping frame and tile order.

## Layout

- `src/`, `include/`: game code (`room.*`: ASCII room layout, tile selection and collision; `knight.*`: player physics and animation; `main.cpp`: camera and parallax)
- `tools/`: helper scripts
- `graphics/`: `.bmp` + `.json` image assets (converted at build time)
- `audio/`, `dmg_audio/`: music and sound effects
- `butano/`: the engine (don't edit; see below)

## Butano

`butano/` is a trimmed copy of a Butano release: only the engine (`butano/butano`), the shared fonts (`butano/common`) and the licenses, with no examples, games or docs. The version is in `butano/VERSION`. Butano is distributed under the zlib license (`butano/LICENSE`, third-party licenses in `butano/licenses/`).

To upgrade, run `tools/update_butano.sh <version>` (see https://github.com/GValiente/butano/releases), then `make clean && make -j8` and commit the result.

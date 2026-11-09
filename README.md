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
- A: jump (hold for higher jumps)

In mGBA the default keyboard mapping is arrow keys for the D-pad and X for A.

## Placeholder art

`tools/make_placeholder_art.py` generates `graphics/knight.bmp`, `graphics/room_tiles.bmp` and `graphics/room_palette.bmp`. Re-run it after editing the pixel art in the script, or replace the BMPs with real art (4bpp indexed, 16 colors, color 0 = transparent; knight frames are 16x32 stacked vertically).

## Layout

- `src/`, `include/`: game code (`room.*`: ASCII room layout, background and collision; `knight.*`: player physics and animation)
- `tools/`: helper scripts
- `graphics/`: `.bmp` + `.json` image assets (converted at build time)
- `audio/`, `dmg_audio/`: music and sound effects
- `butano/`: the engine (don't edit; see below)

## Butano

`butano/` is a trimmed copy of a Butano release: only the engine (`butano/butano`), the shared fonts (`butano/common`) and the licenses, with no examples, games or docs. The version is in `butano/VERSION`. Butano is distributed under the zlib license (`butano/LICENSE`, third-party licenses in `butano/licenses/`).

To upgrade, run `tools/update_butano.sh <version>` (see https://github.com/GValiente/butano/releases), then `make clean && make -j8` and commit the result.

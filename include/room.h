#ifndef HK_ROOM_H
#define HK_ROOM_H

#include "bn_regular_bg_ptr.h"
#include "bn_regular_bg_map_item.h"
#include "bn_regular_bg_map_cell.h"

namespace hk
{

// A room built from an ASCII layout ('#' solid, '.' empty).
// The layout drives both the background graphics and the collision.
// World coordinates are in pixels with (0, 0) at the room's top-left corner.
class room
{

public:
    static constexpr int columns = 64;
    static constexpr int rows = 32;
    static constexpr int tile_size = 8;
    static constexpr int width = columns * tile_size;
    static constexpr int height = rows * tile_size;

    room();

    [[nodiscard]] bool solid_tile(int tile_x, int tile_y) const;

    [[nodiscard]] bool solid_pixel(int x, int y) const
    {
        return solid_tile(x >> 3, y >> 3);
    }

    [[nodiscard]] bn::regular_bg_ptr& bg()
    {
        return _bg;
    }

private:
    alignas(int) bn::regular_bg_map_cell _cells[columns * rows];
    bn::regular_bg_map_item _map_item;
    bn::regular_bg_ptr _bg;

    [[nodiscard]] bn::regular_bg_ptr _create_bg();
};

}

#endif

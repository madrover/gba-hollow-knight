#include "room.h"

#include "bn_bg_tiles.h"
#include "bn_string_view.h"
#include "bn_regular_bg_item.h"
#include "bn_regular_bg_map_cell_info.h"

#include "bn_bg_palette_items_room_palette.h"
#include "bn_regular_bg_tiles_items_room_tiles.h"

namespace hk
{

namespace
{
    // Tile indices in graphics/room_tiles.bmp.
    constexpr int empty_tile = 0;
    constexpr int rock_tile = 1;
    constexpr int rock_alt_tile = 2;
    constexpr int rock_top_tile = 3;
    constexpr int rock_bottom_tile = 4;

    constexpr bn::string_view layout[] = {
        "################################################################",
        "################################################################",
        "##............................................................##",
        "##............................................................##",
        "##............................................................##",
        "##............................................................##",
        "##............................................................##",
        "##............................................................##",
        "##................##########..................................##",
        "##............................................................##",
        "##............................................................##",
        "##............................................................##",
        "##............................................##########......##",
        "##............####............................................##",
        "##............................................................##",
        "##............................................................##",
        "##................................########....................##",
        "##............................................................##",
        "##......####............................................########",
        "##............................................................##",
        "##....................########................................##",
        "##............................................................##",
        "######........................................................##",
        "##............................................................##",
        "##........########............................................##",
        "##............................##..............................##",
        "##............................##........########################",
        "##............................##........########################",
        "##............................##........########################",
        "################################################################",
        "################################################################",
        "################################################################",
    };

    constexpr bool layout_is_valid()
    {
        if(sizeof(layout) / sizeof(layout[0]) != room::rows)
        {
            return false;
        }

        for(const bn::string_view& row : layout)
        {
            if(row.size() != room::columns)
            {
                return false;
            }
        }

        return true;
    }

    static_assert(layout_is_valid(), "Room layout must be exactly room::columns x room::rows");

    constexpr bool layout_solid(int tile_x, int tile_y)
    {
        if(tile_x < 0 || tile_x >= room::columns || tile_y < 0 || tile_y >= room::rows)
        {
            return true;
        }

        return layout[tile_y][tile_x] == '#';
    }
}

room::room() :
    _map_item(_cells[0], bn::size(columns, rows)),
    _bg(_create_bg())
{
}

bool room::solid_tile(int tile_x, int tile_y) const
{
    return layout_solid(tile_x, tile_y);
}

bn::regular_bg_ptr room::_create_bg()
{
    for(int y = 0; y < rows; ++y)
    {
        for(int x = 0; x < columns; ++x)
        {
            int tile_index = empty_tile;

            if(layout_solid(x, y))
            {
                if(! layout_solid(x, y - 1))
                {
                    tile_index = rock_top_tile;
                }
                else if(! layout_solid(x, y + 1))
                {
                    tile_index = rock_bottom_tile;
                }
                else
                {
                    // Cheap hash to break up the repeating rock texture.
                    tile_index = ((x * 7 + y * 13) % 5 == 0) ? rock_alt_tile : rock_tile;
                }
            }

            bn::regular_bg_map_cell_info cell_info;
            cell_info.set_tile_index(tile_index);
            _cells[_map_item.cell_index(x, y)] = cell_info.cell();
        }
    }

    // Tile indices in the cells must match the tiles item exactly, so disable the VRAM tile offset while creating it.
    bn::bg_tiles::set_allow_offset(false);

    bn::regular_bg_item bg_item(
            bn::regular_bg_tiles_items::room_tiles, bn::bg_palette_items::room_palette, _map_item);
    bn::regular_bg_ptr result = bg_item.create_bg(0, 0);

    bn::bg_tiles::set_allow_offset(true);
    return result;
}

}

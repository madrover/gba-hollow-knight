#include "bn_core.h"
#include "bn_color.h"
#include "bn_display.h"
#include "bn_algorithm.h"
#include "bn_unique_ptr.h"
#include "bn_camera_ptr.h"
#include "bn_bg_palettes.h"

#include "room.h"
#include "knight.h"

namespace
{
    constexpr int camera_smoothing = 8;         // Higher is lazier.
    constexpr int camera_look_up = 24;          // Keep the Knight a bit below the screen center.

    // Converts a world position (top-left origin) to Butano coordinates (room centered on (0, 0)),
    // clamped so the camera never shows outside the room.
    bn::fixed_point camera_target(const bn::fixed_point& knight_position)
    {
        constexpr int max_x = hk::room::width / 2 - bn::display::width() / 2;
        constexpr int max_y = hk::room::height / 2 - bn::display::height() / 2;

        bn::fixed x = knight_position.x() - hk::room::width / 2;
        bn::fixed y = knight_position.y() - camera_look_up - hk::room::height / 2;
        return bn::fixed_point(bn::clamp(x, bn::fixed(-max_x), bn::fixed(max_x)),
                               bn::clamp(y, bn::fixed(-max_y), bn::fixed(max_y)));
    }
}

int main()
{
    bn::core::init();

    // Dark blue-gray backdrop, Hallownest style (GBA colors are 5 bits per channel: 0..31).
    bn::bg_palettes::set_transparent_color(bn::color(3, 4, 7));

    // The room holds a 64x32 cell map: keep it on the heap (EWRAM), not on the small IWRAM stack.
    bn::unique_ptr<hk::room> room(new hk::room());

    constexpr bn::fixed_point spawn_position(6 * hk::room::tile_size, 29 * hk::room::tile_size);
    bn::camera_ptr camera = bn::camera_ptr::create(camera_target(spawn_position));
    room->bg().set_camera(camera);

    hk::knight knight(spawn_position, camera);

    while(true)
    {
        knight.update(*room);

        bn::fixed_point target = camera_target(knight.position());
        bn::fixed_point position = camera.position();
        camera.set_position(position + (target - position) / camera_smoothing);

        bn::core::update();
    }
}

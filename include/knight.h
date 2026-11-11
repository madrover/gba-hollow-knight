#ifndef HK_KNIGHT_H
#define HK_KNIGHT_H

#include "bn_fixed_point.h"
#include "bn_sprite_ptr.h"
#include "bn_camera_ptr.h"

namespace hk
{

class room;

// The player. Position is the center of the Knight's feet, in room (world) pixels.
class knight
{

public:
    knight(const bn::fixed_point& spawn_position, const bn::camera_ptr& camera);

    void update(const room& room);

    [[nodiscard]] const bn::fixed_point& position() const
    {
        return _position;
    }

private:
    enum class animation
    {
        IDLE,
        RUN,
        JUMP,
        FALL,
        ATTACK,
    };

    bn::sprite_ptr _sprite;
    bn::sprite_ptr _slash_sprite;
    bn::fixed_point _position;
    bn::fixed_point _velocity;
    bool _grounded = false;
    bool _facing_left = false;
    int _coyote_frames = 0;
    int _jump_buffer_frames = 0;
    int _attack_frames = 0;             // Remaining frames of the current nail slash (0 when not attacking).
    int _attack_cooldown_frames = 0;
    animation _animation = animation::IDLE;
    int _animation_frame = 0;
    int _animation_counter = 0;
    int _graphics_index = 0;
    int _slash_graphics_index = 0;

    void _move_x(const room& room);
    void _move_y(const room& room);
    [[nodiscard]] bool _solid_in_column(const room& room, int pixel_x) const;
    [[nodiscard]] bool _solid_in_row(const room& room, int pixel_y) const;
    void _update_animation();
    void _update_sprite();
};

}

#endif

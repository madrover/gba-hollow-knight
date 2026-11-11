#include "knight.h"

#include "bn_keypad.h"
#include "bn_algorithm.h"
#include "bn_sprite_items_knight.h"
#include "bn_sprite_items_slash.h"

#include "room.h"

namespace hk
{

namespace
{
    // Tuning (pixels and frames, 60 frames per second).
    constexpr bn::fixed run_speed = 1.5;
    constexpr bn::fixed jump_speed = 4.6;
    constexpr bn::fixed gravity = 0.22;
    constexpr bn::fixed max_fall_speed = 5;
    constexpr bn::fixed jump_cut_speed = 1;     // Releasing B while rising caps upward speed to this.
    constexpr int coyote_time_frames = 5;       // Jump still allowed shortly after walking off a ledge.
    constexpr int jump_buffer_frames = 6;       // B pressed shortly before landing still jumps.
    constexpr int attack_frames = 15;           // How long the slash is active.
    constexpr int attack_cooldown_frames = 25;  // Minimum time between slashes (about Hollow Knight's 0.41 s).

    // Hitbox, relative to the feet center. Narrower than the mask and excluding the horns.
    constexpr bn::fixed half_width = 7;
    constexpr bn::fixed body_height = 23;

    // Graphics indices in graphics/knight.bmp (see tools/make_art.py).
    constexpr int idle_frames[] = { 0, 1 };
    constexpr int run_frames[] = { 2, 3, 4, 5 };
    constexpr int jump_frame = 6;
    constexpr int fall_frame = 7;
    constexpr int attack_frame = 8;
    constexpr int air_attack_frame = 9;
    constexpr int idle_frame_duration = 32;
    constexpr int run_frame_duration = 6;

    // Graphics indices in graphics/slash.bmp (see tools/make_art.py).
    constexpr int slash_frame_count = 3;
    constexpr int slash_frame_duration = attack_frames / slash_frame_count;

    constexpr int sprite_half_height = 16;

    // Slash sprite center relative to the Knight sprite center, when facing right.
    constexpr int slash_offset_x = 20;
    constexpr int slash_offset_y = 2;
}

knight::knight(const bn::fixed_point& spawn_position, const bn::camera_ptr& camera) :
    _sprite(bn::sprite_items::knight.create_sprite(0, 0)),
    _slash_sprite(bn::sprite_items::slash.create_sprite(0, 0)),
    _position(spawn_position)
{
    _sprite.set_camera(camera);
    _sprite.set_bg_priority(1);     // In front of the room (priority 2) and the far background (priority 3).
    _slash_sprite.set_camera(camera);
    _slash_sprite.set_bg_priority(1);
    _slash_sprite.set_z_order(-1);  // In front of the Knight.
    _slash_sprite.set_visible(false);
    _update_sprite();
}

void knight::update(const room& room)
{
    // Nail attack. The Knight keeps moving while slashing, but can't turn around until the slash ends.
    if(_attack_frames > 0)
    {
        --_attack_frames;
    }

    if(_attack_cooldown_frames > 0)
    {
        --_attack_cooldown_frames;
    }

    if(bn::keypad::a_pressed() && _attack_cooldown_frames == 0)
    {
        _attack_frames = attack_frames;
        _attack_cooldown_frames = attack_cooldown_frames;
    }

    bool attacking = _attack_frames > 0;

    // Horizontal input: Hollow Knight has no acceleration, the Knight runs at full speed instantly.
    if(bn::keypad::left_held())
    {
        _velocity.set_x(-run_speed);

        if(! attacking)
        {
            _facing_left = true;
        }
    }
    else if(bn::keypad::right_held())
    {
        _velocity.set_x(run_speed);

        if(! attacking)
        {
            _facing_left = false;
        }
    }
    else
    {
        _velocity.set_x(0);
    }

    // Jump with coyote time and input buffering.
    if(bn::keypad::b_pressed())
    {
        _jump_buffer_frames = jump_buffer_frames;
    }
    else if(_jump_buffer_frames > 0)
    {
        --_jump_buffer_frames;
    }

    if(_grounded)
    {
        _coyote_frames = coyote_time_frames;
    }
    else if(_coyote_frames > 0)
    {
        --_coyote_frames;
    }

    if(_jump_buffer_frames > 0 && _coyote_frames > 0)
    {
        _velocity.set_y(-jump_speed);
        _jump_buffer_frames = 0;
        _coyote_frames = 0;
        _grounded = false;
    }

    // Variable jump height: letting go of B cuts the jump short.
    if(! bn::keypad::b_held() && _velocity.y() < -jump_cut_speed)
    {
        _velocity.set_y(-jump_cut_speed);
    }

    _velocity.set_y(bn::min(_velocity.y() + gravity, max_fall_speed));

    _move_x(room);
    _move_y(room);
    _update_animation();
    _update_sprite();
}

bool knight::_solid_in_column(const room& room, int pixel_x) const
{
    int top = (_position.y() - body_height).floor_integer();
    int bottom = _position.y().ceil_integer() - 1;

    for(int y = top; y <= bottom; y += room::tile_size)
    {
        if(room.solid_pixel(pixel_x, y))
        {
            return true;
        }
    }

    return room.solid_pixel(pixel_x, bottom);
}

bool knight::_solid_in_row(const room& room, int pixel_y) const
{
    int left = (_position.x() - half_width).floor_integer();
    int right = (_position.x() + half_width).ceil_integer() - 1;

    for(int x = left; x <= right; x += room::tile_size)
    {
        if(room.solid_pixel(x, pixel_y))
        {
            return true;
        }
    }

    return room.solid_pixel(right, pixel_y);
}

void knight::_move_x(const room& room)
{
    bn::fixed velocity_x = _velocity.x();

    if(velocity_x == 0)
    {
        return;
    }

    _position.set_x(_position.x() + velocity_x);

    if(velocity_x > 0)
    {
        int right = (_position.x() + half_width).ceil_integer() - 1;

        if(_solid_in_column(room, right))
        {
            _position.set_x((right / room::tile_size) * room::tile_size - half_width);
        }
    }
    else
    {
        int left = (_position.x() - half_width).floor_integer();

        if(_solid_in_column(room, left))
        {
            _position.set_x((left / room::tile_size + 1) * room::tile_size + half_width);
        }
    }
}

void knight::_move_y(const room& room)
{
    bn::fixed velocity_y = _velocity.y();
    _position.set_y(_position.y() + velocity_y);

    if(velocity_y > 0)
    {
        int bottom = _position.y().ceil_integer() - 1;

        if(_solid_in_row(room, bottom))
        {
            _position.set_y((bottom / room::tile_size) * room::tile_size);
            _velocity.set_y(0);
        }
    }
    else if(velocity_y < 0)
    {
        int top = (_position.y() - body_height).floor_integer();

        if(_solid_in_row(room, top))
        {
            _position.set_y((top / room::tile_size + 1) * room::tile_size + body_height);
            _velocity.set_y(0);
        }
    }

    // Standing on ground means the pixel row right below the feet is solid.
    _grounded = _velocity.y() >= 0 && _solid_in_row(room, _position.y().floor_integer());
}

void knight::_update_animation()
{
    animation new_animation;

    if(_attack_frames > 0)
    {
        new_animation = animation::ATTACK;
    }
    else if(! _grounded)
    {
        new_animation = _velocity.y() < 0 ? animation::JUMP : animation::FALL;
    }
    else if(_velocity.x() != 0)
    {
        new_animation = animation::RUN;
    }
    else
    {
        new_animation = animation::IDLE;
    }

    if(new_animation != _animation)
    {
        _animation = new_animation;
        _animation_frame = 0;
        _animation_counter = 0;
    }
    else
    {
        ++_animation_counter;
    }

    int graphics_index;

    switch(_animation)
    {

    case animation::IDLE:
        if(_animation_counter >= idle_frame_duration)
        {
            _animation_counter = 0;
            _animation_frame = (_animation_frame + 1) % int(sizeof(idle_frames) / sizeof(idle_frames[0]));
        }
        graphics_index = idle_frames[_animation_frame];
        break;

    case animation::RUN:
        if(_animation_counter >= run_frame_duration)
        {
            _animation_counter = 0;
            _animation_frame = (_animation_frame + 1) % int(sizeof(run_frames) / sizeof(run_frames[0]));
        }
        graphics_index = run_frames[_animation_frame];
        break;

    case animation::JUMP:
        graphics_index = jump_frame;
        break;

    case animation::ATTACK:
        graphics_index = _grounded ? attack_frame : air_attack_frame;
        break;

    default:
        graphics_index = fall_frame;
        break;
    }

    if(graphics_index != _graphics_index)
    {
        _graphics_index = graphics_index;
        _sprite.set_tiles(bn::sprite_items::knight.tiles_item(), graphics_index);
    }
}

void knight::_update_sprite()
{
    // Butano places sprites by their center, with the room background centered on (0, 0).
    _sprite.set_position(_position.x() - room::width / 2,
                         _position.y() - sprite_half_height - room::height / 2);
    _sprite.set_horizontal_flip(_facing_left);

    bool attacking = _attack_frames > 0;
    _slash_sprite.set_visible(attacking);

    if(attacking)
    {
        int slash_graphics_index = bn::min((attack_frames - _attack_frames) / slash_frame_duration,
                                           slash_frame_count - 1);

        if(slash_graphics_index != _slash_graphics_index)
        {
            _slash_graphics_index = slash_graphics_index;
            _slash_sprite.set_tiles(bn::sprite_items::slash.tiles_item(), slash_graphics_index);
        }

        _slash_sprite.set_position(_sprite.x() + (_facing_left ? -slash_offset_x : slash_offset_x),
                                   _sprite.y() + slash_offset_y);
        _slash_sprite.set_horizontal_flip(_facing_left);
    }
}

}

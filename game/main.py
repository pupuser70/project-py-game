import arcade
from arcade import Camera2D
from pyglet.event import EVENT_HANDLE_STATE

SCREEN_W = 1000
SCREEN_H = 700

DEAD_ZONE_W = int(SCREEN_W * 0.35)
DEAD_ZONE_H = int(SCREEN_H * 0.45)

GRAVITY = 1
MOVE_SPEED = 3
JUMP_SPEED = 10
LADDER_SPEED = 3

COYOTE_TIME = 0.08
JUMP_BUFFER = 0.12
MAX_JUMPS = 1
TILE_SCALING = 2

CAMERA_LERP = 0.12

class Open_scene(arcade.View):
    def __init__(self):
        super().__init__()
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

class Test_Level(arcade.View):
    def setup(self):
        self.player_speed = MOVE_SPEED

        #self.texture_hearts = arcade.load_texture('assets/')

        self.gui_camera = Camera2D()
        self.gui_camera.position = (
            90,
            564
        )


        self.keys_pressed = set()

        self.left = self.right = self.up = self.down = self.jump_pressed = False

        map_name = "test_level.tmx"
        tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)

        self.ladders = tile_map.sprite_lists["lader"]
        self.floor_list = tile_map.sprite_lists["floor"]
        self.collision_list = tile_map.sprite_lists["collision"]
        self.player_list = tile_map.sprite_lists['player']
        self.player = self.player_list[0]

        self.engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            gravity_constant=GRAVITY,
            walls=self.collision_list,

            #platforms=self.platforms,
            ladders=self.ladders
        )
        self.can_jump = self.engine.can_jump

        self.jump_buffer_timer = 0
        self.time_since_ground = 999.0
        self.jumps_left = MAX_JUMPS

    def on_draw(self):
        self.clear()

        self.floor_list.draw()
        self.player_list.draw()
        self.ladders.draw()

        self.gui_camera.use()

    def on_update(self, dt: float):
        move = 0
        if self.left and not self.right:
            move = -MOVE_SPEED
        elif self.right and not self.left:
            move = MOVE_SPEED
        self.player.change_x = move

        on_ladder = self.engine.is_on_ladder()  # На лестнице?
        if on_ladder:
            self.can_jump = lambda y_distance: False
            # По лестнице вверх/вниз
            if self.up and not self.down:
                self.player.change_y = LADDER_SPEED
            elif self.down and not self.up:
                self.player.change_y = -LADDER_SPEED
            else:
                self.player.change_y = 0
        else:
            self.can_jump = self.engine.can_jump

        # Если не на лестнице — работает обычная гравитация движка
        # Прыжок: can_jump() + койот + буфер
        #self.jump_buffer_timer = COYOTE_TIME + JUMP_BUFFER
        grounded = self.can_jump(y_distance=6)  # Есть пол под ногами?
        if grounded:
            self.time_since_ground = 0
            self.jumps_left = MAX_JUMPS
        else:
            self.time_since_ground += dt

        # Учтём «запомненный» пробел
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= dt

        want_jump = self.jump_pressed or (self.jump_buffer_timer > 0)

        # Можно прыгать, если стоим на земле или в пределах койот-времени
        if want_jump:
            can_coyote = (self.time_since_ground <= COYOTE_TIME)
            if grounded or can_coyote:
                # Просим движок прыгнуть: он корректно задаст начальную вертикальную скорость
                self.engine.jump(JUMP_SPEED)
                self.jump_buffer_timer = 0

        # Обновляем физику — движок сам двинет игрока и платформы
        self.engine.update()

        ch_y = self.player.center_y
        ch_x = self.player.center_x
        if ch_y <= 563:
            ch_y = 563

        if ch_x <= 502:
            ch_x = 502

        position = (
            ch_x,
            ch_y
        )
        self.gui_camera.position = arcade.math.lerp_2d(  # Изменяем позицию камеры
            self.gui_camera.position,
            position,
            CAMERA_LERP,  # Плавность следования камеры
        )

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = True
        elif key in (arcade.key.UP, arcade.key.W):
            self.up = True
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down = True
        elif key == arcade.key.SPACE:
            self.jump_pressed = True
            self.jump_buffer_timer = JUMP_BUFFER

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = False
        elif key in (arcade.key.UP, arcade.key.W):
            self.up = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down = False
        elif key == arcade.key.SPACE:
            self.jump_pressed = False
            # Вариативная высота прыжка: отпустили рано — подрежем скорость вверх
            if self.player.change_y > 0:
                self.player.change_y *= 0.45

def main():
    window = arcade.Window(SCREEN_W, SCREEN_H, "игра")
    start_view = Test_Level()
    start_view.setup()

    window.show_view(start_view)
    arcade.run()

if __name__ == "__main__":
    main()

import arcade
from arcade import Camera2D
from pyglet.event import EVENT_HANDLE_STATE

SCREEN_W = 1000
SCREEN_H = 600

GRAVITY = 7
MOVE_SPEED = 3
JUMP_SPEED = 25
LADDER_SPEED = 3

COYOTE_TIME = 0.08
JUMP_BUFFER = 0.12
MAX_JUMPS = 1
TILE_SCALING = 1

CAMERA_LERP = 0.12

class Open_scene(arcade.View):
    def __init__(self):
        super().__init__()
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

class Test_Level(arcade.View):
    def setup(self):
        self.player_speed = MOVE_SPEED

        self.world_camera = Camera2D()
        self.gui_camera = Camera2D()

        self.keys_pressed = set()

        self.left = self.right = self.up = self.down = self.jump_pressed = False

        map_name = "test_level.tmx"
        tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)

        self.floor_list = tile_map.sprite_lists["floor"]
        self.collision_list = tile_map.sprite_lists["collision"]
        self.player_list = tile_map.sprite_lists['player']
        self.player = self.player_list[0]

        self.engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            gravity_constant=GRAVITY,
            walls=self.collision_list,

            #platforms=self.platforms,
            #ladders=self.ladders
        )

        self.jump_buffer_timer = 0
        self.time_since_ground = 999.0
        self.jumps_left = MAX_JUMPS

    def on_draw(self):
        self.clear()

        self.floor_list.draw()
        self.player_list.draw()

        self.world_camera.use()
        self.gui_camera.use()

    def on_update(self, dt: float):
        move = 0
        if self.left and not self.right:
            move = -MOVE_SPEED
        elif self.right and not self.left:
            move = MOVE_SPEED
        self.player.change_x = move
        """on_ladder = self.engine.is_on_ladder()  # На лестнице?
        if on_ladder:
            # По лестнице вверх/вниз
            if self.up and not self.down:
                self.player.change_y = LADDER_SPEED
            elif self.down and not self.up:
                self.player.change_y = -LADDER_SPEED
            else:
                self.player.change_y = 0"""

        # Если не на лестнице — работает обычная гравитация движка
        # Прыжок: can_jump() + койот + буфер
        #self.jump_buffer_timer = COYOTE_TIME + JUMP_BUFFER
        grounded = self.engine.can_jump(y_distance=6)  # Есть пол под ногами?
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

        target = (self.player.center_x, self.player.center_y)
        cx, cy = self.world_camera.position
        smooth = (cx + (target[0] - cx) * CAMERA_LERP,
                  cy + (target[1] - cy) * CAMERA_LERP)

        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2

        world_w = 2000  # Мы руками построили пол до x = 2000
        world_h = 900
        cam_x = max(half_w, min(world_w - half_w, smooth[0]))
        cam_y = max(half_h, min(world_h - half_h, smooth[1]))

        self.world_camera.position = (cam_x, cam_y)
        self.gui_camera.position = (SCREEN_W / 2, SCREEN_H / 2)

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

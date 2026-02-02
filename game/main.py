import arcade
from arcade import Camera2D
import player_f

LEVEL = 1

SCREEN_W = 1000
SCREEN_H = 700

DEAD_ZONE_W = int(SCREEN_W * 0.35)
DEAD_ZONE_H = int(SCREEN_H * 0.45)

SCALE_HEART = 2

JUMP_BUFFER = 0.12
GRAVITY = 1

TILE_SCALING = 2

CAMERA_LERP = 0.12


class Open_scene(arcade.View):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def setup(self):
        self.open_picture = arcade.Sprite('images/Text_start.png', 4)
        self.open_picture.center_x = 500
        self.open_picture.center_y = 350
        self.lis_draw = arcade.SpriteList()
        self.lis_draw.append(self.open_picture)

    def on_draw(self):
        self.lis_draw.draw()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if 350 <= x <= 655 and 336 <= y <= 396:
            level = First_Level()
            level.setup(self.window)
            self.window.show_view(level)


class End_scene(arcade.View):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def setup(self):
        self.end_picture = arcade.Sprite('images/End.png', 4)
        self.end_picture.center_x = 600
        self.end_picture.center_y = 300
        self.lis_draw = arcade.SpriteList()
        self.lis_draw.append(self.end_picture)

    def on_draw(self):
        self.lis_draw.draw()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if 485 <= x <= 585 and 305 <= y <= 365:
            level = First_Level()
            level.setup(self.window)
            self.window.show_view(level)


class First_Level(arcade.View):
    def setup(self, window):
        self.gravity = GRAVITY
        self.window = window

        self.texture_heart_full = arcade.load_texture('images/full_heart.png')
        self.texture_heart_not_full = arcade.load_texture('images/not_full_heart.png')
        self.texture_heart_half = arcade.load_texture('images/half_heart.png')

        self.gui_camera = Camera2D()
        self.gui_camera.position = (
            90,
            564
        )

        self.map_name = "first_level.tmx"
        tile_map = arcade.load_tilemap(self.map_name, scaling=TILE_SCALING)

        self.end = self.fon = tile_map.sprite_lists["end"]
        self.fon = tile_map.sprite_lists["fon"]
        self.ladders = tile_map.sprite_lists["lader"]
        self.floor_list = tile_map.sprite_lists["floor"]
        self.collision_list = tile_map.sprite_lists["collision"]
        self.jumping_list = tile_map.sprite_lists['jumping']
        self.ships_list = tile_map.sprite_lists['ships']
        self.platforms_list = tile_map.sprite_lists['platforms']
        self.delta_platforms_list = arcade.SpriteList()
        self.delta_platforms_list.extend(self.platforms_list)

        self.heart_list = arcade.SpriteList()
        for i in range(3):
            self.heart_list.append(arcade.Sprite(self.texture_heart_full, SCALE_HEART))

        self.player = player_f.Player_C(self.jumping_list, self.ships_list,
                                        self.delta_platforms_list,
                                        self.platforms_list, self.heart_list)

        self.engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            gravity_constant=self.gravity,
            walls=self.collision_list,

            platforms=self.delta_platforms_list,
            ladders=self.ladders
        )
        self.heats = 3

        self.player.engine = self.engine
        self.player.setup()
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

    def on_draw(self):
        self.clear()

        self.fon.draw()
        self.platforms_list.draw()
        self.jumping_list.draw()
        self.floor_list.draw()
        self.ladders.draw()
        self.ships_list.draw()
        self.end.draw()
        self.player_list.draw()
        self.heart_list.draw()
        self.gui_camera.use()

    def on_update(self, dt: float):
        if arcade.check_for_collision_with_list(self.player, self.end):
            end_good = End_Good_Scene(self.window)
            end_good.setup()
            self.window.show_view(end_good)
        self.player.updat(dt)
        self.player.updat_animation()
        self.heart_list[0].center_x = self.gui_camera.position[0] - 450
        self.heart_list[1].center_x = self.gui_camera.position[0] - 420
        self.heart_list[2].center_x = self.gui_camera.position[0] - 390

        self.heart_list[0].center_y = self.gui_camera.position[1] + 300
        self.heart_list[1].center_y = self.gui_camera.position[1] + 300
        self.heart_list[2].center_y = self.gui_camera.position[1] + 300

        if self.player.heats == 2:
            self.heart_list[2].texture = self.texture_heart_not_full
        if self.player.heats == 1:
            self.heart_list[1].texture = self.texture_heart_not_full
        if self.player.heats == 0:
            self.heart_list[0].texture = self.texture_heart_not_full
            end = End_scene(self.window)
            end.setup()
            self.window.show_view(end)

        self.engine.update()

        ch_y = self.player.center_y
        ch_x = self.player.center_x
        if ch_y <= 450:
            ch_y = 350

        if ch_x <= 502:
            ch_x = 502

        if ch_x >= 938:
            ch_x = 938

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
        self.player.keys_pressed.add(key)
        if key in (arcade.key.LEFT, arcade.key.A):
            self.player.lef = True
            self.player.stay_l = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.player.righ = True
            self.player.stay_r = False
        elif key in (arcade.key.UP, arcade.key.W):
            self.player.up = True
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.player.down = True
        elif key == arcade.key.SPACE:
            self.player.jump_pressed = True
            self.player.jump_buffer_timer = JUMP_BUFFER

    def on_key_release(self, key, modifiers):
        self.player.keys_pressed.remove(key)
        if key in (arcade.key.LEFT, arcade.key.A):
            self.player.lef = False
            self.player.stay_l = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.player.righ = False
            self.player.stay_r = True
        elif key in (arcade.key.UP, arcade.key.W):
            self.player.up = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.player.down = False
        elif key == arcade.key.SPACE:
            self.player.jump_pressed = False
            # Вариативная высота прыжка: отпустили рано — подрежем скорость вверх
            if self.player.change_y > 0:
                self.player.change_y *= 0.4


class End_Good_Scene(arcade.View):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def setup(self):
        self.end_picture = arcade.Sprite('images/End_good.png', 4)
        self.end_picture.center_x = 600
        self.end_picture.center_y = 300
        self.lis_draw = arcade.SpriteList()
        self.lis_draw.append(self.end_picture)

    def on_draw(self):
        self.lis_draw.draw()



def main():
    window = arcade.Window(SCREEN_W, SCREEN_H, "игра")
    start_scene = Open_scene(window)
    start_scene.setup()
    window.show_view(start_scene)
    arcade.run()


if __name__ == "__main__":
    main()

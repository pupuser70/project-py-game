import arcade
from pyglet.event import EVENT_HANDLE_STATE

TILE_SCALING = 1
GRAVITY = 0.5

class Open_scene(arcade.View):
    def __init__(self):
        super().__init__()
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

class Test_Level(arcade.View):
    def setup(self):
        self.player_speed = 30


        self.keys_pressed = set()  # Множество нажатых клавиш

        map_name = "test_level.tmx"
        tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)

        self.floor_list = tile_map.sprite_lists["floor"]
        self.collision_list = tile_map.sprite_lists["collision"]
        self.player_list = tile_map.sprite_lists['player']
        self.player = self.player_list[0]

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.collision_list
        )

    def on_draw(self):
        self.clear()

        self.floor_list.draw()
        self.player_list.draw()

    def on_update(self, delta_time):
        self.physics_engine.update()

        dx, dy = 0, 0
        if arcade.key.LEFT in self.keys_pressed or arcade.key.A in self.keys_pressed:
            dx -= self.player_speed * delta_time
        if arcade.key.RIGHT in self.keys_pressed or arcade.key.D in self.keys_pressed:
            dx += self.player_speed * delta_time
        if arcade.key.UP in self.keys_pressed or arcade.key.W in self.keys_pressed:
            dy += self.player_speed * delta_time
        if arcade.key.DOWN in self.keys_pressed or arcade.key.S in self.keys_pressed:
            dy -= self.player_speed * delta_time

        dy -= GRAVITY

        # Нормализация диагонального движения
        if dx != 0 and dy != 0:
            factor = 0.7071  # ≈ 1/√2
            dx *= factor
            dy *= factor
        self.player.center_x += dx
        self.player.center_y += dy

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

def main():
    window = arcade.Window(1000, 600, "игра")
    start_view = Test_Level()
    start_view.setup()

    window.show_view(start_view)
    arcade.run()

if __name__ == "__main__":
    main()

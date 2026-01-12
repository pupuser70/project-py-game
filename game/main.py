import arcade

TILE_SCALING = 1

class Open_scene(arcade.View):
    def __init__(self):
        super().__init__()


class Test_Level(arcade.Window):
    def setup(self):
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

        map_name = "test_level.tmx"
        tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)

        self.floor_list = tile_map.sprite_lists["floor"]
        self.collision_list = tile_map.sprite_lists["collision"]
        self.player_list = tile_map.sprite_lists['player']

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_list[0], self.collision_list
        )

    def on_draw(self):
        self.clear()

        self.floor_list.draw()
        self.player_list.draw()

def main():
    game = Test_Level()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
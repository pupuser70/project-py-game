import arcade
from arcade import  Sprite
from arcade.examples.particle_fireworks import TEXTURE

MOVE_SPEED = 3
JUMP_SPEED = 10
MAX_JUMPS = 1
COYOTE_TIME = 0.08
JUMP_BUFFER = 0.12
LADDER_SPEED = 3
JUMP_SPEED_COL = 20
TEXTUR = arcade.load_texture('images/full_heart.png')

class Player_C(Sprite):
    def __init__(self, jumping_list, ships_list, delta_platforms_list, platforms_list, heats, engine=None):
        super().__init__()

        self.texture_r_stay = arcade.load_texture('images/right_stay-Photoroom.png')
        self.texture_r_start = arcade.load_texture('images/right_start.png')
        self.texture_r_finish = arcade.load_texture('images/right_finish-Photoroom.png')
        self.texture_l_stay = arcade.load_texture('images/left_stay-Photoroom.png')
        self.texture_l_start = arcade.load_texture('images/left_start-Photoroom.png')
        self.texture_l_finish = arcade.load_texture('images/left_finish-Photoroom.png')

        self.tex_r_lis = [None, self.texture_r_start,  self.texture_r_finish]
        self.tex_l_lis = [None, self.texture_l_start, self.texture_l_finish]

        self.texture = self.texture_r_stay
        self.jumping_list = jumping_list
        self.ships_list = ships_list
        self.engine = engine
        self.delta_platforms_list = delta_platforms_list
        self.platforms_list= platforms_list
        self.heats_list = heats
        self.center_x = 100
        self.center_y = 250

    def setup(self):
        self.heats = 3
        self.stay_l = False
        self.stay_r = True
        self.keys_pressed = set()
        self.player_speed = MOVE_SPEED
        self.lef = self.righ = False
        self.up = self.down = self.jump_pressed = False
        self.start_x = self.center_x
        self.start_y = self.center_y
        self.can_jump = self.engine.can_jump
        self.jump_buffer_timer = 0
        self.time_since_ground = 999.0
        self.jumps_left = MAX_JUMPS
        self.flag_coll_platforms = 0
        self.flag = False
        self.texture_change_time = 0
        self.texture_change_delay = 0.1
        self.current_texture = 1

    def updat(self, dt: float):
        move = 0
        if self.lef and not self.righ:
            move = -MOVE_SPEED
        elif self.righ and not self.lef:
            move = MOVE_SPEED
        self.change_x = move

        on_ladder = self.engine.is_on_ladder()  # На лестнице?
        if on_ladder:
            self.can_jump = lambda y_distance: False
            # По лестнице вверх/вниз
            if self.up and not self.down:
                self.change_y = LADDER_SPEED
            elif self.down and not self.up:
                self.change_y = -LADDER_SPEED
            else:
                self.change_y = 0
        else:
            self.can_jump = self.engine.can_jump

        # Если не на лестнице — работает обычная гравитация движка
        # Прыжок: can_jump() + койот + буфер
        # self.jump_buffer_timer = COYOTE_TIME + JUMP_BUFFER
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

        if arcade.check_for_collision_with_list(self, self.jumping_list):
            self.engine.jump(JUMP_SPEED_COL)

        if arcade.check_for_collision_with_list(self, self.ships_list):
            self.heats -= 1
            self.center_x = self.start_x
            self.center_y = self.start_y

        if arcade.key.S in self.keys_pressed:
            self.delta_platforms_list.clear()
            self.flag = True
        elif self.flag:
            self.delta_platforms_list.extend(self.platforms_list)
            self.flag = False

    def updat_animation(self, delta_time: float = 1 / 60):
        if self.change_x != 0:
            self.texture_change_time += delta_time
            if self.righ:
                if self.texture_change_time >= self.texture_change_delay:
                    self.texture_change_time = 0
                    self.current_texture *= -1
                    self.texture = self.tex_r_lis[self.current_texture]
            else:
                if self.texture_change_time >= self.texture_change_delay:
                    self.texture_change_time = 0
                    self.current_texture *= -1
                    self.texture = self.tex_l_lis[self.current_texture]

        else:
            if self.stay_r:
                self.texture = self.texture_r_stay
            if self.stay_l:
                self.texture = self.texture_l_stay

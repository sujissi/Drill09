import math
import random

from pico2d import load_image, get_time
from sdl2 import SDLK_a, SDL_KEYDOWN, SDLK_SPACE, SDL_KEYUP, SDLK_RIGHT, SDLK_LEFT


################# 이벤트판단 ##################
def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE


def time_out(e):
    return e[0] == 'TIMEOUT'


def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT


def a_key_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a


################## 상태 ####################
class Idle:  # -> 객체생성을 위한 클래스x

    @staticmethod
    def enter(boy, e):
        if boy.action == 0:
            boy.action = 2
        elif boy.action == 1:
            boy.action = 3
        boy.dir = 0
        boy.frame = 0
        boy.idle_start_time = get_time()
        print('Idle Enter')

    @staticmethod
    def exit(boy, e):
        print('Idle Exit')

    @staticmethod
    def do(boy):
        print('Idle Do')
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.idle_start_time > 4:
            boy.state_machine.handle_event(('TIMEOUT', 0))

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)
        pass


class Sleep:  # -> 객체생성을 위한 클래스x

    @staticmethod
    def enter(boy, e):
        boy.frame = 0
        print('눕다')

    @staticmethod
    def exit(boy, e):
        print('일어서기')

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        print('드르렁드르렁')

    @staticmethod
    def draw(boy):
        if boy.action == 2:
            boy.image.clip_composite_draw(boy.frame * 100, 200, 100, 100,
                                          -3.141592 / 2, '', boy.x + 25, boy.y - 25, 100, 100)
        else:
            boy.image.clip_composite_draw(boy.frame * 100, 300, 100, 100,
                                          3.141592 / 2, '', boy.x - 25, boy.y - 25, 100, 100)


class Run:  # -> 객체생성을 위한 클래스x

    @staticmethod
    def enter(boy, e):
        if right_down(e) or left_up(e):
            boy.dir, boy.action = 1, 1
        elif left_down(e) or right_up(e):
            boy.dir, boy.action = -1, 0
        print('달리기')

    @staticmethod
    def exit(boy, e):
        print('달리기멈춤')
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 5
        print('Idle Do')

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)
        pass


class AutoRun:  # -> 객체생성을 위한 클래스x

    @staticmethod
    def enter(boy, e):
        boy.idle_start_time = get_time()
        rand_dir = random.choice([True, False])
        if rand_dir:
            boy.dir, boy.action = 1, 1
        else:
            boy.dir, boy.action = -1, 0
        print('AutoRun Enter')

    @staticmethod
    def exit(boy, e):
        print('AutoRun Exit')

    @staticmethod
    def do(boy):
        if get_time() - boy.idle_start_time > 4:
            boy.state_machine.handle_event(('TIMEOUT', 0))
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 20
        if boy.x + 50 > 800 or boy.x - 50 < 0:
            boy.dir = -1 * boy.dir
            boy.action = 1 - boy.action
        print('AutoRun Do')

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y + 30, 200, 200)
        pass


################# 상태머신 #####################
class StateMachine:
    def __init__(self, boy):
        self.boy = boy
        self.cur_state = Idle
        self.transitions = {
            Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Sleep, a_key_down: AutoRun},
            Run: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle, a_key_down: AutoRun},
            Sleep: {right_down: Run, left_down: Run, right_up: Run, left_up: Run, space_down: Idle,
                    a_key_down: AutoRun},
            AutoRun: {time_out: Idle}
        }

    def start(self):
        self.cur_state.enter(self.boy, ('START', 0))

    def handle_event(self, e):
        for check_event, next_state in self.transitions[self.cur_state].items():
            if check_event(e):
                self.cur_state.exit(self.boy, e)
                self.cur_state = next_state
                self.cur_state.enter(self.boy, e)
                return True
        return False

    def update(self):
        self.cur_state.do(self.boy)

    def draw(self):
        self.cur_state.draw(self.boy)


################# Boy객체 ########################
class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.action = 3
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self)
        self.state_machine.start()

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_event(('INPUT', event))
        pass

    def draw(self):
        self.state_machine.draw()

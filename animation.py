import pygame, sys
import constants as C
import math

class Animation():
    def __init__(self,entity,frame):
        self.entity = entity
        entity.slow_motion = 1#this value can be changed for player so that it counterasct teh slow motinos
        self.framerate = C.animation_framerate
        self.frame = frame

    def enter_state(self,next_animation):
        self.entity.animation = getattr(sys.modules[__name__], next_animation)(self.entity,self.frame)#make a class based on the name of the newstate: need to import sys

    def reset_timer(self):
        self.frame = 0

    def handle_input(self,input):
        pass

class Entity_animation(Animation):#phase and state
    def __init__(self,entity,frame = 0):
        super().__init__(entity,frame)

    def update(self):
        self.entity.image = self.entity.sprites.get_image(self.entity.currentstate.state_name,int(self.frame),self.entity.currentstate.dir).copy()
        self.frame += self.framerate*self.entity.game_objects.game.dt*self.entity.slow_motion

        if self.frame >= len(self.entity.sprites.sprite_dict[self.entity.currentstate.state_name]):
            self.entity.currentstate.increase_phase()
            self.reset_timer()

    def handle_input(self,input):
        if input=='Hurt':
            self.enter_state('Hurt_animation')
        elif input == 'Invincibile':
            self.enter_state('Invincibile_animation')

class Hurt_animation(Entity_animation):#become white
    def __init__(self,entity,frame):
        super().__init__(entity,frame)
        self.duration = C.hurt_animation_length#hurt animation duration
        self.next_animation = 'Entity_animation'

    def update(self):
        super().update()
        self.entity.image.fill((250,250,250),special_flags=pygame.BLEND_ADD)
        self.duration -= self.entity.game_objects.game.dt*self.entity.slow_motion

        if self.duration < 0:
            self.enter_state(self.next_animation)

    def handle_input(self,input):
        if input == 'Invincibile':
            self.next_animation = 'Invincibile_animation'

class Invincibile_animation(Entity_animation):#blink white
    def __init__(self,entity,frame):
        super().__init__(entity,frame)
        self.duration = C.invincibility_time_player-(C.hurt_animation_length+1)#a duration which considers the player invinsibility
        self.time = 0

    def update(self):
        super().update()
        colour=[int(0.5*255*math.sin(self.time)+255*0.5),int(0.5*255*math.sin(self.time)+255*0.5),int(0.5*255*math.sin(self.time)+255*0.5)]
        self.entity.image.fill(colour,special_flags=pygame.BLEND_ADD)
        self.duration -= self.entity.game_objects.game.dt*self.entity.slow_motion
        self.time += 0.5*self.entity.game_objects.game.dt*self.entity.slow_motion

        if self.duration < 0:
            self.enter_state('Entity_animation')

class Simple_animation(Animation):#no state or phase
    def __init__(self,entity,frame = 0):
        super().__init__(entity,frame)

    def update(self):
        self.entity.image = self.entity.sprites[int(self.frame)].copy()
        self.frame += self.framerate*self.entity.game_objects.game.dt

        if self.frame >= len(self.entity.sprites):
            self.reset_timer()
            self.entity.reset_timer()

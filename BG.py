import pygame, math, random, sys, Read_files, states_weather

class Weather(pygame.sprite.Sprite):

    def __init__(self,weather_group):
        super().__init__()
        self.pos=[random.randint(0, 500),random.randint(-500, -100)]#starting position
        self.group = weather_group
        self.currentstate = states_weather.Fall(self)
        self.velocity=[0,0]
        self.wind=2

    def update_pos(self,scroll):
        self.rect.topleft = [self.rect.topleft[0] + scroll[0]+self.velocity[0], self.rect.topleft[1] + scroll[1]+self.velocity[1]]

    def update(self,scroll):
        self.update_pos(scroll)
        self.currentstate.update()
        self.currentstate.update_animation()
        self.boundary()

    def boundary(self):
        if self.rect.y>300:#if on the lower side of screen.
            self.rect.y=random.randint(-500, -100)

        #continiouse falling, horizontally
        if self.rect.x<-50:
            self.rect.x+=500
        elif self.rect.x>500:
            self.rect.x-=500

    def create_particles(self,particle,number=100):
        for i in range(0,number):
            obj=getattr(sys.modules[__name__], particle)(self.group)
            self.group.add(obj)

    def set_color(self):
        replace_color=(251,242,54)#=self.image.get_at((4,4))
        img_copy=pygame.Surface(self.image.get_size())
        img_copy.fill(self.color)
        self.image.set_colorkey(replace_color)
        img_copy.blit(self.image,(0,0))
        self.image=img_copy
        self.image.set_colorkey((0,0,0,255))

    def speed(self):
        pass

    def collision(self):
        self.currentstate.change_state()

class Snow(Weather):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/animations/Weather/Snow/')

    def __init__(self,group):
        super().__init__(group)
        self.image=pygame.image.load('Sprites/animations/Weather/Snow/Fall/fall1.png').convert_alpha()
        self.rect = self.image.get_rect(center=self.pos)
        self.time=0

    def speed(self):
        self.time+=1
        self.velocity=[math.sin(self.time//10) + self.wind,1]
        if self.time>100:
            self.time=0

class Sakura(Weather):
    def __init__(self,group):
        super().__init__(group)
        self.scale=[20,20]
        colors=[[255,192,203],[255,105,180],[255,100,180]]
        self.color=colors[random.randint(0, len(colors)-1)]
        self.velocity=[self.phase,1.5]

class Autumn(Sakura):
    def __init__(self,group):
        super().__init__(group)
        colors=[[178,34,34],[139,69,19],[128,128,0],[255,228,181]]
        self.color=colors[random.randint(0, len(colors)-1)]

class Rain(Weather):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/animations/Weather/Rain/')

    def __init__(self,group):
        super().__init__(group)
        self.image=pygame.image.load('Sprites/animations/Weather/Rain/Fall/fall1.png').convert_alpha()
        self.rect = self.image.get_rect(center=self.pos)
        self.velocity=[0.1+self.wind,5]

class Light():
    def __init__(self):
        super().__init__()
        pass

    @staticmethod
    def add_white(radius,colour,screen,pos):
        surf=pygame.Surface((2*radius,2*radius))
        pygame.draw.circle(surf,colour,(radius,radius),radius)
        surf.set_colorkey((0,0,0))
        screen.blit(surf,(pos[0]-radius,pos[1]-radius),special_flags=pygame.BLEND_RGB_ADD)

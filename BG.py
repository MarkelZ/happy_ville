import pygame, math, random

weather=pygame.sprite.Group()

class Background(pygame.sprite.Sprite):

    number_of_particles=0

    def __init__(self):
        super().__init__()
        self.pos=[random.randint(-400, 400),random.randint(-400, -100)]
        self.velocity=[0,0]
        Background.number_of_particles+=1
        self.phase=random.randint(0, 10)
        self.max=100#max number of partivles

    def update(self,pos,screen):
        pygame.draw.circle(screen,self.color,self.pos,self.radius)#draw a circle

        self.pos = [self.pos[0] + pos[0], self.pos[1] + pos[1]]#compensate for scroll

        self.speed()#modulate the speed according to the particle type

        if self.pos[1]>300:#if on the lower side of screen. SHould we do ground collisions?
            weather.remove(self)
            Background.number_of_particles-=1
        #continiouse falling, horizontally
        if self.pos[0]<0:
            self.pos[0]+=480
        elif self.pos[0]>480:
            self.pos[0]-=480

    def create_particle(self,particle):
        for i in range(self.number_of_particles,self.max):
            if particle=='snow':
                particles=Snow()
                weather.add(particles)
            elif particle=='sakura':
                particles=Sakura()
                weather.add(particles)
            elif particle=='rain':
                particles=Rain()
                weather.add(particles)
        return weather

class Snow(Background):
    def __init__(self):
        super().__init__()
        self.radius=2#size
        self.timer=500#lifetime
        self.color=(255,255,255)

    def speed(self):
        self.timer-=1
        self.velocity=[0.5*math.sin(self.timer//10 + self.phase),0.5]
        self.pos=[self.pos[0]+self.velocity[0],self.pos[1]+self.velocity[1]]

class Sakura(Background):
    def __init__(self):
        super().__init__()
        self.radius=2#size
        self.timer=500#lifetime
        self.color=(255,100,180)

    def speed(self):
        self.timer-=1
        self.velocity=[self.phase,1.5]
        self.pos=[self.pos[0]+self.velocity[0],self.pos[1]+self.velocity[1]]

class Rain(Background):
    def __init__(self):
        super().__init__()
        self.radius=1#size
        self.timer=500#lifetime
        self.color=(0,0,200)

    def speed(self):
        self.timer-=1
        self.velocity=[0.1,5]
        self.pos=[self.pos[0]+self.velocity[0],self.pos[1]+self.velocity[1]]

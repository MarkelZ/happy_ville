import pygame, random, sys, Read_files, animation, states_player, states_NPC, states_enemy, states_vatt, states_boss, math, sound

pygame.mixer.init()

class ExtendedGroup(pygame.sprite.Group):#adds a white glow around enteties
    def __init__(self):
        super().__init__()

    def draw(self, surface):
        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sprites:
            self.spritedict[spr] = surface_blit(spr.image, spr.rect)
            ExtendedGroup.add_colour(20,(20,20,20),surface,spr.hitbox)#addded this
        self.lostsprites = []

    @staticmethod
    def add_colour(radius,colour,screen,rect):
        surf=pygame.Surface((2*radius,2*radius))
        pygame.draw.circle(surf,colour,(radius,radius),radius)
        surf.set_colorkey((0,0,0))
        screen.blit(surf,(rect.x,rect.y),special_flags=pygame.BLEND_RGB_ADD)

class Platform(pygame.sprite.Sprite):#has hitbox
    def __init__(self,pos,size = (16,16)):
        super().__init__()
        self.rect = pygame.Rect(pos,size)
        self.rect.bottomleft = pos
        self.hitbox = self.rect.inflate(0,0)
        #self.is_slope=False

    def update(self,pos):
        self.update_pos(pos)

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.center=self.rect.center

class Invisible_block(Platform):
    def __init__(self,pos,size):
        super().__init__(pos,size)

    def collide_y(self,entity):
        pass

    def collide_x(self,entity):
        if type(entity).__name__ != "Player":#only apply to enemies and NPC
            entity.dir[0] = -entity.dir[0]#turn around

class Collision_block(Platform):
    def __init__(self,pos,size):
        super().__init__(pos,size)

    def collide_x(self,entity):
        #check for collisions and get a dictionary of sprites that collides
        if entity.velocity[0]>0:#going to the right
            entity.hitbox.right = self.hitbox.left
            entity.collision_types['right'] = True
        else:#going to the left
            entity.hitbox.left = self.hitbox.right
            entity.collision_types['left'] = True
        entity.update_rect()

    def collide_y(self,entity):
        if entity.velocity[1]>0:#going down
            entity.hitbox.bottom = self.hitbox.top
            entity.collision_types['bottom'] = True
            entity.velocity[1] = 0
        else:#going up
            entity.hitbox.top = self.hitbox.bottom
            entity.collision_types['top'] = True
            entity.velocity[1] = 0 #knock back
        entity.update_rect()

class Collision_oneway_up(Platform):
    def __init__(self,pos,size):
        super().__init__(pos,size)

    def collide_x(self,entity):
        pass

    def collide_y(self,entity):
        offset=10
        if entity.velocity[1]>0:#going down
            if entity.hitbox.bottom<self.hitbox.top+offset:
                entity.hitbox.bottom = self.hitbox.top
                entity.collision_types['bottom'] = True
                entity.velocity[1] = 0
                self.goingup=False
                entity.update_rect()
        else:#going up
            pass

class Collision_right_angle(Collision_block):
    def __init__(self,pos,points):
        self.define_values(pos, points)
        super().__init__(self.new_pos,self.size)
        #self.is_slope=True

    #function calculates size, real bottomleft position and orientation of right angle triangle
    #the value in orientatiion represents the following:
    #0 = tilting to the right, flatside down
    #1 = tilting to the left, flatside down
    #2 = tilting to the right, flatside up
    #3 = tilting to the left, flatside up
    def define_values(self, pos, points):
        self.new_pos = (0,0)
        self.size = (0,0)
        self.orientation = 0
        x_0_count = 0
        y_0_count = 0
        x_extreme = 0
        y_extreme = 0

        for point in points:
            if point[0] == 0:
                x_0_count += 1
            else:
                x_extreme = point[0]
            if point[1] == 0:
                y_0_count += 1
            else:
                y_extreme = point[1]

        self.size = (abs(x_extreme), abs(y_extreme))

        if x_extreme < 0:
            if y_extreme < 0:
                self.new_pos = (pos[0] + x_extreme, pos[1])
                if x_0_count == 1:
                    self.orientation = 0
                elif y_0_count == 1:
                    self.orientation = 3
                else:
                    self.orientation = 1

            else:
                self.new_pos = (pos[0] + x_extreme, pos[1] + y_extreme)
                if x_0_count == 1:
                    self.orientation = 2
                elif y_0_count == 1:
                    self.orientation = 1
                else:
                    self.orientation = 3

        else:
            if y_extreme < 0:
                self.new_pos = pos
                if x_0_count == 1:
                    self.orientation = 1
                elif y_0_count == 1:
                    self.orientation = 2
                else:
                    self.orientation = 0

            else:
                self.new_pos = (pos[0], pos[1] + y_extreme)
                if x_0_count == 1:
                    self.orientation = 3
                elif y_0_count == 1:
                    self.orientation = 0
                else:
                    self.orientation = 2

class Spikes(Platform):
    def __init__(self,pos,size):
        super().__init__(pos,size)
        self.image=pygame.image.load("Sprites/level_sheets/Spkies.png").convert_alpha()
        self.dmg = 10

    def collide_x(self,entity):
        if entity.velocity[0]>0:#going to the right
            entity.velocity[0]=-6#knock back
        else:#going to the left
            entity.velocity[0]=6#knock back
        entity.take_dmg(self.dmg)

    def collide_y(self,entity):
        if entity.velocity[1]>0:#going down
            entity.velocity[1]=-6#knock back
        else:#going up
            entity.velocity[1]=6#knock back
        entity.take_dmg(self.dmg)

class Staticentity(pygame.sprite.Sprite):#no hitbox but image
    def __init__(self,pos,img=pygame.Surface((16,16))):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def update(self,pos):
        self.update_pos(pos)

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]

class BG_Block(Staticentity):
    def __init__(self,pos,img,parallax=1):
        super().__init__(pos,img)
        self.true_pos = self.rect.topleft
        self.parallax=parallax

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + self.parallax*pos[0], self.rect.topleft[1] + self.parallax*pos[1]]
        self.true_pos= [self.true_pos[0] + self.parallax*pos[0], self.true_pos[1] + self.parallax*pos[1]]
        self.rect.topleft = self.true_pos

class BG_Animated(BG_Block):
    def __init__(self,pos,sprite_folder_path,parallax=1):
        super().__init__(pos,pygame.Surface((16,16)),parallax)
        self.timer = 0
        self.frame_index = 0
        self.sprites = Read_files.load_sprites(sprite_folder_path)
        self.image = self.sprites[0]

    def update(self, pos):
        self.update_pos(pos)
        self.update_sprite()

    def update_sprite(self):
        if self.timer == 4:
            self.timer = 0
            self.frame_index += 1
            if self.frame_index == len(self.sprites):
                self.frame_index = 0
            self.image = self.sprites[self.frame_index]
        else:
            self.timer += 1

class Particle_effect(Staticentity):

    class Particle(pygame.sprite.Sprite):
        def __init__(self, pos = [0,0], vel = [0,0], accel = 0.98, color = [0,0,0,0], fade = 1):
            super().__init__()
            self.image = pygame.Surface((1,1), pygame.SRCALPHA, 32)
            self.image = self.image.convert_alpha()
            self.image.fill(color)
            self.rect = self.image.get_rect()
            self.rect.topleft = pos
            self.true_pos = pos
            self.vel = vel
            self.accel = accel
            self.color = color
            self.fade = fade

        def update(self):
            self.true_pos = [self.true_pos[0] + self.vel[0], self.true_pos[1] + self.vel[1]]
            self.rect.topleft = [int(self.true_pos[0]),int(self.true_pos[1])]
            self.vel[0] = self.vel[0] * self.accel
            self.vel[1] = self.vel[1] * self.accel
            if not self.fade == 1:
                self.color[-1] = int(self.color[-1] * self.fade)
                self.image.fill(self.color)



    def __init__(self, pos, img_size = (32,32)):
        super().__init__(pos)
        self.image = pygame.Surface(img_size, pygame.SRCALPHA, 32)
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.lifetime = 100
        self.generate_particles()

    def generate_particles(self):
        self.particles = pygame.sprite.Group()

    def update(self, pos):
        self.image.fill((0,0,0,0))
        self.particles.draw(self.image)
        self.particles.update()
        super().update(pos)
        self.lifetime -= 1
        if not bool(self.particles) or self.lifetime == 0:
            self.kill()

class Particle_effect_attack(Particle_effect):


    def __init__(self, pos):
        self.blit_size = (256,256)
        super().__init__(pos, self.blit_size)
        self.lifetime = 30

    def generate_particles(self):
        #generate random number of particles
        super().generate_particles()
        quantity = random.randint(600,700)
        direction_qty = random.randint(50,60)
        directions = []
        for _ in range(direction_qty):
            angle = random.randint(1,360)
            directions.append((math.cos(angle),math.sin(angle)))
        for j in range(quantity):
            vel = random.uniform(1,9)
            self.particles.add(self.Particle(pos = [self.blit_size[0]/2,self.blit_size[1]/2],vel = [i*vel for i in directions[random.randint(0,len(directions)-1)]], color = [255,255,255,255], fade = 0.9))

class Dynamicentity(Staticentity):
    def __init__(self,pos):
        super().__init__(pos)
        self.collision_types = {'top':False,'bottom':False,'right':False,'left':False}

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.bottom=self.rect.bottom

    def update_hitbox(self):
        self.hitbox.midbottom = self.rect.midbottom#[self.rect.bottom + self.hitbox_offset[0], self.rect.bottom + self.hitbox_offset[1]]

    def update_rect(self):
        self.rect.midbottom = self.hitbox.midbottom#[self.hitbox.bottom - self.hitbox_offset[0], self.hitbox.bottom - self.hitbox_offset[1]]

class Character(Dynamicentity):#enemy, NPC,player
    def __init__(self,pos):
        super().__init__(pos)
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]
        self.acceleration=[1,0.7]
        self.velocity=[0,0]
        self.friction=[0.2,0]
        self.animation_stack=[animation.Entity_animation(self)]#maybe it is better to assign animation class based on the speific entity, since some doesn't have pre,main,post
        self.max_vel=7

    def update(self,pos):
        self.update_pos(pos)
        self.currentstate.update()
        self.animation_stack[-1].update()

    def take_dmg(self,dmg):
        if dmg>0:
            self.health-=dmg
            if self.health>0:#check if dead¨
                self.hurt_animation()#become white
                self.currentstate.handle_input('Hurt')#handle if we shoudl go to hurt state
            else:
                self.currentstate.change_state('Death')#overrite any state and go to death

    def hurt_animation(self):
        if str(type(self.animation_stack[-1]).__name__) != 'Hurt_animation':#making sure to not append more than one hurt animation at time
            new_animation=animation.Hurt_animation(self)
            new_animation.enter_state()

    def set_pos(self, pos):
        self.rect.center = (pos[0],pos[1])
        self.hitbox.midbottom = self.rect.midbottom

    def group_distance(self):
        bounds=[-100,600,-100,350]#-x,+x,-y,+y. #shuodl change to player distance?
        if self.rect[0]<bounds[0] or self.rect[0]>bounds[1] or self.rect[1]<bounds[2] or self.rect[1]>bounds[3]: #or abs(entity.rect[1])>300:#this means it is outside of screen
            self.remove(self.group)#remove from group
            self.add(self.pause_group)#add to pause
        else:
            self.add(self.group)#add to group
            self.remove(self.pause_group)#remove from pause

class Enemy(Character):
    def __init__(self,pos,projectile_group,loot_group,enemy_group,pause_group):
        super().__init__(pos)
        self.projectiles = projectile_group
        self.loot_group = loot_group
        self.group = enemy_group
        self.pause_group = pause_group
        self.inventory = {'Amber_Droplet':random.randint(0, 10)}#random.randint(0, 10)
        self.currentstate = states_enemy.Idle(self)
        self.counter=0
        self.AImethod=self.peaceAI
        self.player_distance=[0,0]
        self.aggro=True
        self.max_vel=3
        self.friction=[0.5,0]

    def update(self,pos,playerpos):
        super().update(pos)
        self.AI(playerpos)
        self.group_distance()

    def loots(self):
        for key in self.inventory.keys():#go through all loot
            for i in range(0,self.inventory[key]):#make that many object for that specific loot and add to gorup
                obj=getattr(sys.modules[__name__], key)([self.rect.x,self.rect.y])#make a class based on the name of the key: need to import sys
                self.loot_group.add(obj)
            self.inventory[key]=0

    def countered(self):
        self.velocity[0]=-30*self.dir[0]
        duration=30
        self.currentstate = states_enemy.Stun(self,duration)#should it overwrite?

    def knock_back(self,dir):
        self.velocity[0]=dir*30

    def AI(self,playerpos):
        self.player_distance=[playerpos[0]-self.rect.centerx,playerpos[1]-self.rect.centerx]#check plater distance
        self.updateAI()#decide aggro or peace
        self.counter += 1
        self.AImethod()#run ether aggro- or peace-AI

    def updateAI(self):#move these into AI methods
        if abs(self.player_distance[0])<200 and self.AImethod.__name__ != 'aggroAI':
            self.AImethod=self.aggroAI
        elif abs(self.player_distance[0])>200 and self.AImethod.__name__ != 'peaceAI':
            self.AImethod=self.peaceAI

    def peaceAI(self):
        if self.counter>20:
            self.counter=0
            rand=random.randint(0,1)
            if rand==0:
                self.currentstate.handle_input('Idle')
            else:
                self.currentstate.handle_input('Walk')

    def aggroAI(self):
        if self.counter < 40:
            pass
        else:
            if self.player_distance[0] > self.attack_distance:
                self.dir[0] = 1
                self.currentstate.handle_input('Run')
            elif abs(self.player_distance[0])<self.attack_distance:
                self.currentstate.handle_input('Attack')
                self.counter = 0
            elif self.player_distance[0] < -self.attack_distance:
                self.dir[0] = -1
                self.currentstate.handle_input('Run')
            else:
                self.counter = 0
                self.currentstate.handle_input('Idle')

class Woopie(Enemy):
    def __init__(self,pos,projectile_group,loot_group,enemy_group,pause_group):
        super().__init__(pos,projectile_group,loot_group,enemy_group,pause_group)
        self.image = pygame.image.load("Sprites/Enteties/enemies/woopie/main/Idle/Kodama_stand1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,30)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health = 1
        self.spirit=100
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/woopie/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.attack_distance=0

class Vatt(Enemy):

    aggro = False  #remember to turn false when changing maps
    def __init__(self,pos,projectile_group,loot_group,enemy_group,pause_group):
        super().__init__(pos,projectile_group,loot_group,enemy_group,pause_group)
        self.image = pygame.image.load("Sprites/Enteties/enemies/vatt/main/idle/idle1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],16,30)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health = 30
        self.spirit = 30
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/vatt/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.currentstate = states_vatt.Idle(self)
        self.attack_distance = 60
        self.aggro=False

    def updateAI(self):
        if Vatt.aggro and not self.aggro:
            self.currentstate.change_state('Transform')#also sets to aggro AI
            self.aggro = True
            #self.AImethod=self.aggroAI

    def peaceAI(self):
        if self.counter>70:
            self.counter=0
            rand=random.randint(0,6)
            if rand<2:
                self.currentstate.handle_input('Idle')
            else:
                self.currentstate.handle_input('Walk')

    def aggroAI(self):
        if self.counter < 40:
            pass
        else:
            if self.player_distance[0] > self.attack_distance:
                self.dir[0] = 1
                self.currentstate.handle_input('Run')
            elif self.player_distance[0] < -self.attack_distance:
                self.dir[0] = -1
                self.currentstate.handle_input('Run')
            else:
                self.counter = 0
                self.currentstate.handle_input('Javelin')

class Flowy(Enemy):
    def __init__(self,pos,projectile_group,loot_group,enemy_group,pause_group):
        super().__init__(pos,projectile_group,loot_group,enemy_group,pause_group)
        self.image = pygame.image.load("Sprites/Enteties/enemies/flowy/main/Idle/Stand1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,40)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health = 10
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/flowy/')
        self.spirit=10

class Larv(Enemy):
    def __init__(self,pos,projectile_group,loot_group,enemy_group,pause_group):
        super().__init__(pos,projectile_group,loot_group,enemy_group,pause_group)
        self.image = pygame.image.load("Sprites/Enteties/enemies/larv/main/Idle/catapillar_idle1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,30)
        self.health = 10
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/larv/')
        self.spirit=10
        self.attack=Poisonblobb
        self.attack_distance=60

class Player(Character):

    sfx_sword = pygame.mixer.Sound("Audio/SFX/utils/sword_3.ogg")

    def __init__(self,pos,projectile_group,cosmetics_group):
        super().__init__(pos)
        self.image = pygame.image.load("Sprites/Enteties/aila/main/Idle/aila_idle1.png").convert()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],16,35)
        self.rect.midbottom=self.hitbox.midbottom#match the positions of hitboxes
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/aila/')
        self.max_health = 250
        self.max_spirit = 100
        self.health = 100
        self.spirit = 100

        self.cosmetics = cosmetics_group
        self.projectiles = projectile_group#pygame.sprite.Group()

        self.abilities={'Hammer':Hammer,'Force':Force,'Arrow':Arrow,'Heal':Heal,'Darksaber':Darksaber}#'Shield':Shield#the objects are referensed but made in states
        self.equip='Hammer'#ability pointer
        self.sword=Sword(self)
        self.shield=Shield

        #can be removed?
        #self.action_sfx_player = pygame.mixer.Channel(1)
        #self.action_sfx_player.set_volume(0.1)
        #self.action_sfx = {'run': pygame.mixer.Sound("Audio/SFX/player/footstep.mp3")}
        #self.movement_sfx_timer = 110

        self.inventory={'Amber_Droplet':10}#the keys need to have the same name as their respective classes
        self.omamoris=Omamoris(self)
        self.currentstate = states_player.Idle(self)

    #def load_sfx(self):#make a sound class
    #    if self.action['run'] and not self.action['fall'] and self.movement_sfx_timer > 15:
    #        self.action_sfx_player.play(self.action_sfx['run'])
    #        self.movement_sfx_timer = 0
    #    self.movement_sfx_timer += 1

    def enter_idle(self):
        self.currentstate = states_player.Idle(self)

    def reset_movement(self):
        self.velocity = [0,0]
        self.acceleration = [0,0.7]
        self.friction = [0.2,0]

    def update(self,pos):
        super().update(pos)
        self.omamoris.update()

    def equip_omamori(self,omamori_index):
        new_omamori=self.omamoris.omamori_list[omamori_index]
        if new_omamori not in self.omamoris.equipped_omamoris:#add the omamori
            if len(self.omamoris.equipped_omamoris)<3:#maximum number of omamoris to equip
                self.omamoris.equipped_omamoris.append(new_omamori)
                new_omamori.attach()
        else:#remove the omamori
            old_omamori=self.omamoris.omamori_list[omamori_index]
            self.omamoris.equipped_omamoris.remove(old_omamori)
            old_omamori.detach()#call the detach function of omamori

class NPC(Character):
    def __init__(self,pos,npc_group,pause_group):
        super().__init__(pos)
        self.group = npc_group
        self.pause_group = pause_group
        self.name = str(type(self).__name__)#the name of the class
        self.health = 50
        self.conv_index = 0
        self.currentstate = states_NPC.Idle(self)

    def load_conversation(self):
        self.conversation = Read_files.read_json("Text/NPC/" + self.name + ".json")

    #returns conversation depdening on worldstate input. increases index
    def get_conversation(self, flag):
        try:
            conv = self.conversation[flag][str(self.conv_index)]
        except:
            self.conv_index -= 1
            return None
        return conv

    def reset_conv_index(self):
        self.conv_index = 0

    def increase_conv_index(self):
        self.conv_index += 1

    def update(self, pos,playerpos):
        super().update(pos)
        self.AI()
        self.group_distance()

    def idle(self):
        self.currentstate.handle_input('Idle')

    def walk(self):
        self.currentstate.handle_input('Walk')

class Aslat(NPC):
    def __init__(self, pos,npc_group,pause_group):
        super().__init__(pos,npc_group,pause_group)
        self.sprites = Read_files.Sprites_Player("Sprites/Enteties/NPC/" + self.name + "/animation/")
        self.image = self.sprites.get_image('idle', 0, self.dir, 'main')
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],18,40)
        self.rect.bottom = self.hitbox.bottom   #match bottom of sprite to hitbox
        self.portrait=pygame.image.load('Sprites/Enteties/NPC/MrBanks/Woman1.png').convert_alpha()  #temp
        self.load_conversation()
        #self.max_vel = 1.5
        self.counter=0

    def AI(self):
        self.counter+=1
        if self.counter>100:
            self.counter=0
            rand=random.randint(0,1)
            if rand==0:
                self.idle()
            else:
                self.walk()
#        if self.action['inv']:#collision with invisble block
#            self.velocity[0] = -self.velocity[0]
#            self.dir[0] = -self.dir[0]
#            self.action['inv'] = False

class MrBanks(NPC):
    def __init__(self,pos,npc_group,pause_group):
        super().__init__(pos,npc_group,pause_group)
        self.name = 'MrBanks'
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],20,48)
        self.rect.center = self.hitbox.center#match the positions of hitboxes
        self.portrait=pygame.image.load('Sprites/Enteties/NPC/'+self.name+ '/Woman1.png').convert_alpha()
        self.text_surface=pygame.image.load("Sprites/Enteties/NPC/conv/Conv_BG.png").convert_alpha()
        self.sprites = Read_files.Sprites_enteties("Sprites/Enteties/NPC/" + self.name + "/animation/")
        self.conversation=Read_files.Conversations('Sprites/Enteties/NPC/'+self.name+ '/conversation.txt')#a dictionary of conversations with "world state" as keys
        self.conv_action=['deposit','withdraw']
        self.conv_action_BG=pygame.image.load("Sprites/Enteties/NPC/conv/Conv_action_BG.png").convert_alpha()
        self.conv_possition=[[400],[300]]

        self.loot={'Coin':2}#the keys need to have the same name as their respective classes
        self.business=False
        self.ammount=0


    def AI(self):
        if abs(self.rect[0])>500 or abs(self.rect[1])>500:#if far away
            self.stay_still()
        else:
            self.move_again()



    def blit_conv_action(self,game_screen):
        game_screen.blit(self.conv_action_BG,(850,200))#the text BG

        if not self.business:#if not busness

            if self.conv_idx[1]<=0:
                self.conv_idx[1]=0
            elif self.conv_idx[1]>=len(self.conv_action):
                self.conv_idx[1]=len(self.conv_action)-1

            self.font.render(game_screen,'o',(930,self.conv_possition[1][self.conv_idx[1]]),1)#call the self made aplhabet blit and blit the conversation
            self.conv_possition=[[],[]]

            scale=[1]*len(self.conv_action)
            scale[self.conv_idx[1]]=2
            i=1

            for conv in self.conv_action:
                self.font.render(game_screen,conv,(950,250+50*i),scale[i-1])#call the self made aplhabet blit and blit the conversation
                self.conv_possition[1].append(250+50*i)
                i+=1
        else:#if buisness
            game_screen.blit(self.conv_action_BG,(850,200))#the text BG
            self.font.render(game_screen,str(self.ammount)+' coins?',(940,300),1)#call the self made aplhabet blit and blit the conversation
            self.font.render(game_screen,self.conv_action[self.conv_idx[1]]+'?',(930,270),1)#call the self made aplhabet blit and blit the conversation

            self.conv_possition[0]=[920,1020]

            if self.conv_idx[0]<=0:
                self.conv_idx[0]=0
            elif self.conv_idx[0]>=2:
                self.conv_idx[0]=1
            scale=[1,1]#yes or no
            scale[self.conv_idx[0]]=2

            self.font.render(game_screen,'Yes',(940,400),scale[0])#call the self made aplhabet blit and blit the conversation
            self.font.render(game_screen,'No',(1040,400),scale[1])#call the self made aplhabet blit and blit the conversation
            self.font.render(game_screen,'o',(self.conv_possition[0][self.conv_idx[0]],400),1)#call the self made aplhabet blit and blit the conversation

    def trade(self,player):#exchane of money
        if self.conv_idx[0]==0:#if press yes
            if self.conv_action[self.conv_idx[1]] == 'deposit':
                player.loot['Coin']-=self.ammount
                self.loot['Coin']+=self.ammount
            elif self.conv_action[self.conv_idx[1]] == 'withdraw':
                player.loot['Coin']+=self.ammount
                self.loot['Coin']-=self.ammount
        else:#if press no
            self.buisness=False
            self.ammount=0

    def upinteger(self,player):
        self.ammount+=1*int(self.business)
        if self.conv_action[self.conv_idx[1]] == 'deposit':
            self.ammount=min(player.loot['Coin'],self.ammount)
        elif self.conv_action[self.conv_idx[1]] == 'withdraw':
            self.ammount=min(self.loot['Coin'],self.ammount)

    def downinteger(self,player):
        self.ammount-=1*int(self.business)
        self.ammount=max(0,self.ammount)#minimum 0

class Boss(Character):
    def __init__(self,pos,projectile_group,loot_group):
        super().__init__(pos,projectile_group,loot_group)
        self.projectiles = projectile_group
        self.loot_group = loot_group
        self.inventory = {'Amber_Droplet':random.randint(0, 10)}#random.randint(0, 10)
        self.currentstate = states_boss.Idle(self)

    def knock_back(self,dir):
        pass

class Reindeer(Boss):
    def __init__(self,pos,projectile_group,loot_group):
        super().__init__(pos,projectile_group,loot_group)
        self.image = pygame.image.load("Sprites/Enteties/boss/reindeer/main/idle/raindeer_idle1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],40,50)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health = 1000
        self.spirit=1000
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/boss/reindeer/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')

    def AI(self,playerpos):
        pass

class Path_col(Staticentity):

    def __init__(self, pos, size, destination, spawn):
        super().__init__(pos, pygame.Surface(size))
        self.rect.bottomleft = pos
        self.hitbox = self.rect.inflate(0,0)
        self.destination = destination
        self.spawn = spawn

    def update(self, pos):
        super().update(pos)
        self.hitbox.center = self.rect.center

#legacy code --- delete???
class Trigger(pygame.sprite.Sprite):

    def __init__(self,pos):
        super().__init__()
        self.rect = pygame.Rect(pos, (16,16))
        self.hitbox = self.rect.inflate(0,0)

    def update(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.center=self.rect.center

class Path_Col_v(Trigger):


    def __init__(self,pos,destination):
        super().__init__(pos)
        ext = 32
        self.rect = pygame.Rect((pos[0],pos[1]-ext), (16,16+(2*ext)))
        self.hitbox = self.rect.inflate(0,0)
        self.next_map = destination
        self.image = pygame.Surface((16,16+(2*ext)))
        self.image.fill((0,0,0))

class Path_Col_h(Trigger):

    def __init__(self,pos,destination):
        super().__init__(pos)
        ext = 32
        self.rect = pygame.Rect((pos[0]-ext,pos[1]), (16+(2*ext),16))
        self.hitbox = self.rect.inflate(0,0)
        self.next_map = destination
        self.image = pygame.Surface((16+(2*ext),16))
        self.image.fill((0,0,0))

class Camera_Stop(pygame.sprite.Sprite):

    def __init__(self,size,pos,dir):
        super().__init__()
        self.rect=pygame.Rect((pos),size)
        self.hitbox = self.rect.inflate(0,0)
        self.dir = dir
        self.image = pygame.Surface((16,16))
        self.image.fill((0,0,0))

    def update(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.center=self.rect.center

class Interactable(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.interacted = False

    def update(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.center=self.rect.center

class Pathway(Interactable):

    def __init__(self, destination):
        super().__init__()
        self.next_map = destination

class Door(Pathway):

    def __init__(self,pos,destination):
        super().__init__(destination)
        self.image_sheet = Read_files.Sprites().generic_sheet_reader("Sprites/animations/Door/door.png",32,48,1,4)
        self.image = self.image_sheet[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(0,0)
        self.timer = 0

    def update(self,pos):
        super().update(pos)
        if self.interacted:
            if self.timer < 21:
                self.image = self.image_sheet[self.timer//7]
                self.timer += 1
            else:
                self.image = self.image_sheet[3]

class Chest(Interactable):
    def __init__(self,pos,id,loot,state):
        super().__init__()
        self.image_sheet = Read_files.Sprites().generic_sheet_reader("Sprites/animations/Chest/chest.png",16,21,1,3)
        self.image = self.image_sheet[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos[0],pos[1]-5)
        self.hitbox = self.rect.inflate(0,0)
        self.timer = 0
        self.ID = id
        self.loot = {loot:1}
        if state == "opened":
            self.opened()

    def opened(self):
        self.image = self.image_sheet[2]
        self.timer = 9
        self.interacted = True

    def update(self,pos):
        super().update(pos)
        if self.interacted:
            if self.timer < 8:
                self.image = self.image_sheet[1]
                self.timer += 1
            else:
                self.image = self.image_sheet[2]

class Chest_Big(Interactable):
    def __init__(self,pos,id,loot,state):
        super().__init__()
        self.image_sheet = Read_files.Sprites().generic_sheet_reader("Sprites/animations/Chest/chest_big.png",32,29,1,5)
        self.image = self.image_sheet[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos[0],pos[1]-13)
        self.hitbox = self.rect.inflate(0,0)
        self.timer = 0
        self.ID = id
        self.loot = loot
        if state == "opened":
            self.opened()

    def opened(self):
        self.image = self.image_sheet[4]
        self.timer = 29
        self.interacted = True

    def update(self,pos):
        super().update(pos)
        if self.interacted:
            if self.timer < 28:
                self.image = self.image_sheet[self.timer//7]
                self.timer += 1
            else:
                self.image = self.image_sheet[4]
                self.interacted = False

class Abilities(pygame.sprite.Sprite):
    def __init__(self,entity):
        super().__init__()
        self.entity=entity
        self.state='main'
        self.animation=animation.Ability_animation(self)

    def update(self,pos):
        self.lifetime-=1
        self.update_pos(pos)
        self.animation.update()
        self.destroy()

    def destroy(self):
        if self.lifetime<0:
            self.kill()

    def collision_enemy(self,collision_enemy):
        self.kill()

    def collision_plat(self):
        pass

class Heal(Abilities):
    def __init__(self,entity):
        super().__init__(entity)

class Melee(Abilities):
    def __init__(self,entity):
        super().__init__(entity)
        self.rectangle()
        self.dir=entity.dir.copy()

    def rectangle(self):
        self.rect = pygame.Rect(self.entity.rect.x,self.entity.rect.y,40,40)
        self.hitbox = self.rect.copy()

    def update_pos(self,scroll):
        self.rect.topleft = [self.rect.topleft[0] + scroll[0], self.rect.topleft[1] + scroll[1]]
        self.hitbox.center = self.rect.center

    def update_hitbox(self):#make this a dictionary?
        if self.dir[1] > 0:#up
            self.hitbox.midbottom=self.entity.hitbox.midtop
            self.dir[0] = 0#no knock back when hit from below or above
        elif self.dir[1] < 0:#down
            self.hitbox.midtop=self.entity.hitbox.midbottom
            self.dir[0] = 0 #no knock back when hit from below or above
        elif self.dir[0] > 0:#right
            self.hitbox.midleft=self.entity.hitbox.midright
        elif self.dir[0] < 0:#left
            self.hitbox.midright=self.entity.hitbox.midleft
        self.rect.center=self.hitbox.center#match the positions of hitboxes

    def update(self,pos):
        super().update(pos)
        self.update_hitbox()

    def countered(self):
        self.entity.countered()
        self.kill()

class Sword(Melee):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Attack/Sword/')

    def __init__(self,entity):
        super().__init__(entity)
        self.dmg=10

    def collision_enemy(self,collision_enemy):
        self.sword_jump()
        collision_enemy.knock_back(self.dir[0])
        slash=Slash([collision_enemy.rect.x,collision_enemy.rect.y])
        clash = Particle_effect_attack([collision_enemy.rect.x,collision_enemy.rect.y])
        self.entity.cosmetics.add(clash)
        self.kill()

    def sword_jump(self):
        if self.dir[1]==-1:
            self.entity.velocity[1]=-11

class Darksaber(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.dmg=0
        self.lifetime=10#swrod hitbox duration

    def collision_enemy(self,collision_enemy):
        if collision_enemy.spirit>=10:
            collision_enemy.spirit-=10
            spirits=Spiritsorb([collision_enemy.rect.x,collision_enemy.rect.y])
            collision_enemy.loot_group.add(spirits)
        self.kill()

class Shield(Melee):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Attack/Shield/')

    def __init__(self,entity):
        super().__init__(entity)
        self.dmg=0
        self.lifetime=10

    def rectangle(self):
        self.rect = pygame.Rect(self.entity.rect[0],self.entity.rect[1],80,80)
        self.hitbox = self.rect.copy()

    def update_hitbox(self):
        self.rect.midtop=self.entity.rect.midtop

    def collision_enemy(self,collision_enemy):
        collision_enemy.countered()
        self.kill()

class Projectiles(Abilities):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()
        self.rectangle()
        self.velocity=[0,0]

    def rectangle(self):
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.hitbox=self.rect.copy()

    def update_pos(self,scroll):
        self.rect.topleft = [self.rect.topleft[0] + self.velocity[0]+scroll[0], self.rect.topleft[1] + self.velocity[1]+scroll[1]]
        self.hitbox.center = self.rect.center

    def update_hitbox(self):
        if self.dir[1] > 0:#up
            self.hitbox.midbottom=self.entity.hitbox.midtop
            self.velocity[1]=-self.speed[1]
        elif self.dir[1] < 0:#down
            self.hitbox.midtop=self.entity.hitbox.midbottom
            self.velocity[1]=self.speed[1]
        elif self.dir[0] > 0 and self.dir[1] == 0:#right
            self.hitbox.midleft=self.entity.hitbox.midright
            self.velocity[0]=self.speed[0]
        elif self.dir[0] < 0 and self.dir[1] == 0:#left
            self.hitbox.midright=self.entity.hitbox.midleft
            self.velocity[0]=-self.speed[1]
        self.rect.center=self.hitbox.center#match the positions of hitboxes

    def knock_back(self):
        self.velocity[0]=-self.velocity[0]
        self.velocity[1]=-self.velocity[1]

    def countered(self,projectile):
        projectile.entity.projectiles.add(self)#add the projectilce to Ailas projectile group
        self.knock_back()

class Hammer(Projectiles):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Attack/Hammer/')

    def __init__(self,entity):
        super().__init__(entity)
        self.dmg=10
        self.lifetime=25
        self.speed=[0,0]
        self.update_hitbox()

        self.rect.bottom=self.entity.rect.bottom
        self.hitbox.center = self.rect.center

    def collision_enemy(self,collision_enemy):
        self.dmg=0

class Poisoncloud(Projectiles):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Attack/Poisoncloud/')

    def __init__(self,entity):
        super().__init__(entity)
        self.dmg=1
        self.lifetime=400
        self.speed=[0,0]
        self.update_hitbox()

    def collision_ene(self,collision_ene):
        pass

    def destroy(self):
        if self.lifetime<0:
            self.animation.reset_timer()
            self.state='post'

    def countered(self):
        self.animation.reset_timer()
        self.state='post'

class Poisonblobb(Projectiles):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Attack/Poisonblobb/')

    def __init__(self,entity):
        super().__init__(entity)
        self.dmg=10
        self.lifetime=100
        self.speed=[4,4]
        self.hitbox=pygame.Rect(self.rect.x,self.rect.y,16,16)
        self.update_hitbox()

    def update(self,scroll):
        self.update_vel()
        super().update(scroll)

    def update_vel(self):
        self.velocity[1]+=0.1#graivity

    def collision_plat(self):
        self.velocity=[0,0]
        if self.state=='main':
            self.animation.reset_timer()
            self.state='post'

class Stone(Abilities):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Attack/Stone/')

    def __init__(self,entity):
        super().__init__(entity)
        self.lifetime=100
        self.dmg=10
        self.charge_velocity=0
        self.action='small'
        self.initiate()
        self.hitbox=pygame.Rect(self.rect.x,self.rect.y,10,10)

    def update_hitbox(self):
        if self.dir[1] > 0:#up
            self.hitbox.midbottom=self.entity.hitbox.midtop
        elif self.dir[1] < 0:#down
            self.hitbox.midtop=self.entity.hitbox.midbottom
        elif self.dir[0] > 0 and self.dir[1] == 0:#right
            self.hitbox.midleft=self.entity.hitbox.midright
        elif self.dir[0] < 0 and self.dir[1] == 0:#left
            self.hitbox.midright=self.entity.hitbox.midleft
        self.rect.center=self.hitbox.center#match the positions of hitboxes

    def update(self,pos):
        self.update_pos(pos)
        self.update_animation()#has to be here
        self.speed()#set the speed
        self.destroy()

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='charge'
        elif self.phase=='main':
            pass
        elif self.phase=='post':
            self.kill()

    def speed(self):
        if self.phase=='charge':#charging
            self.charge_velocity=self.charge_velocity+0.5*self.dir[0]
            self.charge_velocity=self.dir[0]*min(20,self.dir[0]*self.charge_velocity)#set max velocity

            if abs(self.charge_velocity)>=20:#increase the ball size when max velocity is reached
                self.action='medium'
                self.shake=2#add shake effect if the ball is big

        elif self.phase=='main':#main pahse
            self.lifetime-=1#affect only the lifetime in main state
            if self.action=='small':#only have gravity if small
                self.velocity[1]+=0.1#graivity

    def collision_enemy(self,collision_enemy):
        self.velocity=[0,0]
        self.dmg=0
        self.phase='post'

    def collision_plat(self):
        self.velocity=[0,0]
        self.dmg=0
        self.phase='post'

    def rotate(self):
        angle=self.dir[0]*max(-self.dir[0]*self.velocity[0]*self.velocity[1],-60)

        self.image=pygame.transform.rotate(self.original_image,angle)#fig,angle,scale
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.hitbox=pygame.Rect(x,y,10,10)

        self.rect.center = (x, y)  # Put the new rect's center at old center.

    def knock_back(self):
        self.velocity[0]=-self.velocity[0]
        self.velocity[1]=-self.velocity[1]

    def countered(self):
        super().countered()
        self.knock_back()

class Force(Projectiles):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Attack/Force/')

    def __init__(self,entity):
        super().__init__(entity)
        self.lifetime=30
        self.dmg=0
        self.state='pre'
        self.speed=[10,10]
        self.update_hitbox()

    def collision_plat(self):
        self.animation.reset_timer()
        self.state='post'
        self.velocity=[0,0]

    def collision_enemy(self,collision_enemy):#if hit something
        self.animation.reset_timer()
        self.state='post'
        self.velocity=[0,0]

        collision_enemy.velocity[0]=self.dir[0]*10#abs(push_strength[0])
        collision_enemy.velocity[1]=-6

class Arrow(Projectiles):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Attack/Arrow/')

    def __init__(self,entity):
        super().__init__(entity)
        self.lifetime=100
        self.dmg=10
        self.speed=[10,10]
        self.update_hitbox()


    def collision_enemy(self,collision_enemy):
        self.velocity=[0,0]
        self.dmg=0
        self.kill()

    def collision_plat(self):
        self.velocity=[0,0]
        self.dmg=0

class Loot(Dynamicentity):
    def __init__(self,pos):
        super().__init__(pos)
        self.lifetime=500
        self.state='idle'
        self.animation=animation.Basic_animation(self)

    def destory(self):
        if self.lifetime<0:#remove after a while
            self.kill()

    def update(self,scroll):
        self.lifetime-=1
        self.update_pos(scroll)
        self.update_vel()
        self.animation.update()
        self.destory()

class Amber_Droplet(Loot):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/amber_droplet/')

    def __init__(self,pos):
        super().__init__(pos)
        self.velocity=[random.randint(-3, 3),-4]
        self.rect = pygame.Rect(pos[0],pos[1],5,5)#resize the rect
        self.hitbox = self.rect.copy()

    def check_collisions(self):
        if self.collision_types['bottom']:
            self.velocity[0] = 0.5*self.velocity[0]
            self.velocity[1] = -0.7*self.velocity[1]
        elif self.collision_types['right'] or self.collision_types['left']:
            self.velocity[0] = -self.velocity[0]

    def update_vel(self):
        self.velocity[1] += 0.5

    def update(self,pos):
        self.check_collisions()#need to be before super.update
        super().update(pos)

    def pickup(self,player):
        obj=(self.__class__.__name__)#get the loot in question
        player.inventory[obj]+=1
        self.kill()

class Spiritsorb(Loot):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/spiritorbs/')

    def __init__(self,pos):
        super().__init__(pos)
        rand_pos=[random.randint(-10, 10),random.randint(-10, 10)]
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0]+rand_pos[0],pos[1]+rand_pos[1],5,5)
        self.hitbox=self.rect.copy()

    def update_vel(self):
        self.velocity=[0.1*random.randint(-10, 10),0.1*random.randint(-10, 10)]

    def pickup(self,player):
        player.spirit += 10
        self.kill()

class Animatedentity(Staticentity):#animated without hitbox
    def __init__(self,pos):
        super().__init__(pos)
        self.state='idle'
        self.animation=animation.Basic_animation(self)

    def update(self,scroll):
        self.update_pos(scroll)
        self.animation.update()

class Cosmetics(Animatedentity):
    def __init__(self,pos):
        super().__init__(pos)

    def update(self,scroll):
        self.lifetime-=1
        super().update(scroll)
        self.destroy()

    def destroy(self):
        if self.lifetime<0:
            self.kill()

class Slash(Cosmetics):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/GFX/slash/')

    def __init__(self,pos):
        super().__init__(pos)
        self.state=str(random.randint(1, 3))
        self.image = self.sprites[self.state][0]#not sure why we need this.... there is a black box without
        self.lifetime=10

class Menu_Arrow():

    def __init__(self):
        self.img = pygame.image.load("Sprites/utils/arrow.png")
        self.rect = self.img.get_rect()

    #note: sets pos to input, doesn't update with an increment of pos like other entities
    def update(self,pos):
        self.rect.topleft = pos

    def draw(self,screen):
        screen.blit(self.img, self.rect.topleft)

class Omamoris():
    def __init__(self,entity):
        self.equipped_omamoris=[]#equiped omamoris
        self.omamori_list=[Double_jump(entity),Double_sword(entity),More_spirit(entity)]#omamoris inventory.

    def update(self):
        for omamori in self.equipped_omamoris:
            omamori.update()

    def handle_input(self,input):
        for omamori in self.equipped_omamoris:
            omamori.handle_input(input)

class Omamori():
    def __init__(self,entity):
        self.entity=entity
        self.state='idle'
        self.animation=animation.Basic_animation(self)

    def update(self):
        pass

    def handle_input(self,input):
        pass

    def detach(self):
        self.state='idle'
        self.animation.reset_timer()

    def attach(self):
        self.state='equip'
        self.animation.reset_timer()

class Double_jump(Omamori):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/omamori/double_jump/')#for inventory

    def __init__(self,entity):
        super().__init__(entity)
        self.counter=0

    def update(self):
        if self.entity.collision_types['bottom'] or self.entity.collision_types['right'] or self.entity.collision_types['left']:
            self.reset_counter()

    def handle_input(self,input):
        if input[-1]=='a' and self.counter<1:
            self.entity.currentstate.handle_press_input('double_jump')
            if type(self.entity.currentstate).__name__=='Double_jump':
                self.counter+=1

    def reset_counter(self):
        self.counter=0

class Double_sword(Omamori):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/omamori/double_sword/')#for inventory

    def __init__(self,entity):
        super().__init__(entity)

    def detach(self):
        super().detach()
        self.entity.sword.rect = pygame.Rect(self.entity.rect.x,self.entity.rect.y,40,40)
        self.entity.sword.hitbox = self.entity.sword.rect.copy()

    def attach(self):
        super().attach()
        self.entity.sword.rect = pygame.Rect(self.entity.rect.x,self.entity.rect.y,80,40)
        self.entity.sword.hitbox = self.entity.sword.rect.copy()

class More_spirit(Omamori):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/omamori/more_spirit/')#for inventory

    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.spirit += 0.5

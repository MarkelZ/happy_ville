import pygame, Read_files, random, sys

class Entity(pygame.sprite.Sprite):

    acceleration=[1,0.8]

    def __init__(self):
        super().__init__()
        self.movement=[0,0]
        self.velocity=[0,0]
        self.frame = 0
        self.dir=[1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]
        self.ac_dir=self.dir.copy()
        self.world_state=0#state of happyness thingy of the world
        self.loot={'coin':0}
        self.collision_types = {'top':False,'bottom':False,'right':False,'left':False}
        self.collision_spikes = {'top':False,'bottom':False,'right':False,'left':False}
        self.phase='pre'

    def death(self,loot):
        if self.health<=0:#if 0 health of enemy
            self.action['death']=True
            self.velocity=[0,0]
            self.loots(loot)
            return self.shake#screen shake when eneny dies
        return 0

    def set_img(self):#action is set to true- > pre animation. When finished, main animation and set action to false -> do post animatino
        all_action=self.priority_action+self.nonpriority_action

        for action in all_action:#go through the actions
            if self.action[action] and action in self.priority_action:#if the action is priority

                if action != self.state:
                    self.state = action
                    self.reset_timer()

                self.image = self.sprites.get_image(action,self.frame//4,self.ac_dir)
                self.frame += 1

                if self.frame == self.sprites.get_frame_number(action,self.ac_dir)*4:
                    if action == 'death':
                        self.kill()
                    else:
                        self.reset_timer()
                        self.action[action] = False
                        self.state = 'stand'
                        self.action[self.equip]=False#to cancel even if you get hurt
                break

            elif self.action[action] and action in self.nonpriority_action:#if the action is nonpriority

                #reset timer if the action is wrong
                if action != self.state:
                    self.state = action
                    self.reset_timer()

                self.image = entity.sprites.get_image(action,self.frame//4,self.dir)
                self.frame += 1

                if self.frame == self.sprites.get_frame_number(action,self.dir)*4:
                        self.reset_timer()
                break#take only the higest priority of the nonpriority list

    def AI(self,knight):
        pass

    def attack_action(self,projectiles):
        return projectiles

    def update(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.center=self.rect.center

    def update_action(self, new_action):
        if not self.action[new_action]:
            self.action[new_action] = True
            self.timer = 0

    def update_hitbox(self):
        self.hitbox.center = self.rect.center

    def update_rect(self):
        self.rect.center = self.hitbox.center

    def reset_timer(self):
        self.frame = 0
        self.ac_dir[0]=self.dir[0]
        self.ac_dir[1]=self.dir[1]

    def loots(self,loot):
        for key in self.loot.keys():#go through all loot
            for i in range(0,self.loot[key]):#make that many object for that specific loot and add to gorup
                #obj=globals()[key]#make a class based on the name of the key: using global stuff
                obj=getattr(sys.modules[__name__], key)#make a class based on the name of the key: need to import sys
                #obj=eval(key)#make a class based on the name of the key: apperently not a good solution
                loot.add(obj(self.hitbox))
            self.loot[key]=0
        return loot

class Player(Entity):

    def __init__(self,pos):
        super().__init__()
        self.image = pygame.image.load("Sprites/Enteties/aila/main/stand/aila_idle1.png").convert()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],16,35)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.sprites = Read_files.Sprites_Enteties('Sprites/Enteties/aila/',True)#Read_files.Sprites_player()
        self.health = 200
        self.max_health = 250
        self.spirit = 100
        self.max_spirit = 100
        self.priority_action=['death','hurt','dash','sword','bow','force']#animation
        self.nonpriority_action=['jump','wall','fall','run','stand']#animation
        self.action={'stand':True,'run':False,'sword':False,'jump':False,'death':False,'hurt':False,'bow':False,'dash':False,'wall':False,'fall':False,'inv':False,'talk':False,'force':False}
        self.state = 'stand'
        self.equip='sword'#can change to bow
        self.sword=Sword(self.dir,self.hitbox)
        self.hitbox_offset = (0,13)
        self.interacting = False
        self.friction=[0.2,0]
        self.loot={'Coin':10,'Arrow':20}#the keys need to have the same name as their respective classes
        self.action_cooldown=False
        self.shake=0
        self.dashing_cooldown=10
        self.charging=[False]#a list beause to make it a pointer

        #frame rates
        self.frame_limit={'death':10,'hurt':10,'dash':16,'sword':8,'bow':4,'force':10}
        self.action_framerate={}
        for action in self.frame_limit.keys():#framerate for the main phase
            self.action_framerate[action]=int(self.frame_limit[action]/self.sprites.get_frame_number(action,self.ac_dir,'main'))

    def set_img(self):
        all_action=self.priority_action+self.nonpriority_action

        for action in all_action:#go through the actions
            if self.action[action]:

                if action != self.state and self.phase!='post':#changing action
                    self.state = action
                    self.reset_timer()#reset frame an remember the direction
                    self.phase = 'pre'

                if self.phase=='pre' or self.phase=='charge':

                    self.image = self.sprites.get_image(action,self.frame//4,self.ac_dir,self.phase)
                    self.frame += 1

                    if self.frame == self.sprites.get_frame_number(action,self.ac_dir,self.phase)*4:
                        if action == 'death':
                            self.kill()
                        else:
                            self.frame=0
                            if self.charging[0] and action in ['sword','bow','force']:#do not set chagre while standing/running
                                self.phase='charge'
                            else:
                                self.phase = 'main'
                    break

                elif self.phase == 'main':
                    if action in self.priority_action:#priority action

                        self.image = self.sprites.get_image(action,self.frame//self.action_framerate[action],self.ac_dir,self.phase)
                        self.frame += 1

                        if self.frame == self.frame_limit[action]:
                            self.frame=0

                            if self.sprites.get_frame_number(action,self.ac_dir,'post') == 0:#if there is no post animation
                                self.phase = 'pre'
                                self.action_cooldown = False
                                self.action[action] = False
                            else:
                                self.phase = 'post'
                        break

                    elif action in self.nonpriority_action:#none-priority actions

                        self.image = self.sprites.get_image(action,self.frame//4,self.dir,self.phase)
                        self.frame += 1

                        if self.frame == self.sprites.get_frame_number(action,self.dir,self.phase)*4:
                            self.frame=0
                            if self.sprites.get_frame_number(self.state,self.ac_dir,'post') != 0:#if there is post animation
                                self.phase = 'post'
                        break

                else:#if post animation
                    self.image = self.sprites.get_image(self.state,self.frame//4,self.ac_dir,'post')
                    self.frame += 1

                    if self.frame == self.sprites.get_frame_number(self.state,self.ac_dir,'post')*4:
                        self.frame=0
                        self.phase = 'pre'
                        self.action_cooldown = False#allow for new action after post animation
                        self.action[action] = False
                    break

    def set_pos(self, pos):
        self.rect.center = (pos[0],pos[1])
        self.hitbox.center = self.rect.center

    def attack_action(self,projectiles):
        if self.action[self.equip]:

            if self.phase == 'pre' and not self.action_cooldown:
                if self.equip=='bow' and self.spirit >= 10:

                    projectiles.add(Bow(self.ac_dir,self.hitbox,self.charging))
                    self.spirit -= 10
                    self.action_cooldown=True#cooldown flag

            elif self.phase == 'main' and not self.action_cooldown:#produce the object in the main animation
                if self.equip=='sword':
                    self.sword=Sword(self.ac_dir,self.hitbox)
                    projectiles.add(self.sword)
                elif self.equip == 'force' and self.spirit >= 10:
                    projectiles.add(Force(self.ac_dir,self.hitbox))
                    self.spirit -= 10
                    self.force_jump()
                self.action_cooldown=True#cooldown flag
        return projectiles

    def change_equipment(self):
        if self.state not in self.priority_action:#don't change if there are bow or sword already
            if self.equip == 'sword':
                self.equip = 'bow'
            elif self.equip == 'bow':
                self.equip = 'force'
            else:
                self.equip = 'sword'

    def force_jump(self):
        #if self.dir[1]!=0:
        self.velocity[1]=self.dir[1]*10#force jump

    def dashing(self):
        if self.spirit>=10 and not self.charging[0]:#if we have spirit
            self.velocity[0] = 30*self.dir[0]
            self.action['dash'] = True
            self.spirit -= 10
            self.action[self.equip]=False#cancel any action

    def jump(self):
        self.friction[1] = 0
        self.velocity[1]=-11
        self.action['jump']=True
        if self.action['wall']:
            self.velocity[0]=-self.dir[0]*10

    def talk(self):
        self.action['talk']=not self.action['talk']

    def update(self,pos):
        super(Player, self).update(pos)
        #self.update_hitbox()
        if self.spirit <= self.max_spirit:
            self.spirit += 0.1

    #    if self.action['sword']:
        self.sword.updates(self.hitbox)

        self.set_img()

    def update_hitbox(self):
        self.hitbox.center = [self.rect.center[0] + self.hitbox_offset[0], self.rect.center[1] + self.hitbox_offset[1]]

    def update_rect(self):
        self.rect.center = [self.hitbox.center[0] - self.hitbox_offset[0], self.hitbox.center[1] - self.hitbox_offset[1]]

    def loots(self,loot):
        pass

class Enemy_1(Player):
    def __init__(self,pos):
        super().__init__(pos)
        self.health=10
        self.distance=[0,0]
        self.inv=False#flag to check if collision with invisible blocks
        self.sprites = Read_files.Sprites_evil_knight()
        self.shake=self.hitbox.height/10

    def AI(self,player):#the AI

        self.distance[0]=int((self.rect[0]-player.rect[0]))#follow the player
        self.distance[1]=int((self.rect[1]-player.rect[1]))#follow the player

        if abs(self.distance[0])>150 and abs(self.distance[1])>40 or player.action['death'] or self.action['hurt']:#don't do anything if far away, or player dead or while taking dmg
            self.action['run']=False
            self.action['stand']=True

        elif abs(self.distance[0]<150) and abs(self.distance[1])<40:

            self.dir[0]=-Enemy_1.sign(self.distance[0])
            self.action['run']=True
            self.action['stand']=False

            if abs(self.distance[0])<40:#don't get too close
                self.action['run']=False
                self.action['stand']=True

        if abs(self.distance[0])<80 and abs(self.distance[1])<40 and not player.action['death']:#swing sword when close
            self.action[self.equip] = True

    @staticmethod
    def sign(x):
        if x>0: return 1
        return -1

class Enemy_2(Entity):
    def __init__(self,pos):
        super().__init__()
        self.image = pygame.image.load("Sprites/Enteties/enemies/flowy/stand/Stand1.png").convert()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,40)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health = 10
        self.priority_action=['death','hurt','sword','bow','trans']#animation
        self.nonpriority_action=['fall','run','stand']#animation
        self.action={'stand':True,'run':False,'sword':False,'death':False,'hurt':False,'bow':False,'fall':False,'trans':False,'dash':False}
        self.state = 'stand'
        self.equip='sword'
        self.sprites = Read_files.Flowy()
        self.friction=[0.2,0]
        self.loot={'Coin':2,'Arrow':1}#the keys need to have the same name as their respective classes
        self.distance=[0,0]
        self.shake=self.hitbox.height/10

    @staticmethod#a function to add glow around the entity
    def add_white(radius,colour,screen,pos):
        surf=pygame.Surface((2*radius,2*radius))
        pygame.draw.circle(surf,colour,(radius,radius),radius)
        surf.set_colorkey((0,0,0))
        screen.blit(surf,(pos[0]-radius,pos[1]-radius),special_flags=pygame.BLEND_RGB_ADD)

    def AI(self,player,screen):#the AI
        #light around the entity
        radius=max(20-abs(self.distance[0])//10,1)
        Enemy_2.add_white(radius,(20,0,0),screen,self.rect.center)#radius, clolor, screen,position

        self.distance[0]=int((self.rect[0]-player.rect[0]))#follow the player
        self.distance[1]=int((self.rect[1]-player.rect[1]))#follow the player

        if 100 < abs(self.distance[0])<200 and abs(self.distance[1])<100 and not player.action['death']:#swing sword when close
            self.action['trans'] = True

        elif abs(self.distance[0])<100 and abs(self.distance[1])<100 and not player.action['death']:#swing sword when close
            self.action[self.equip] = True

class Block(pygame.sprite.Sprite):

    def __init__(self,img,pos):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def update(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]

class Platform(Block):

    def __init__(self,img,pos,chunk_key=False):
        super().__init__(img,pos)
        self.hitbox = self.rect.inflate(0,0)
        self.chunk_key=chunk_key
        self.spike=False

    def update(self,pos):
        super().update(pos)
        self.hitbox.center=self.rect.center

class Spikes(Block):
    def __init__(self,img,pos,chunk_key=False):
        super().__init__(pygame.image.load("Sprites/level_sheets/Spkies.png").convert_alpha(),pos)
        self.hitbox = self.rect.inflate(0,0)
        self.chunk_key=chunk_key
        self.spike=True

    def update(self,pos):
        super().update(pos)
        self.hitbox.center=self.rect.center

class BG_Block(Block):

    def __init__(self,img,pos):
        super().__init__(img,pos)

class BG_near(Block):

    def __init__(self,img,pos):
        super().__init__(img,pos)
        self.paralex=0.75

    def update(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + self.paralex*pos[0], self.rect.topleft[1] + self.paralex*pos[1]]

class BG_mid(Block):

    def __init__(self,img,pos):
        super().__init__(img,pos)
        self.paralex=0.5

    def update(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + int(self.paralex*pos[0]), self.rect.topleft[1] + int(self.paralex*pos[1])]

class BG_far(Block):

    def __init__(self,img,pos):
        super().__init__(img,pos)
        self.paralex=0.03
        self.true_pos = self.rect.topleft

    def update(self,pos):
        self.true_pos= [self.true_pos[0] + self.paralex*pos[0], self.true_pos[1] + self.paralex*pos[1]]
        self.update_pos()

    def update_pos(self):
        self.rect.topleft = self.true_pos

class Invisible_block(Entity):

    def __init__(self,pos):
        super().__init__()
        self.rect=pygame.Rect(pos[0],pos[1],2,2)
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(0,0)

class Interactable(Entity):

    def __init__(self):
        super().__init__()
        self.interacted = False

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
        self.image_sheet = Read_files.Chest().get_sprites()
        self.image = self.image_sheet[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos[0],pos[1]-5)
        self.hitbox = self.rect.inflate(0,0)
        self.timer = 0
        self.ID = id
        self.loot = loot
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
        self.image_sheet = Read_files.Chest_Big().get_sprites()
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

class NPC(Entity):
    acceleration=[0.3,0.8]

    def __init__(self):
        super().__init__()
        self.action = {'stand':True,'run':False,'death':False,'hurt':False,'dash':False,'inv':False,'talk':False}
        self.nonpriority_action = ['run','stand']
        self.priority_action = ['death','hurt']
        self.health = 50
        self.state = 'stand'
        self.font=Read_files.Alphabet("Sprites/UI/Alphabet/Alphabet.png")#intitilise the alphabet class
        self.page_frame=0#if there are pages of text
        self.text_frame=-1#chosing which text to say: woudl ike to move this to NPC class instead
        self.letter_frame=1#to show one letter at the time: woudl ike to move this to NPC class instead
        self.conv_idx=[0,0]
        self.friction=[0.2,0]

    def blit_conversation(self,text,game_screen):#blitting of text from conversation
        self.text_surface.blit(self.portrait,(550,100))#the portait on to the text_surface
        game_screen.blit(self.text_surface,(200,200))#the text BG
        self.font.render(game_screen,text,(400,300),1)#call the self made aplhabet blit and blit the conversation
        self.font.render(game_screen,self.name,(750,400),1)#blit the name

    def new_page(self):
        if '&' in self.conversation.text[self.world_state][self.text_frame//1]:#& means there is a new page
            conversation=self.conversation.text[self.world_state][self.text_frame//1]
            indices = [i for i, x in enumerate(conversation) if x == "&"]#all indexes for &
            self.number_of_pages=len(indices)

            for i in range(self.page_frame,self.number_of_pages+1):
                start=min(indices[self.page_frame-1],self.page_frame*10000)
                if self.page_frame>=self.number_of_pages:
                    end=-1
                else:
                    end=indices[self.page_frame]
            return self.conversation.text[self.world_state][self.text_frame//1][start:end]
        else:
            self.number_of_pages=0
            return self.conversation.text[self.world_state][self.text_frame//1]

    def talking(self):
        self.action['talk']=True
        self.action['run']=False
        self.action['stand']=True
        self.velocity=[0,0]

    def talk(self,game_screen,player):
        if not self.action['talk']:#if first time
            self.page_frame=0
            self.letter_frame=1#reset the letter frame
            self.text_frame+=1

        if self.text_frame >= len(self.conversation.text[self.world_state]):
            self.text_frame=0#reset the conversation tree

        self.talking()#settign flags
        conv=self.new_page()#preparing the conversation if new page exits
        self.blit_conv_action(game_screen)#if it is a villiager with action

        if self.letter_frame//3!=len(conv):#if not everything has been said.
            text=conv[:self.letter_frame//3+1]
            self.letter_frame+=1
            self.blit_conversation(text,game_screen)
        else:#if everything was said, print the whole text
            self.page_frame=min(self.number_of_pages,self.page_frame)
            self.blit_conversation(conv,game_screen)

        self.input_quit(player)

    def input_quit(self,player):#to exits between option menues
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                #for action conversations
                if event.key==pygame.K_ESCAPE:#escape button
                    self.business = False
                    self.ammount=0
                    self.action['talk']=False
                    player.action['talk']=False
                if event.key == pygame.K_UP:#up
                    self.conv_idx[1]-=1*int(not self.business)
                    self.upinteger(player)
                if event.key == pygame.K_DOWN:#up
                    self.conv_idx[1]+=1*int(not self.business)
                    self.downinteger(player)
                if event.key == pygame.K_LEFT:#left
                    self.conv_idx[0]-=1*int(self.business)

                if event.key == pygame.K_RIGHT:#right
                    self.conv_idx[0]+=1*int(self.business)

                if event.key == pygame.K_RETURN:#enter the option
                    if self.business:
                        self.trade(player)
                    self.business = not self.business

                #exit/skip conversation
                if event.key == pygame.K_t:
                    if self.page_frame<self.number_of_pages:
                        self.page_frame+=1#next page
                    else:
                        self.action['talk']=False
                        self.ammount=0

                        player.action['talk']=False
                        self.page_frame=0#reset page
                    self.letter_frame=1#reset the letter frame

    def business(self):
        pass

    def upinteger(self,player):
        pass

    def downinteger(self,player):
        pass

    def blit_conv_action(self,game_screen):
        pass

    def trade():
        pass

    def stay_still(self):
        self.acceleration=[0,0]
        self.action['stand']=True

    def move_again(self):
        self.acceleration=[1,0.8]

class NPC_1(NPC):
    def __init__(self,pos):
        super().__init__()
        self.name = 'NPC_1'
        self.image = pygame.image.load("Sprites/Enteties/player/run/HeroKnight_run_0.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],20,48)
        self.rect.center = self.hitbox.center#match the positions of hitboxes
        self.portrait=pygame.image.load('Sprites/Enteties/NPC/'+self.name+ '/Woman1.png').convert_alpha()
        self.text_surface=pygame.image.load("Sprites/Enteties/NPC/conversation/Conv_BG.png").convert_alpha()
        self.sprites = Read_files.NPC(self.name)
        self.conversation=Read_files.Conversations('Sprites/Enteties/NPC/'+self.name+ '/conversation.txt')#a dictionary of conversations with "world state" as keys

    def AI(self):
        self.action['run']=True

        if abs(self.rect[0])>500 or abs(self.rect[1])>500:#if far away
            self.stay_still()
        else:
            self.move_again()

        if self.action['inv']:#collision with invisble block
            self.velocity[0] = -self.velocity[0]
            self.dir[0] = -self.dir[0]
            self.action['inv'] = False

class MrBanks(NPC):
    def __init__(self,pos):
        super().__init__()
        self.name = 'MrBanks'
        self.image = pygame.image.load("Sprites/Enteties/player/run/HeroKnight_run_0.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],20,48)
        self.rect.center = self.hitbox.center#match the positions of hitboxes
        self.portrait=pygame.image.load('Sprites/Enteties/NPC/'+self.name+ '/Woman1.png').convert_alpha()
        self.text_surface=pygame.image.load("Sprites/Enteties/NPC/conversation/Conv_BG.png").convert_alpha()
        self.sprites = Read_files.NPC(self.name)
        self.conversation=Read_files.Conversations('Sprites/Enteties/NPC/'+self.name+ '/conversation.txt')#a dictionary of conversations with "world state" as keys
        self.conv_action=['deposit','withdraw']
        self.conv_action_BG=pygame.image.load("Sprites/Enteties/NPC/conversation/Conv_action_BG.png").convert_alpha()
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

class Weapon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frame=0
        self.charging=[False]
        self.action=''

    def update(self,scroll,entity_ac_dir=[0,0],entity_hitbox=[0,0]):
        #remove the equipment if it has expiered
        self.lifetime-=1
        self.rect.topleft = [self.rect.topleft[0] + self.velocity[0]+scroll[0], self.rect.topleft[1] + self.velocity[1]+scroll[1]]
        self.hitbox.center = self.rect.center

        self.set_img()
        self.destroy()

    def set_img(self):
        self.image = self.sprites.get_image(self.action,self.frame//4,self.dir,self.state)
        self.frame += 1

        if self.frame == self.sprites.get_frame_number(self.action,self.dir,self.state)*4:
            self.reset_timer()
            if self.state=='pre':
                if self.charging[0]:
                    self.state='charge'
                else:
                    self.state = 'main'
            #elif self.state=='charge' and not self.charging[0]:
            #    self.state='main'
            elif self.state=='post':
                self.kill()

    def reset_timer(self):
        self.frame = 0

    def destroy(self):
        if self.lifetime<0:
            self.kill()

class Sword(Weapon):
    def __init__(self,entity_dir,entity_hitbox):
        super().__init__()
        self.lifetime=7#need to be changed depending on the animation of sword of player
        self.dmg=10
        self.velocity=[0,0]
        #self.state='pre'

        self.image = pygame.image.load("Sprites/Attack/Sword/main/swing1.png").convert_alpha()

        self.rect = self.image.get_rect(center=[entity_hitbox[0],entity_hitbox[1]])
        self.hitbox=pygame.Rect(entity_hitbox[0],entity_hitbox[1],entity_hitbox.height,entity_hitbox.width)
        self.rect.center=self.hitbox.center#match the positions of hitboxes

        self.dir=entity_dir.copy()
        self.spawn(entity_hitbox)#spawn hitbox based on entity position and direction

    def updates(self,entity_hitbox):
        self.lifetime-=1
        self.spawn(entity_hitbox)
        self.destroy()#check lifetime

    def spawn(self,entity_hitbox):
        if self.dir[1] > 0:#up
            self.hitbox.midbottom=entity_hitbox.midtop
        elif self.dir[1] < 0:#down
            self.hitbox.midtop=entity_hitbox.midbottom
        elif self.dir[0] > 0 and self.dir[1] == 0:#right
            self.hitbox.midleft=entity_hitbox.midright
        elif self.dir[0] < 0 and self.dir[1] == 0:#left
            self.hitbox.midright=entity_hitbox.midleft

    def update(self,scroll=0):
        pass

    def collision(self,entity=None,cosmetics=None,collision_ene=None):
        pass
        #entity.velocity[1]=entity.dir[1]*10#nail jump
        #collision_ene.velocity[0]=entity.dir[0]*10#enemy knock back

class Bow(Weapon):
    def __init__(self,entity_dir,entity_rect,charge):
        super().__init__()
        self.velocity=[0,0]
        self.lifetime=100
        self.dmg=10
        self.state='pre'
        self.action='small'
        self.dir=entity_dir.copy()#direction of the projectile
        self.sprites = Read_files.Sprites_Enteties('Sprites/Attack/Bow/',True)

        self.image = pygame.image.load("Sprites/Attack/Bow/pre/small/force_stone1.png").convert_alpha()
        self.rect = self.image.get_rect(center=[entity_rect.center[0]-5+self.dir[0]*20,entity_rect.center[1]])
        self.hitbox=pygame.Rect(entity_rect.center[0]-5+self.dir[0]*20,entity_rect.center[1],10,10)
        self.rect.center=self.hitbox.center#match the positions of hitboxes

        self.charging=charge#pointed to player charge state
        self.charge_velocity=self.dir[0]

    def update(self,scroll,entity_ac_dir=[0,0],entity_hitbox=[0,0]):
        #remove the equipment if it has expiered
        self.rect.topleft = [self.rect.topleft[0] + self.velocity[0]+scroll[0], self.rect.topleft[1] + self.velocity[1]+scroll[1]]
        self.hitbox.center = self.rect.center

        self.set_img()#set the animation
        self.speed()#set the speed
        self.destroy()#if lifetime expires

    def speed(self):
        if self.state=='charge':#charging
            self.charge_velocity=self.charge_velocity+0.25*self.dir[0]
            self.charge_velocity=self.dir[0]*min(10,self.dir[0]*self.charge_velocity)#set max velocity

            if abs(self.charge_velocity)>=10:#increase the ball size when max velocity is reached
                self.action='medium'

            if not self.charging[0]:#when finish chaging
                self.frame=0
                self.state='main'
                self.velocity[0]=self.charge_velocity#set the velocity

        elif self.state=='main':#main pahse
            self.lifetime-=1#affect only the lifetime in main state
            self.velocity[1]+=0.1#graivity


    def collision(self,entity=None,cosmetics=None,collision_ene=None):
        self.velocity=[0,0]
        self.dmg=0
        self.state='post'

    def rotate(self):
        angle=self.dir[0]*max(-self.dir[0]*self.velocity[0]*self.velocity[1],-60)

        self.image=pygame.transform.rotate(self.original_image,angle)#fig,angle,scale
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.hitbox=pygame.Rect(x,y,10,10)

        self.rect.center = (x, y)  # Put the new rect's center at old center.

class Force(Weapon):
    def __init__(self,entity_dir,entity_hitbox):
        super().__init__()

        if entity_dir[1]!=0:#shppting up or down
            self.velocity=[0,-entity_dir[1]*10]
        else:#horizontal
            self.velocity=[entity_dir[0]*10,0]

        self.lifetime=20
        self.dmg=0
        self.dir=entity_dir.copy()

        self.sprites = Read_files.Sprites_Enteties('Sprites/Attack/Force/')
        self.state='pre'

        self.image = pygame.image.load("Sprites/Attack/Force/pre/fly3.png").convert_alpha()
        if self.velocity[0]<0:#if shoting left
            self.image=pygame.transform.flip(self.image,True,False)

        self.rect = self.image.get_rect(center=[entity_hitbox[0],entity_hitbox[1]])
        self.hitbox=pygame.Rect(entity_hitbox[0],entity_hitbox[1],30,30)
        self.rect.center=self.hitbox.center#match the positions of hitboxes

    def collision(self,entity=None,cosmetics=None,collision_ene=None):#if hit something
        #push_strength=[500/(self.rect[0]-entity.rect[0]),500/(self.rect[1]-entity.rect[1])]
        self.state='post'
        self.frame=0
        self.velocity=[0,0]

        if collision_ene:#if collision with enemy
            cosmetics.add(Spirits([collision_ene.rect[0],collision_ene.rect[1]]))#spawn cosmetic spirits
            #if self.dir[1]!=0:
            #    entity.velocity[1]=self.dir[1]*abs(push_strength[1])#force jump
            if self.dir[1]==0:#push enemy back
                collision_ene.velocity[0]=self.dir[0]*10#abs(push_strength[0])
                collision_ene.velocity[1]=-6
            return
        #if self.dir[1]!=0:#if patform down
        #    entity.velocity[1]=self.dir[1]*abs(push_strength[1])*0.75#force jump

class Loot(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        choice=[-20,-18,-16,-14,-12,-10,-8,-6,-4,-2,2,4,6,8,10,12,14,16,18,20]#just not 0
        self.pos=[random.choice(choice),random.choice(choice)]
        self.lifetime=300
        self.movement=[0,0]#for platfform collisions
        dir=self.pos[0]/abs(self.pos[0])#horizontal direction
        self.velocity=[dir*random.randint(0, 3),-11]
        self.collision_types = {'top':False,'bottom':False,'right':False,'left':False}
        self.collision_spikes = {'top':False,'bottom':False,'right':False,'left':False}

    def update_hitbox(self):
        self.hitbox.center = self.rect.center

    def update_rect(self):
        self.rect.center = self.hitbox.center

    def update(self,scroll):
        #remove the equipment if it has expiered
        self.speed()

        self.lifetime-=1
        self.rect.topleft = [self.rect.topleft[0] + self.velocity[0]+scroll[0], self.rect.topleft[1] + self.velocity[1]+scroll[1]]
        self.hitbox.center = self.rect.center

        if self.lifetime<0:#remove after a while
            self.kill()

    def speed(self):
        self.velocity[1]+=0.9#gravity

        self.velocity[1]=min(self.velocity[1],7)#set a y max speed
        self.movement[1]=self.velocity[1]#set the vertical velocity

class Coin(Loot):
    def __init__(self,entity_hitbox):
        super().__init__()

        self.image = pygame.image.load("Sprites/Enteties/Items/coin.png").convert_alpha()
        self.rect = self.image.get_rect(center=[entity_hitbox[0]+self.pos[0],entity_hitbox[1]+self.pos[1]])
        self.hitbox=pygame.Rect(entity_hitbox[0]+self.pos[0],entity_hitbox[1]+self.pos[1],10,10)
        self.rect.center=self.hitbox.center#match the positions of hitboxes

class Arrow(Loot):
    def __init__(self,entity_hitbox):
        super().__init__()

        self.image = pygame.image.load("Sprites/Enteties/Items/arrow.png").convert_alpha()
        self.rect = self.image.get_rect(center=[entity_hitbox[0]+self.pos[0],entity_hitbox[1]+self.pos[1]])
        self.hitbox=pygame.Rect(entity_hitbox[0]+self.pos[0],entity_hitbox[1]+self.pos[1],10,10)
        self.rect.center=self.hitbox.center#match the positions of hitboxes

class Spirits(pygame.sprite.Sprite):

    def __init__(self,pos):
        super().__init__()
        self.image = pygame.image.load("Sprites/animations/Spirits/Spirits1.png").convert_alpha()
        self.rect = self.image.get_rect(center=[pos[0],pos[1]])
        self.hitbox=pygame.Rect(pos[0],pos[1],5,5)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.frame=0
        self.lifetime=10

    def update(self,pos):
        self.lifetime -= 1

        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.center=self.rect.center

        if self.lifetime<0:
            self.kill()

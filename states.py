import pygame, sys, random
import Read_files
import Entities, entities_UI
import cutscene
import constants as C
import state_inventory
import animation

class Game_State():
    def __init__(self,game):
        self.game = game

    def update(self):
        pass

    def render(self,display):
        pass

    def handle_events(self,event):
        pass

    def enter_state(self):
        self.game.state_stack.append(self)

    def exit_state(self):
        self.game.state_stack.pop()

class Title_Menu(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.game_objects = game.game_objects
        self.arrow = entities_UI.Menu_Arrow()
        self.title = self.game.game_objects.font.render(text = 'HAPPY VILLE') #temporary
        self.sprites = Read_files.load_sprites('Sprites/UI/load_screen/new_game')
        self.image = self.sprites[0]
        self.animation = animation.Simple_animation(self)

        #create buttons
        self.buttons = ['NEW GAME','LOAD GAME','OPTIONS','QUIT']
        self.current_button = 0
        self.initiate_buttons()
        self.define_BG()

    def define_BG(self):
        size = (90,100)
        self.bg = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(self.bg,[20,20,20,200],(0,0,size[0],size[1]),border_radius=10)

    def reset_timer(self):
        pass

    def update(self):
        #update menu arrow position
        self.animation.update()
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update((ref_pos[0] - 10, ref_pos[1]))

    def render(self):
        self.game.screen.fill((255,255,255))
        self.game.screen.blit(self.image, (0,0))

        #blit title
        self.game.screen.blit(self.title, (self.game.WINDOW_SIZE[0]/2 - self.title.get_width()/2,50))
        self.game.screen.blit(self.bg, (70,180))

        #blit buttons
        for b in self.buttons:
            self.game.screen.blit(self.button_surfaces[b], self.button_rects[b].topleft)

        #blit arrow
        self.arrow.draw(self.game.screen)

    def handle_events(self, event):
        #print(event)
        if event[0]:
            if event[-1] == 'up':
                self.current_button -= 1
                if self.current_button < 0:
                    self.current_button = len(self.buttons) - 1
            elif event[-1] == 'down':
                self.current_button += 1
                if self.current_button >= len(self.buttons):
                    self.current_button = 0
            elif event[-1] in ('return', 'a'):
                self.change_state()
            elif event[-1] == 'start':
                pygame.quit()
                sys.exit()

    def initiate_buttons(self):
        y_pos = 200
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            text = (self.game.game_objects.font.render(text = b))
            text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
            self.button_surfaces[b] = text
            self.button_rects[b] = pygame.Rect((100,y_pos),self.button_surfaces[b].get_size())
            y_pos += 20


    def change_state(self):
        if self.current_button == 0:#new game
            new_state = Gameplay(self.game)
            new_state.enter_state()

            #when starting a new game, should be a cutscene
            #new_state = Cutscenes(self.game,'New_game')
            #new_state.enter_state()

            #load new game level
            self.game.game_objects.load_map('village_2','1')

        elif self.current_button == 1:
            new_state = Load_Menu(self.game)
            new_state.enter_state()

        elif self.current_button == 2:
            new_state = Start_Option_Menu(self.game)
            new_state.enter_state()

        elif self.current_button == 3:
            pygame.quit()
            sys.exit()

class Load_Menu(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.game_objects = game.game_objects
        self.arrow = entities_UI.Menu_Arrow()
        self.title = self.game.game_objects.font.render(text = 'LOAD GAME') #temporary
        self.sprites = Read_files.load_sprites('Sprites/UI/load_screen/new_game')
        self.image = self.sprites[0]
        self.animation = animation.Simple_animation(self)

        #create buttons
        self.buttons = ['SLOT 1','SLOT 2','SLOT 3','SLOT 4']
        self.current_button = 0
        self.initiate_buttons()
        self.define_BG()

    def define_BG(self):
        size = (90,100)
        self.bg = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(self.bg,[20,20,20,200],(0,0,size[0],size[1]),border_radius=10)

    def reset_timer(self):
        pass

    def update(self):
        #update menu arrow position
        self.animation.update()
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update((ref_pos[0] - 10, ref_pos[1]))

    def render(self):
        #fill game.screen
        self.game.screen.fill((255,255,255))
        self.game.screen.blit(self.image, (0,0))

        #blit title
        self.game.screen.blit(self.title, (self.game.WINDOW_SIZE[0]/2 - self.title.get_width()/2,50))
        self.game.screen.blit(self.bg, (70,180))

        #blit buttons
        for b in self.buttons:
            self.game.screen.blit(self.button_surfaces[b], self.button_rects[b].topleft)

        #blit arrow
        self.arrow.draw(self.game.screen)

    def handle_events(self, event):
        if event[0]:
            if event[-1] == 'up':
                self.current_button -= 1
                if self.current_button < 0:
                    self.current_button = len(self.buttons) - 1
            elif event[-1] == 'down':
                self.current_button += 1
                if self.current_button >= len(self.buttons):
                    self.current_button = 0
            elif event[-1] == 'start':
                self.exit_state()
            elif event[-1] in ('return', 'a'):
                self.game.game_objects.load_game()#load saved game data

                new_state = Gameplay(self.game)
                new_state.enter_state()
                map=self.game.game_objects.player.spawn_point['map']
                point=self.game.game_objects.player.spawn_point['point']
                self.game.game_objects.load_map(map,point)

    def initiate_buttons(self):
        y_pos = 200
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            text = (self.game.game_objects.font.render(text = b))
            text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
            self.button_surfaces[b] = text
            self.button_rects[b] = pygame.Rect((100,y_pos),self.button_surfaces[b].get_size())
            y_pos += 20

class Start_Option_Menu(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.game_objects = game.game_objects
        self.arrow = entities_UI.Menu_Arrow()
        self.title = self.game.game_objects.font.render(text = 'OPTIONS') #temporary
        self.sprites = Read_files.load_sprites('Sprites/UI/load_screen/new_game')
        self.image = self.sprites[0]
        self.animation = animation.Simple_animation(self)

        #create buttons
        self.buttons = ['Option 1','Option 2','Option 3','Option 4','Option 5']
        self.current_button = 0
        self.initiate_buttons()
        self.define_BG()

    def reset_timer(self):
        pass

    def define_BG(self):
        size = (90,130)
        self.bg = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(self.bg,[20,20,20,200],(0,0,size[0],size[1]),border_radius=10)

    def update(self):
        #update menu arrow position
        self.animation.update()
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update((ref_pos[0] - 10, ref_pos[1]))

    def render(self):
        #fill game.screen
        self.game.screen.fill((255,255,255))
        self.game.screen.blit(self.image, (0,0))

        #blit title
        self.game.screen.blit(self.title, (self.game.WINDOW_SIZE[0]/2 - self.title.get_width()/2,50))
        self.game.screen.blit(self.bg, (70,180))

        #blit buttons
        for b in self.buttons:
            self.game.screen.blit(self.button_surfaces[b], self.button_rects[b].topleft)

        #blit arrow
        self.arrow.draw(self.game.screen)

    def handle_events(self, event):
        if event[0]:
            if event[-1] == 'up':
                self.current_button -= 1
                if self.current_button < 0:
                    self.current_button = len(self.buttons) - 1
            elif event[-1] == 'down':
                self.current_button += 1
                if self.current_button >= len(self.buttons):
                    self.current_button = 0
            elif event[-1] == 'start':
                self.exit_state()

    def initiate_buttons(self):
        y_pos = 200
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            text = (self.game.game_objects.font.render(text = b))
            text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
            self.button_surfaces[b] = text
            self.button_rects[b] = pygame.Rect((100,y_pos),self.button_surfaces[b].get_size())
            y_pos += 20

class Option_Menu(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.arrow = entities_UI.Menu_Arrow()
        self.title = self.game.game_objects.font.render(text = 'OPTIONS') #temporary

        #create buttons
        self.buttons = ['Option 1','Option 2','Option 3','Option 4','Option 5']
        if self.game.DEBUG_MODE:
            self.buttons = ['Render FPS', 'Render Hitboxes']
        self.current_button = 0
        self.initiate_buttons()

    def update(self):
        #update menu arrow position
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update((ref_pos[0] - 10, ref_pos[1]))

    def render(self):
        #fill game.screen
        self.game.screen.fill((255,255,255))

        #blit title
        self.game.screen.blit(self.title, (self.game.WINDOW_SIZE[0]/2 - self.title.get_width()/2,50))

        #blit buttons
        for b in self.buttons:
            self.game.screen.blit(self.button_surfaces[b], self.button_rects[b].topleft)

        #blit arrow
        self.arrow.draw(self.game.screen)

    def handle_events(self, event):
        if event[0]:
            if event[-1] == 'up':
                self.current_button -= 1
                if self.current_button < 0:
                    self.current_button = len(self.buttons) - 1
            elif event[-1] == 'down':
                self.current_button += 1
                if self.current_button >= len(self.buttons):
                    self.current_button = 0
            elif event[-1] == 'start':
                self.exit_state()
            elif event[-1] in ('return', 'a'):
                self.update_options()

    def initiate_buttons(self):
        y_pos = 90
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            self.button_surfaces[b] = (self.game.game_objects.font.render(text = b))
            self.button_rects[b] = pygame.Rect((self.game.WINDOW_SIZE[0]/2 - self.button_surfaces[b].get_width()/2 ,y_pos),self.button_surfaces[b].get_size())
            y_pos += 20

    def update_options(self):
        if self.game.DEBUG_MODE:
            if self.current_button == 0:
                self.game.RENDER_FPS_FLAG = not self.game.RENDER_FPS_FLAG
            elif self.current_button == 1:
                self.game.RENDER_HITBOX_FLAG = not self.game.RENDER_HITBOX_FLAG

class Gameplay(Game_State):
    def __init__(self,game):
        super().__init__(game)

    def update(self):
        self.game.game_objects.update()
        self.game.game_objects.collide_all()
        self.game.game_objects.UI['gameplay'].update()

    def render(self):
        self.game.screen.fill((17,22,22))
        self.game.game_objects.draw()
        self.game.game_objects.UI['gameplay'].render()
        if self.game.RENDER_FPS_FLAG:
            self.blit_fps()

    def blit_fps(self):
        fps_string = str(int(self.game.clock.get_fps()))
        self.game.screen.blit(self.game.game_objects.font.render((30,12),'fps ' + fps_string),(self.game.WINDOW_SIZE[0]-40,20))

    def handle_events(self, input):
        self.game.game_objects.player.currentstate.handle_movement(input)#move around
        if input[0]:#press
            if input[-1]=='start':#escape button
                new_state = Pause_Menu(self.game)
                new_state.enter_state()

            elif input[-1]=='rb':
                new_state = Ability_menu(self.game)
                new_state.enter_state()

            elif input[-1] == 'y':
                self.game.game_objects.collisions.check_interaction_collision()

            elif input[-1] == 'select':
                new_state = Inventory_menu(self.game)
                new_state.enter_state()

            elif input[-1] == 'down':
                self.game.game_objects.collisions.pass_through()

            else:
                self.game.game_objects.player.currentstate.handle_press_input(input)
                self.game.game_objects.player.abilities.handle_input(input)#to change movement ability
                #self.game.game_objects.player.omamoris.handle_input(input)
        elif input[1]:#release
            self.game.game_objects.player.currentstate.handle_release_input(input)

    def handle_input(self,input):
        if input == 'dmg':
            new_game_state = Pause_gameplay(self.game,duration=11)
            new_game_state.enter_state()
        elif input == 'death':#normal death
            self.game.game_objects.player.death()

class Pause_Menu(Gameplay):#when pressing ESC duing gameplay
    def __init__(self,game):
        super().__init__(game)
        self.arrow = entities_UI.Menu_Arrow()
        self.title = self.game.game_objects.font.render(text = 'Pause menu') #temporary
        self.title.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
        #create buttons
        self.buttons = ['RESUME','OPTIONS','QUIT TO MAIN MENU','QUIT GAME']
        self.current_button = 0
        self.initiate_buttons()
        self.define_BG()

    def define_BG(self):
        size = (100,120)
        self.bg = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(self.bg,[20,20,20,200],(0,0,size[0],size[1]),border_radius=10)

    def update(self):
        #update menu arrow position
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update((ref_pos[0] - 10, ref_pos[1]))

    def render(self):
        #fill game.screen
        super().render()
        self.game.screen.fill((50,50,50),special_flags=pygame.BLEND_RGB_ADD)
        self.game.screen.blit(self.bg, (self.game.WINDOW_SIZE[0]/2 - self.bg.get_width()/2,100))

        #blit title
        self.game.screen.blit(self.title, (self.game.WINDOW_SIZE[0]/2 - self.title.get_width()/2,110))

        #blit buttons
        for b in self.buttons:
            self.game.screen.blit(self.button_surfaces[b], self.button_rects[b].topleft)

        #blit arrow
        self.arrow.draw(self.game.screen)

    def handle_events(self, event):
        if event[0]:
            if event[-1] == 'up':
                self.current_button -= 1
                if self.current_button < 0:
                    self.current_button = len(self.buttons) - 1
            elif event[-1] == 'down':
                self.current_button += 1
                if self.current_button >= len(self.buttons):
                    self.current_button = 0
            elif event[-1] in ('return', 'a'):
                self.change_state()
            elif event[-1] == 'start':
                self.exit_state()

    def initiate_buttons(self):
        y_pos = 140
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            text = (self.game.game_objects.font.render(text = b))
            text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
            self.button_surfaces[b] = text
            self.button_rects[b] = pygame.Rect((self.game.WINDOW_SIZE[0]/2 - self.button_surfaces[b].get_width()/2 ,y_pos),self.button_surfaces[b].get_size())
            y_pos += 20

    def change_state(self):
        if self.current_button == 0:
            self.exit_state()

        elif self.current_button == 1:
            new_state = Option_Menu(self.game)
            new_state.enter_state()

        elif self.current_button == 2:
            self.game.state_stack = [self.game.state_stack[0]]

        elif self.current_button == 3:
            pygame.quit()
            sys.exit()

class Pause_gameplay(Gameplay):#a pause screen with shake. = when aila takes dmg
    def __init__(self,game, duration=10, amplitude = 20):
        super().__init__(game)
        self.duration = duration
        self.amp = amplitude
        self.game.state_stack[-1].render()#make sure that everything is plotted before making a screen copy
        self.temp_surface = self.game.screen.copy()
        #self.shader = shader_entities.Shader_entities(self)

    def update(self):
        self.game.game_objects.cosmetics.update([0,0])
        self.duration -= self.game.dt
        self.amp = int(0.8*self.amp)
        if self.duration < 0:
            self.exit_state()

    def render(self):
        #super().render()
        self.game.game_objects.cosmetics.draw(self.game.screen)
        self.game.screen.blit(self.temp_surface, (random.randint(-self.amp,self.amp),random.randint(-self.amp,self.amp)))

class Cultist_encounter_gameplay(Gameplay):#if player dies, the plater is not respawned but transffered to cultist hideout
    def __init__(self,game):
        super().__init__(game)

    def handle_input(self,input):
        if input == 'dmg':
            new_game_state = Pause_gameplay(self.game,duration=11)
            new_game_state.enter_state()
        elif input == 'exit':
            self.exit_state()
        elif input == 'death':
            self.game.game_objects.player.reset_movement()
            self.game.game_objects.load_map('cultist_hideout_1','2')

class Slow_motion_gameplay(Gameplay):
    def __init__(self, game):
        super().__init__(game)
        self.slow_rate = 0.5#determines the rate of slow motion, between 0 and 1
        self.game.game_objects.player.abilities.spirit_abilities['Slow_motion'].init(self.slow_rate)
        self.duration = self.game.game_objects.player.abilities.spirit_abilities['Slow_motion'].duration

        self.bar = self.game.game_objects.player.abilities.spirit_abilities['Slow_motion'].sprites.sprite_dict['bar'][0].copy()
        self.meter = self.game.game_objects.player.abilities.spirit_abilities['Slow_motion'].sprites.sprite_dict['meter'][0].copy()
        self.width = self.meter.get_width()

        self.pos = [self.game.WINDOW_SIZE[0]*0.5 - self.width*0.5,3]
        self.rate =self.meter.get_width()/self.duration

    def update(self):
        self.game.dt *= self.slow_rate#slow motion
        super().update()
        self.duration -= self.game.dt
        self.exit()

    def render(self):
        super().render()
        self.game.screen.fill((20,20,20), special_flags = pygame.BLEND_RGB_ADD)
        self.width -= self.game.dt*self.rate
        self.width = max(self.width,0)
        self.game.screen.blit(pygame.transform.scale(self.meter,[self.width,self.meter.get_height()]),self.pos)
        self.game.screen.blit(self.bar, self.pos)

    def exit(self):
        if self.duration < 0:
            self.game.game_objects.player.slow_motion = 1
            self.exit_state()

class Ability_menu(Gameplay):#when pressing tab
    def __init__(self, game):
        super().__init__(game)
        self.abilities=list(self.game.game_objects.player.abilities.spirit_abilities.keys())
        self.index = self.abilities.index(self.game.game_objects.player.abilities.equip)

        hud2=pygame.image.load("Sprites/Attack/HUD/abilityHUD2.png").convert_alpha()
        hud3=pygame.image.load("Sprites/Attack/HUD/abilityHUD3.png").convert_alpha()
        hud4=pygame.image.load("Sprites/Attack/HUD/abilityHUD4.png").convert_alpha()
        hud5=pygame.image.load("Sprites/Attack/HUD/abilityHUD5.png").convert_alpha()
        hud6=pygame.image.load("Sprites/Attack/HUD/abilityHUD6.png").convert_alpha()

        self.hud=[hud2,hud3,hud4,hud5,hud6]
        self.coordinates=[(40,0),(60,50),(30,60),(0,40),(20,0),(0,0)]

    def update(self):
        self.game.dt *= 0.5#slow motion
        super().update()

    def render(self):
        super().render()
        self.game.screen.fill((20,20,20),special_flags=pygame.BLEND_RGB_ADD)

        hud=self.hud[self.index]
        for index,ability in enumerate(self.abilities):
            hud.blit(self.game.game_objects.player.abilities.spirit_abilities[ability].sprites.sprite_dict['active_1'][0],self.coordinates[index])

        self.game.screen.blit(hud,(250,100))

    def handle_events(self, input):
        if input[0]:#press
            if input[-1] == 'right':
                self.index+=1
                if self.index>len(self.abilities)-1:
                    self.index=0
            elif input[-1] =='left':
                self.index-=1
                if self.index<0:
                    self.index=len(self.abilities)-1
        elif input [1]:#release
            if input[-1]=='rb':
                self.game.game_objects.player.abilities.equip=self.abilities[self.index]
                self.exit_state()

class Inventory_menu(Gameplay):
    def __init__(self, game):
        super().__init__(game)
        self.iventory_UI = self.game.game_objects.UI['inventory']
        self.letter_frame = 0#for description
        self.state = state_inventory.Items(self)
        self.item_index = [0,0]#row, col

        self.define_blit_positions()
        self.define_pointer()

    def define_blit_positions(self):#set positions
        items = self.iventory_UI.items.copy()#a list if empty items
        key_items = self.iventory_UI.key_items#a dict of empty key items
        index = 0
        for key in self.game.game_objects.player.inventory.keys():#crease the object in inventory and sepeerate between useable items and key items
            item = getattr(sys.modules[Entities.__name__], key)([0,0],self.game.game_objects)#make the object based on the string
            if hasattr(item, 'use_item'):
                item.rect.topleft = items[index].rect.topleft
                item.number = self.game.game_objects.player.inventory[key]#number of items euirepped
                items[index] = item
                index += 1
            else:
                item.rect.topleft = key_items[key].rect.topleft
                item.number = self.game.game_objects.player.inventory[key]#number of items euirepped
                key_items[key] = item

        stones = self.iventory_UI.stones#a dict of emppty stones
        for key in self.game.game_objects.player.sword.stones.keys():
            self.game.game_objects.player.sword.stones[key].rect.topleft = stones[key].rect.topleft
            stones[key] = self.game.game_objects.player.sword.stones[key]

        self.items = {'sword':list(stones.values()),'key_items':list(key_items.values()),'items':items}#organised items: used to select the item

    def define_pointer(self,size = [16,16]):#called everytime we move from one area to another
        self.pointer = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(self.pointer,[200,50,50,255],(0,0,size[0],size[1]),width=1,border_radius=5)

    def update(self):
        super().update()
        self.letter_frame += self.game.dt

    def render(self):
        super().render()
        self.blit_inventory_BG()
        self.blit_inventory()
        self.blit_sword()
        self.blit_pointer()
        self.blit_description()

    def blit_inventory_BG(self):
        self.iventory_UI.BG.set_alpha(230)
        self.game.screen.blit(self.iventory_UI.BG,(0,0))

    def blit_inventory(self):
        for index, item in enumerate(self.items['items']):#items we can use
            item.animation.update()
            self.game.screen.blit(pygame.transform.scale(item.image,(16,16)),item.rect.topleft)
            number = self.game.game_objects.font.render(text = str(item.number))
            number.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
            self.game.screen.blit(number,item.rect.center)

        for index, item in enumerate(self.items['key_items']):
            item.animation.update()
            self.game.screen.blit(pygame.transform.scale(item.image,(16,16)),item.rect.topleft)
            number = self.game.game_objects.font.render(text = str(item.number))
            number.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
            self.game.screen.blit(number,item.rect.center)

    def blit_sword(self):
        self.iventory_UI.sword.animation.update()
        self.game.screen.blit(self.iventory_UI.sword.image,self.iventory_UI.sword.rect.topleft)

        for stone in self.items['sword']:
            stone.animation.update()
            self.game.screen.blit(stone.image,stone.rect.topleft)

    def blit_pointer(self):
        self.game.screen.blit(self.pointer,self.items[self.state.state_name][self.item_index[0]].rect.topleft)#pointer

    def blit_description(self):
        self.conv = self.items[self.state.state_name][self.item_index[0]].description
        text = self.game.game_objects.font.render((152,80), self.conv, int(self.letter_frame//2))
        text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
        self.game.screen.blit(text,(380,120))

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()
            elif input[-1] == 'rb':#nezt page
                self.exit_state()
                new_state = Omamori_menu(self.game)
                new_state.enter_state()
            elif input[-1] == 'lb':#previouse page
                self.exit_state()
                new_state = Map_menu(self.game)
                new_state.enter_state()
            elif input[-1]=='a' or input[-1]=='return':
                self.use_item()
            self.state.handle_input(input)
            self.letter_frame = 0

    def use_item(self):
        if not hasattr(self.items[self.state.state_name][self.item_index[0]], 'use_item'): return#if it is a item
        if self.items[self.state.state_name][self.item_index[0]].number <= 0: return#if we have more than 0 item
        self.items[self.state.state_name][self.item_index[0]].use_item()
        self.exit_state()

class Omamori_menu(Gameplay):
    def __init__(self, game):
        super().__init__(game)
        self.omamori_UI = self.game.game_objects.UI['omamori']

        self.letter_frame = 0#for description
        self.define_blit_positions()
        self.define_pointer()
        self.omamori_index = 0

    def define_blit_positions(self):
        for index, key in enumerate(self.game.game_objects.player.omamoris.equipped):#the equiped ones
            pos = self.omamori_UI.equipped[index].rect.center
            self.game.game_objects.player.omamoris.equipped[key].set_pos(pos)

        omamori_dict = self.omamori_UI.inventory#copy all empty ones and then overwrite with the rellavant ones in inventory
        for index, key in enumerate(self.game.game_objects.player.omamoris.inventory):#the ones in inventory
            pos = self.omamori_UI.inventory[key].rect.center
            self.game.game_objects.player.omamoris.inventory[key].set_pos(pos)
            omamori_dict[key] = self.game.game_objects.player.omamoris.inventory[key]
        self.omamori_list = list(omamori_dict.values())

    def define_pointer(self,size = [16,16]):#called everytime we move from one area to another
        size = self.omamori_list[0].rect.size
        self.pointer = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(self.pointer,[200,50,50,255],(size[0]*0.5-8,size[1]*0.5+8,16,16),width=1,border_radius=5)

    def update(self):
        super().update()
        self.letter_frame += self.game.dt

    def render(self):
        super().render()
        self.blit_omamori_BG()
        self.blit_omamori_menu()
        self.blit_pointer()
        self.blit_description()

    def blit_omamori_BG(self):
        self.omamori_UI.BG.set_alpha(230)
        self.game.screen.blit(self.omamori_UI.BG,(0,0))

    def blit_omamori_menu(self):
        for omamori in self.game.game_objects.player.omamoris.equipped.values():#equipped ones
            omamori.animation.update()
            self.game.screen.blit(omamori.image,omamori.rect.topleft)

        for omamori in self.omamori_list:
            omamori.animation.update()
            self.game.screen.blit(omamori.image,omamori.rect.topleft)

    def blit_description(self):
        self.conv = self.omamori_list[self.omamori_index].description
        text = self.game.game_objects.font.render((152,80), self.conv, int(self.letter_frame//2))
        text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
        self.game.screen.blit(text,(380,120))

    def blit_pointer(self):
        pos = self.omamori_list[self.omamori_index].rect.topleft
        self.game.screen.blit(self.pointer,pos)#pointer

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()
            elif input[-1] == 'rb':#nezt page
                if self.game.game_objects.world_state.statistics['kill']:#if we have killed something
                    self.exit_state()
                    new_state = Journal_menu(self.game)
                    new_state.enter_state()
            elif input[-1] == 'lb':#previouse page
                self.exit_state()
                new_state = Inventory_menu(self.game)
                new_state.enter_state()
            elif input[-1]=='a' or input[-1]=='return':
                self.choose_omamori()

            elif input[-1] =='right':
                self.letter_frame = 0
                self.omamori_index += 1
                self.omamori_index = min(self.omamori_index,len(self.omamori_UI.inventory)-1)

            elif input[-1] =='left':
                self.letter_frame = 0
                self.omamori_index -= 1
                self.omamori_index = max(0,self.omamori_index)

            elif input[-1] =='down':
                self.letter_frame = 0
                self.omamori_index += 5
                self.omamori_index = min(self.omamori_index,len(self.omamori_UI.inventory)-1)

            elif input[-1] =='up':
                self.letter_frame = 0
                self.omamori_index -= 5
                self.omamori_index = max(0,self.omamori_index)

    def choose_omamori(self):
        name = type(self.omamori_list[self.omamori_index]).__name__#name of omamori
        if name == 'Omamori': return#if it is an empyu omamori. return
        self.game.game_objects.player.omamoris.equip_omamori(name)

        for index, omamori in enumerate(self.game.game_objects.player.omamoris.equipped.values()):#update the positions of the equiped ones
            pos = self.omamori_UI.equipped[index].rect.center
            omamori.set_pos(pos)

class Journal_menu(Gameplay):
    def __init__(self, game):
        super().__init__(game)
        self.journal_UI =  self.game.game_objects.UI['journal']
        self.letter_frame = 0
        self.journal_index = [0,0]
        self.enemies = []
        self.enemy_index = self.journal_index.copy()
        self.number = 8 #number of enemies per page

        for enemy in self.game.game_objects.world_state.statistics['kill']:
            self.enemies.append(getattr(sys.modules[Entities.__name__], enemy.capitalize())([0,0],self.game.game_objects))#make the object based on the string

        self.select_enemies()
        self.define_pointer()

    def select_enemies(self):
        self.selected_enemies = self.enemies[self.enemy_index[0]:self.enemy_index[0]+self.number:1]

    def define_pointer(self):#called everytime we move from one area to another
        size = [48,16]
        self.pointer = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(self.pointer,[200,50,50,255],(0,0,size[0],size[1]),width=1,border_radius=5)

    def update(self):
        super().update()
        self.letter_frame += self.game.dt

    def render(self):
        super().render()
        self.blit_journal_BG()
        self.blit_names()
        self.blit_pointer()
        self.blit_enemy()
        self.blit_description()

    def blit_journal_BG(self):
        self.journal_UI.BG.set_alpha(230)
        self.game.screen.blit(self.journal_UI.BG,(0,0))

    def blit_names(self):
        for index, enemy in enumerate(self.selected_enemies):
            name = enemy.__class__.__name__
            text = self.game.game_objects.font.render((152,80), name, 100)
            text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
            self.game.screen.blit(text,self.journal_UI.name_pos[index])

    def blit_pointer(self):
        pos = [self.journal_UI.name_pos[self.journal_index[0]][0],self.journal_UI.name_pos[self.journal_index[0]][1]-5]#add a offset
        self.game.screen.blit(self.pointer,pos)#pointer

    def blit_enemy(self):
        enemy = self.selected_enemies[self.journal_index[0]]
        enemy.rect.midbottom = self.journal_UI.image_pos#allign based on bottom
        enemy.animation.update()
        self.game.screen.blit(enemy.image,[enemy.rect.center[0]-enemy.rect.width*0.5,enemy.rect.center[1]-enemy.rect.height*0.5])#it blits the top left courner so need to correct based on the rectanle size

    def blit_description(self):
        self.conv = self.selected_enemies[self.journal_index[0]].description
        text = self.game.game_objects.font.render((152,80), self.conv, int(self.letter_frame//2))
        text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
        self.game.screen.blit(text,(380,120))

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()
            elif input[-1] == 'rb':#nezt page
                pass
            elif input[-1] == 'lb':#previouse page
                self.exit_state()
                new_state = Omamori_menu(self.game)
                new_state.enter_state()

            elif input[-1] =='down':
                self.letter_frame = 0
                self.journal_index[0] += 1
                if self.journal_index[0] == self.number:
                    self.enemy_index[0] += 1
                    self.enemy_index[0] = min(self.enemy_index[0],len(self.enemies)-self.number)
                    self.select_enemies()
                self.journal_index[0] = min(self.journal_index[0],len(self.selected_enemies)-1)

            elif input[-1] =='up':
                self.letter_frame = 0
                self.journal_index[0] -= 1
                if self.journal_index[0] == -1:
                    self.enemy_index[0] -= 1
                    self.enemy_index[0] = max(0,self.enemy_index[0])
                    self.select_enemies()
                self.journal_index[0] = max(0,self.journal_index[0])

class Map_menu(Gameplay):
    def __init__(self, game):
        super().__init__(game)
        self.map_UI = self.game.game_objects.UI['map']

        self.scroll = [0,0]
        self.index = 0
        self.pos = [-0.5*(self.map_UI.BG.get_width() - self.game.WINDOW_SIZE[0]),-0.5*(self.map_UI.BG.get_height() - self.game.WINDOW_SIZE[1])]#start offset position

        for object in self.map_UI.objects:
            object.update(self.pos)

    def update(self):
        super().update()
        self.update_pos(self.scroll)
        self.limit_pos()
        for object in self.map_UI.objects:
            object.update(self.scroll)

        self.map_UI.objects[self.index].currentstate.handle_input('Equip')

    def update_pos(self,scroll):
        self.pos = [self.pos[0]+scroll[0],self.pos[1]+scroll[1]]

    def limit_pos(self):
        #self.pos[0] = min(0,self.pos[0])
        #self.pos[0] = max(self.game.WINDOW_SIZE[0] - self.map_UI.BG.get_width(),self.pos[0])
        #self.pos[1] = min(0,self.pos[1])
        #self.pos[1] = max(self.game.WINDOW_SIZE[1] - self.map_UI.BG.get_height(),self.pos[1])
        if self.pos[0] > 0:
            self.pos[0] = 0
            self.scroll[0] = 0
        elif self.pos[0] < self.game.WINDOW_SIZE[0] - self.map_UI.BG.get_width():
            self.pos[0] = self.game.WINDOW_SIZE[0] - self.map_UI.BG.get_width()
            self.scroll[0] = 0
        if self.pos[1] > 0:
            self.pos[1] = 0
            self.scroll[1] = 0
        elif self.pos[1] < self.game.WINDOW_SIZE[1] - self.map_UI.BG.get_height():
            self.pos[1] = self.game.WINDOW_SIZE[1] - self.map_UI.BG.get_height()
            self.scroll[1] = 0

    def render(self):
        super().render()
        self.game.screen.blit(self.map_UI.BG,self.pos)
        for object in self.map_UI.objects:
            self.game.screen.blit(object.image,object.rect.topleft)

    def calculate_position(self):
        scroll = [-self.map_UI.objects[self.index].rect.center[0]+self.game.WINDOW_SIZE[0]*0.5,-self.map_UI.objects[self.index].rect.center[1]+self.game.WINDOW_SIZE[1]*0.5]
        for object in self.map_UI.objects:
            object.update(scroll)
        self.update_pos(scroll)

    def handle_events(self,input):
        self.scroll = [-2*input[2]['r_stick'][0],-2*input[2]['r_stick'][1]]#right analog stick

        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()
            elif input[-1] == 'rb':#nezt page
                self.exit_state()
                new_state = Inventory_menu(self.game)
                new_state.enter_state()
            elif input[-1] == 'right':#should it be left analogue stick?
                self.map_UI.objects[self.index].currentstate.handle_input('Idle')
                self.index += 1
                self.index = min(self.index,len(self.map_UI.objects)-1)
                self.calculate_position()
            elif input[-1] == 'left':#should it be left analogue stick?
                self.map_UI.objects[self.index].currentstate.handle_input('Idle')
                self.index -= 1
                self.index = max(0,self.index)
                self.calculate_position()
            elif input[-1] == 'a':#when pressing a
                self.map_UI.objects[self.index].activate()#open the local map. I guess it should be a new state

    def exit_state(self):
        super().exit_state()
        for object in self.map_UI.objects:
            object.revert()

class Fast_travel_menu(Gameplay):
    def __init__(self, game):
        super().__init__(game)
        self.travel_UI = self.game.game_objects.UI['fast_travel']
        self.index = [0,0]
        self.define_destination()
        self.define_pointer()

    def define_destination(self):
        self.destinations = []
        for level in self.game.game_objects.world_state.travel_points.keys():
            self.destinations.append(level)

    def define_pointer(self):#called everytime we move from one area to another
        size = [48,16]
        self.pointer = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(self.pointer,[200,50,50,255],(0,0,size[0],size[1]),width=1,border_radius=5)

    def blit_BG(self):
        self.game.screen.blit(self.travel_UI.BG,(0,0))#pointer

    def blit_destinations(self):
        for index, name in enumerate(self.game.game_objects.world_state.travel_points.keys()):
            text = self.game.game_objects.font.render((152,80), name, 100)
            text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
            self.game.screen.blit(text,self.travel_UI.name_pos[index])#pointer

    def blit_pointer(self):
        pos = self.travel_UI.name_pos[self.index[0]]
        self.game.screen.blit(self.pointer,pos)#pointer

    def render(self):
        super().render()
        self.blit_BG()
        self.blit_destinations()
        self.blit_pointer()

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()

            elif input[-1] =='down':
                self.index[0] += 1
                self.index[0] = min(self.index[0],len(self.destinations)-1)

            elif input[-1] =='up':
                self.index[0] -= 1
                self.index[0] = max(0,self.index[0])

            elif input[-1] == 'a':
                self.exit_state()
                self.game.game_objects.player.set_abs_dist()
                level = self.destinations[self.index[0]]
                cord = self.game.game_objects.world_state.travel_points[level]
                self.game.game_objects.load_map(level,cord)

class Fast_travel_unlock(Gameplay):
    def __init__(self, game,fast_travel):
        super().__init__(game)
        self.fast_travel = fast_travel
        self.index = [0,0]
        self.letter_frame = 0
        self.actions = ['yes','no']
        self.conv = 'Would you like to offer ' + str(self.fast_travel.cost) + ' ambers to this statue?'
        self.bg_size = [152,48]
        self.bg = self.game.game_objects.font.fill_text_bg(self.bg_size)
        self.define_pos()
        self.define_pointer()

    def define_pos(self):
        self.pos = []
        for i in range(0,len(self.actions)):
            self.pos.append([255+i*30,110])

    def define_pointer(self):#called everytime we move from one area to another
        size = [16,10]
        self.pointer = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(self.pointer,[200,50,50,255],(0,0,size[0],size[1]),width=1,border_radius=5)

    def blit_BG(self):
        self.game.screen.blit(self.bg,[self.game.WINDOW_SIZE[0]*0.5-self.bg_size[0]*0.5,self.game.WINDOW_SIZE[1]*0.25])

    def blit_actions(self):
        for index, action in enumerate(self.actions):
            response = self.game.game_objects.font.render(text = action)
            self.game.screen.blit(response,self.pos[index])

    def blit_text(self):
        text = self.game.game_objects.font.render((130,90), self.conv, int(self.letter_frame//2))
        self.game.screen.blit(text,(220,90))

    def blit_pointer(self):
        pos = self.pos[self.index[0]]
        self.game.screen.blit(self.pointer,pos)#pointer

    def update(self):
        super().update()
        self.letter_frame += self.game.dt

    def render(self):
        super().render()
        self.blit_BG()
        self.blit_actions()
        self.blit_text()
        self.blit_pointer()

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()

            elif input[-1] =='right':
                self.index[0] += 1
                self.index[0] = min(self.index[0],len(self.pos)-1)

            elif input[-1] =='left':
                self.index[0] -= 1
                self.index[0] = max(0,self.index[0])

            elif input[-1] == 'a':
                if self.index[0] == 1:#no
                    self.exit_state()
                elif self.index[0] == 0:#yes
                    if self.fast_travel.unlock():#enough money: unlocked
                        self.exit_state()
                    else:#not enout money
                        pass

class Ability_upgrades(Gameplay):#when double clicking the save point, open ability upgrade screen, spirit abilities
    def __init__(self, game):
        super().__init__(game)
        self.define_UI()
        self.index = [0,0]
        self.letter_frame = 0
        self.define_abilities()
        self.define_pointer()
        self.blit_titles()

    def define_UI(self):
        self.abillity_UI = self.game.game_objects.UI['ability_spirit_upgrade']
        self.abilities = self.game.game_objects.player.abilities.spirit_abilities

    def define_abilities(self):
        rows = self.abillity_UI.rows
        for ability in self.abilities.keys():
            self.abillity_UI.abilities[rows[ability]][0].activate(1)#set the first column of abilities aila has to one level 1

            for level in range(1,len(self.abillity_UI.abilities[rows[ability]][0].description)):#the levels already aquired
                if level < self.abilities[ability].level:
                    self.abillity_UI.abilities[rows[ability]][level].activate(level+1)
                else:
                    self.abillity_UI.abilities[rows[ability]][level].deactivate(level+1)

    def define_pointer(self,size = [32,32]):#called everytime we move from one area to another
        self.pointer = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(self.pointer,[200,50,50,255],(0,0,size[0],size[1]),width=1,border_radius=5)

    def update(self):
        super().update()
        self.letter_frame += self.game.dt

    def render(self):
        super().render()
        self.blit_BG()
        self.blit_symbols()
        self.blit_pointer()
        self.blit_description()
        self.blit_titles()

    def blit_titles(self):
        title = self.game.game_objects.font.render(text = 'absorbed abillities')
        title.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
        self.game.screen.blit(title,[250,50])

    def blit_pointer(self):
        self.game.screen.blit(self.pointer,self.abillity_UI.abilities[self.index[0]][self.index[1]].rect.center)#pointer

    def blit_symbols(self):
        for abilities in self.abillity_UI.abilities:
            for ability in abilities:
                ability.animation.update()
                self.game.screen.blit(ability.image,ability.rect.center)

    def blit_BG(self):
        self.abillity_UI.BG.set_alpha(230)
        self.game.screen.blit(self.abillity_UI.BG,(0,0))#pointer

    def blit_description(self):
        ability = self.abillity_UI.abilities[self.index[0]][0]#the row we are on
        level = self.index[1]#the columns we are on
        conv = ability.description[level]
        text = self.game.game_objects.font.render((152,80), conv, int(self.letter_frame//2))
        text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
        self.game.screen.blit(text,(380,120))

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()
            elif input[-1] == 'rb' or input[-1] == 'lb':#nezt page
                self.exit_state()
                new_state = Ability_movement_upgrades(self.game)
                new_state.enter_state()
            elif input[-1]=='a' or input[-1]=='return':
                self.choose_ability()

            elif input[-1] =='right':
                self.index[1] += 1
                self.index[1] = min(self.index[1],len(self.abillity_UI.abilities[self.index[0]])-1)
                self.letter_frame = 0

            elif input[-1] =='left':
                self.index[1] -= 1
                self.index[1] = max(0,self.index[1])
                self.letter_frame = 0

            elif input[-1] =='down':
                self.index[0] += 1
                self.index[0] = min(self.index[0],len(self.abillity_UI.abilities)-1)
                self.letter_frame = 0
                self.index[1] = min(self.index[1],len(self.abillity_UI.abilities[self.index[0]])-1)

            elif input[-1] =='up':
                self.index[0] -= 1
                self.index[0] = max(0,self.index[0])
                self.letter_frame = 0
                self.index[1] = min(self.index[1],len(self.abillity_UI.abilities[self.index[0]])-1)

    def choose_ability(self):
        ability = self.abillity_UI.abilities[self.index[0]][0]#the row we are on
        level = self.index[1]#the columns we are on
        if self.abilities[type(ability).__name__].level == level:
            self.abilities[type(ability).__name__].upgrade_ability()
            self.abillity_UI.abilities[self.index[0]][level].activate(level+1)

    def exit_state(self):
        super().exit_state()
        self.game.game_objects.player.currentstate.handle_input('Pray_spe_post')

class Ability_movement_upgrades(Ability_upgrades):#when double clicking the save point, open ability upgrade screen, spirit abilities
    def __init__(self, game):
        super().__init__(game)

    def define_UI(self):
        self.abillity_UI = self.game.game_objects.UI['ability_movement_upgrade']
        self.abilities = self.game.game_objects.player.abilities.movement_dict

    def blit_titles(self):
        title = self.game.game_objects.font.render(text = 'absorbed abillities')
        title.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
        self.game.screen.blit(title,[250,50])

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()
            elif input[-1] == 'rb' or input[-1] == 'lb':#nezt page
                self.exit_state()
                new_state = Ability_upgrades(self.game)
                new_state.enter_state()
            elif input[-1]=='a' or input[-1]=='return':
                self.choose_ability()

            elif input[-1] =='right':
                self.index[1] += 1
                self.index[1] = min(self.index[1],len(self.abillity_UI.abilities[self.index[0]])-1)
                self.letter_frame = 0

            elif input[-1] =='left':
                self.index[1] -= 1
                self.index[1] = max(0,self.index[1])
                self.letter_frame = 0

            elif input[-1] =='down':
                self.index[0] += 1
                self.index[0] = min(self.index[0],len(self.abillity_UI.abilities)-1)
                self.letter_frame = 0
                self.index[1] = min(self.index[1],len(self.abillity_UI.abilities[self.index[0]])-1)

            elif input[-1] =='up':
                self.index[0] -= 1
                self.index[0] = max(0,self.index[0])
                self.letter_frame = 0
                self.index[1] = min(self.index[1],len(self.abillity_UI.abilities[self.index[0]])-1)

class Fading(Gameplay):#fades out and then in
    def __init__(self,game):
        super().__init__(game)
        self.page = 0
        self.render_fade = [self.render_out,self.render_in]
        self.fade_surface = pygame.Surface(self.game.WINDOW_SIZE, pygame.SRCALPHA, 32)
        self.fade_surface.fill((0,0,0))
        self.init_out()

    def init_in(self):
        self.count = 0
        self.fade_length = 20
        self.fade_surface.set_alpha(255)

    def init_out(self):
        self.count = 0
        self.fade_length = 60
        self.fade_surface.set_alpha(int(255/self.fade_length))

    def update(self):
        super().update()
        self.count += min(self.game.dt,2)#the framerate jump when loading map. This class is called when loading a map. Need to set maximum dt
        if self.count > self.fade_length:
            self.page += 1
            self.init_in()
            if self.page == 2:
                self.exit()

    def exit(self):
        self.game.game_objects.load_bg_music()
        self.exit_state()

    def render(self):
        self.render_fade[self.page]()
        self.game.screen.blit(self.fade_surface, (0,0))

    def render_in(self):
        super().render()
        self.fade_surface.set_alpha(int((self.fade_length - self.count)*(255/self.fade_length)))

    def render_out(self):
        self.fade_surface.set_alpha(int(self.count*(255/self.fade_length)))

    def handle_events(self, input):
        pass

class Conversation(Gameplay):
    def __init__(self, game, npc):
        super().__init__(game)
        self.game.game_objects.player.reset_movement()
        self.npc = npc
        self.print_frame_rate = C.animation_framerate
        self.text_WINDOW_SIZE = (352, 96)
        self.blit_pos = [int((self.game.WINDOW_SIZE[0]-self.text_WINDOW_SIZE[0])*0.5),60]
        self.clean_slate()

        self.conv = self.npc.dialogue.get_conversation()

    def clean_slate(self):
        self.letter_frame = 0
        self.text_window = self.game.game_objects.font.fill_text_bg(self.text_WINDOW_SIZE)
        self.text_window.blit(self.npc.portrait,(0,10))

    def update(self):
        super().update()
        self.letter_frame += self.print_frame_rate*self.game.dt

    def render(self):
        super().render()
        text = self.game.game_objects.font.render((272,80), self.conv, int(self.letter_frame))
        self.text_window.blit(text,(64,8))
        self.game.screen.blit(self.text_window,self.blit_pos)

    def handle_events(self, input):
        if input[0]:
            if input[-1] == 'start':
                self.exit_state()

            elif input[-1] == 'y':
                if self.letter_frame < len(self.conv):
                    self.letter_frame = 10000
                else:#check if we have a series of conversations or not
                    self.clean_slate()
                    self.npc.dialogue.increase_conv_index()
                    self.conv = self.npc.dialogue.get_conversation()
                    if not self.conv:
                        self.exit_state()

    def exit_state(self):
        super().exit_state()
        self.npc.buisness()

class Facilities(Gameplay):
    def __init__(self, game, npc = None):
        super().__init__(game)
        self.npc = npc
        self.pointer_index = [0,0]#position of box
        self.pointer = entities_UI.Menu_Arrow()
        self.set_response('welcome')
        self.render_list=[self.blit_frame1]
        self.handle_list=[self.handle_frame1]
        self.select_list=[self.select_frame1]
        self.pointer_list = [self.pointer_frame1]
        self.frame = 1

    def init_canvas(self,size=[64,64]):
        self.surf=[]
        self.bg = self.game.game_objects.font.fill_text_bg(size)
        for string in self.actions:
            self.surf.append(self.game.game_objects.font.render(text = string))

    def blit_frame1(self):
        for index, surf in enumerate(self.surf):
            self.bg.blit(surf,(30,10+index*10))#
        self.game.screen.blit(self.bg,(280,120))#box position

    def render(self):
        super().render()
        self.render_list[-1]()
        self.pointer_list[-1]()
        self.blit_response()

    def handle_events(self,input):
        self.handle_list[-1](input)

    def set_response(self,text):
        self.respond = self.game.game_objects.font.render(text = text)

    def blit_response(self):
        self.game.screen.blit(self.respond,(190,150))

    def pointer_frame1(self):
        self.game.screen.blit(self.pointer.img,(300,130+10*self.pointer_index[1]))#pointer

    def select(self):
        self.select_list[-1]()

    def select_frame1(self):
        pass

    def next_frame(self):#instead of hardcoding it, maybe it can iterate through the number somehow
        self.frame+=1
        self.render_list.append(getattr(self,'blit_frame'+str(self.frame)))
        self.select_list.append(getattr(self,'select_frame'+str(self.frame)))
        self.handle_list.append(getattr(self,'handle_frame'+str(self.frame)))
        self.pointer_list.append(getattr(self,'pointer_frame'+str(self.frame)))

    def previouse_frame(self):
        self.render_list.pop()
        self.select_list.pop()
        self.handle_list.pop()
        self.pointer_list.pop()
        self.frame-=1

    def handle_frame1(self,input):
        if input[0]:#press
            if input[-1] == 'y':
                self.exit_state()
            elif input[-1] =='down':
                self.pointer_index[1] += 1
                self.pointer_index[1] = min(self.pointer_index[1],len(self.actions)-1)
            elif input[-1] =='up':
                self.pointer_index[1] -= 1
                self.pointer_index[1] = max(self.pointer_index[1],0)
            elif input[-1]=='a' or input[-1]=='return':
                self.select()

class Smith(Facilities):
    def __init__(self, game, npc):
        super().__init__(game,npc)
        self.actions = ['upgrade','enhance','cancel']
        self.init_canvas([64,22*len(self.actions)])#specific for each facility

    def select_frame2(self):
        if self.pointer_index[1] < len(self.actions)-1:#if we select upgrade
            stone_str = self.actions[self.pointer_index[1]]
            self.game.game_objects.player.sword.set_stone(stone_str)
            self.set_response('Now it is ' + stone_str)
        else:#select cancel
            self.previouse_frame()

    def pointer_frame2(self):
        self.pointer_frame1()

    def handle_frame2(self,input):
        self.handle_frame1(input)

    def blit_frame2(self):
        self.blit_frame1()

    def previouse_frame(self):
        super().previouse_frame()
        self.actions=['upgrade','enhance','cancel']
        self.init_canvas([64,22*len(self.actions)])#specific for each facility

    def next_frame(self):
        super().next_frame()
        self.actions=[]
        for index, stones in enumerate(self.game.game_objects.player.sword.stones):
            self.actions.append(stones)
        self.actions.append('cancel')
        self.init_canvas([64,22*len(self.actions)])

    def select_frame1(self):
        if self.pointer_index[1] == 0:#if we select upgrade
            self.upgrade()
        elif self.pointer_index[1] == 1:
            self.next_frame()
        else:#select cancel
            self.exit_state()

    def upgrade(self):
        if self.game.game_objects.player.inventory['Tungsten'] >= self.game.game_objects.player.sword.tungsten_cost:
            self.game.game_objects.player.sword.level_up()
            self.set_response('Now it is better')
        else:#not enough tungsten
            self.set_response('You do not have enought heavy rocks')

class Bank(Facilities):
    def __init__(self, game, npc):
        super().__init__(game,npc)
        self.actions=['withdraw','deposit','cancel']
        self.ammount = 0
        self.init_canvas()

    def blit_frame2(self):
        self.game.screen.blit(self.bg,(280,120))#box position
        self.amount_surf = self.game.game_objects.font.render(text = str(self.ammount))
        self.game.screen.blit(self.amount_surf,(310,130))#box position

    def select_frame1(self):#exchane of money
        if self.pointer_index[1]==2:#cancel
            self.exit_state()
        else:#widthdraw or deposit
            self.bg = self.game.game_objects.font.fill_text_bg([64,64])
            self.next_frame()

    def select_frame2(self):
        if self.pointer_index[1]==0:#widthdraw
            self.game.game_objects.player.inventory['Amber_Droplet']+=self.ammount
            self.npc.ammount-=self.ammount
        elif self.pointer_index[1]==1:#deposit
            self.game.game_objects.player.inventory['Amber_Droplet']-=self.ammount
            self.npc.ammount+=self.ammount
        self.previouse_frame()

    def pointer_frame2(self):
        pass

    def handle_frame2(self,input):
        if input[0]:#press
            if input[-1] =='down':
                self.ammount -= 1
                self.ammount = max(self.ammount,0)
            elif input[-1] =='up':
                self.ammount += 1
                if self.pointer_index[1]==0:#widthdraw
                    self.ammount = min(self.ammount,self.npc.ammount)
                else:
                    self.ammount = min(self.ammount,self.game.game_objects.player.inventory['Amber_Droplet'])

            elif input[-1] =='right':
                self.ammount += 100
                if self.pointer_index[1]==0:#widthdraw
                    self.ammount = min(self.ammount,self.npc.ammount)
                else:
                    self.ammount = min(self.ammount,self.game.game_objects.player.inventory['Amber_Droplet'])
            elif input[-1] == 'left':
                self.ammount -= 100
                self.ammount = max(self.ammount,0)

            elif input[-1]=='a' or input[-1]=='return':
                self.select()

class Soul_essence(Facilities):#called from inorinoki
    def __init__(self, game):
        super().__init__(game)
        self.actions=['health','spirit','cancel']
        self.cost = 4
        self.init_canvas()

    def select_frame1(self):
        if self.pointer_index[1] == 0:#if we select health
            if self.game.game_objects.player.inventory['Soul_essence'] >= self.cost:
                pos = [self.game.game_objects.player.rect[0],-100]
                heart = Entities.Heart_container(pos,self.game.game_objects)
                self.game.game_objects.loot.add(heart)
                self.game.game_objects.player.inventory['Soul_essence']-=self.cost
        elif self.pointer_index[1] == 1:#if we select spirit
            if self.game.game_objects.player.inventory['Soul_essence'] >= self.cost:
                pos = [self.game.game_objects.player.rect[0],-100]
                spirit = Entities.Spirit_container(pos,self.game.game_objects)
                self.game.game_objects.loot.add(spirit)
                self.game.game_objects.player.inventory['Soul_essence']-=self.cost
        else:#select cancel
            self.exit_state()

class Vendor(Facilities):
    def __init__(self, game, npc):
        super().__init__(game, npc)
        self.letter_frame = 0
        self.init_canvas()
        self.pointer = entities_UI.Menu_Box()
        self.item_index = [0,0]#pointer of item

    def init_canvas(self):
        self.bg1 = self.game.game_objects.font.fill_text_bg([300,200])

        self.items = []
        for item in self.npc.inventory.keys():
            item=getattr(sys.modules[Entities.__name__], item)([0,0],self.game.game_objects)#make the object based on the string
            self.items.append(item)

        self.amber = getattr(sys.modules[Entities.__name__], 'Amber_Droplet')([0,0],self.game.game_objects)#make the object based on the string

        #tempporary to have many items to test scrollingl list
        for i in range(0,3):
            self.items.append(getattr(sys.modules[Entities.__name__], 'Amber_Droplet')([0,0],self.game.game_objects))
        self.items.append(getattr(sys.modules[Entities.__name__], 'Bone')([0,0],self.game.game_objects))

        self.display_number = min(3,len(self.items))#number of items to list
        self.sale_items=self.items[0:self.display_number+1]

        self.buy_sur = self.game.game_objects.font.render(text = 'Buy')
        self.cancel_sur= self.game.game_objects.font.render(text = 'Cancel')

    def update(self):
        super().update()
        self.letter_frame += 1

    def blit_frame1(self):
        width=self.bg1.get_width()
        self.game.screen.blit(self.bg1,((self.game.WINDOW_SIZE[0]-width)/2,20))
        self.blit_items()
        self.blit_money()
        self.blit_description()

    def blit_frame2(self):
        self.blit_frame1()
        self.bg2.blit(self.buy_sur,(30,10))#
        self.bg2.blit(self.cancel_sur,(30,20))#
        self.game.screen.blit(self.bg2,(280,120))#box position

    def blit_money(self):#blit how much gold we have in inventory
        money = self.game.game_objects.player.inventory['Amber_Droplet']
        count_text = self.game.game_objects.font.render(text = str(money))
        self.game.screen.blit(count_text,(200,50))
        self.amber.animation.update()
        self.game.screen.blit(self.amber.image,(190,50))

    def blit_description(self):
        conv=self.items[self.item_index[1]].description
        text = self.game.game_objects.font.render((272,80), conv, int(self.letter_frame//2))
        self.game.screen.blit(text,(190,100))

    def blit_items(self):
        for index, item in enumerate(self.sale_items):
            if index < self.display_number:
                item.animation.update()
                self.game.screen.blit(pygame.transform.scale(item.image,(10,10)),(240,80+20*index))
                #blit cost
                item_name=str(type(item).__name__)
                cost=self.npc.inventory[item_name]
                cost_text = self.game.game_objects.font.render(text = str(cost))
                self.game.screen.blit(cost_text,(260,80+20*index))

            else:#the last index
                item.animation.update()
                item.image.set_alpha(100)
                self.game.screen.blit(pygame.transform.scale(item.image,(10,10)),(240,140))

    def pointer_frame1(self):
        self.game.screen.blit(self.pointer.img,(220+20*self.pointer_index[0],60+20*self.pointer_index[1]))#pointer

    def pointer_frame2(self):
        self.game.screen.blit(self.pointer.img,(300,130+10*self.pointer_index[1]))#pointer

    def select_frame1(self):
        self.next_frame()
        self.bg2 = self.game.game_objects.font.fill_text_bg([64,32])
        self.item = type(self.items[self.item_index[1]]).__name__
        self.pointer = entities_UI.Menu_Arrow()

    def select_frame2(self):
        if self.pointer_index[1] == 0:#if we select buy
            self.buy()
        else:
            self.set_response('What do you want?')
        self.previouse_frame()
        self.pointer = entities_UI.Menu_Box()

    def buy(self):
        if self.game.game_objects.player.inventory['Amber_Droplet']>=self.npc.inventory[self.item]:
            self.game.game_objects.player.inventory[self.item] += 1
            self.game.game_objects.player.inventory['Amber_Droplet']-=self.npc.inventory[self.item]
            self.set_response('Thanks for buying')
        else:#not enough money
            self.set_response('Get loss you poor piece of shit')

    def handle_frame1(self, input):
        if input[0]:#press
            if input[-1] == 'y':
                self.exit_state()

            elif input[-1] =='down':
                self.item_index[1] += 1
                self.item_index[1] = min(self.item_index[1],len(self.items)-1)

                if self.pointer_index[1]==2:
                    self.sale_items=self.items[self.item_index[1]-self.display_number+1:self.item_index[1]+self.display_number-1]
                    if self.item_index[1]==len(self.items)-1:
                        return

                self.pointer_index[1] += 1
                self.pointer_index[1] = min(self.pointer_index[1],self.display_number-1)
                self.letter_frame=0

            elif input[-1] =='up':
                self.item_index[1]-=1
                self.item_index[1] = max(self.item_index[1],0)

                if self.pointer_index[1]==0:
                    self.sale_items=self.items[self.item_index[1]:self.item_index[1]+self.display_number+1]
                    if self.item_index[1]==0:
                        return

                self.pointer_index[1] -= 1
                self.pointer_index[1] = max(self.pointer_index[1],0)
                self.letter_frame = 0

            elif input[-1]=='a' or input[-1]=='return':
                self.select()

    def handle_frame2(self,input):
        if input[0]:#press
            if input[-1] == 'y':
                self.exit_state()

            elif input[-1] =='down':
                self.pointer_index[1] += 1
                self.pointer_index[1] = min(self.pointer_index[1],1)
            elif input[-1] =='up':
                self.pointer_index[1] -= 1
                self.pointer_index[1] = max(self.pointer_index[1],0)
            elif input[-1]=='a' or input[-1]=='return':
                self.select()

class Cutscenes(Gameplay):#basically, this class is not needed but would be nice to have the cutscene classes in a seperate file
    def __init__(self, game,scene):
        super().__init__(game)
        #self.game.game_objects.player.reset_movement()
        self.current_scene = getattr(cutscene, scene)(self)#make an object based on string
        if scene != 'Death':
            self.game.game_objects.world_state.cutscenes_complete.append(scene)#scenes will not run if the scnene is in this list

    def update(self):
        super().update()
        self.current_scene.update()

    def render(self):
        super().render()#want the BG to keep rendering for engine. It is not needed for file cut scnene
        self.current_scene.render()#to plot the abilities. Maybe better with another state?

    def handle_events(self, input):
        self.current_scene.handle_events(input)

class New_ability(Gameplay):#when player obtaines a new ability
    def __init__(self, game,ability):
        super().__init__(game)
        self.page = 0
        self.render_fade=[self.render_in,self.render_out]

        self.img = self.game.game_objects.player.sprites.sprite_dict[ability][0].copy()
        self.game.game_objects.player.reset_movement()

        self.surface = pygame.Surface((int(self.game.WINDOW_SIZE[0]), int(self.game.WINDOW_SIZE[1])), pygame.SRCALPHA, 32).convert_alpha()
        self.surface.fill((0,0,0))

        self.fade = 0
        self.surface.set_alpha(self.fade)

    def render(self):
        super().render()
        self.surface.set_alpha(int(self.fade))
        self.render_fade[self.page]()
        self.game.screen.blit(self.surface,(0, 0))
        self.game.screen.blit(self.img,(200, 200))#blit directly on screen to avoid alpha change on this

    def render_in(self):
        self.fade += 1
        self.fade = min(self.fade,150)
        self.img.set_alpha((255-150)+int(self.fade))

    def render_out(self):
        self.fade -= 1
        self.fade = max(self.fade,0)
        self.img.set_alpha(int(self.fade))

        if self.fade == 0:
            self.exit_state()

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'start':
                self.page = 1
            elif input[-1] == 'a':
                self.page = 1

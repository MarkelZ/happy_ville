import pygame, sys
import UI_loader
import Entities#to load the inventory -> entities_UI?
import states_inventory

class Select_menu():
    def __init__(self, game_state):
        self.game_state = game_state
        self.game_objects = game_state.game.game_objects

    def enter_state(self,newstate):
         self.game_state.state = getattr(sys.modules[__name__], newstate)(self.game_state)#make a class based on the name of the newstate: need to import sys

    def update(self):
        pass

    def render(self):
        pass

    def handle_events(self,input):
        pass

    def exit_state(self):
        self.game_state.exit_state()

class Inventory(Select_menu):
    def __init__(self, game_state):
        super().__init__(game_state)
        self.iventory_UI = UI_loader.UI_loader(self.game_objects,'inventory')
        self.letter_frame = 0#for description
        self.state = states_inventory.Items(self)
        self.item_index = [0,0]

        self.define_blit_positions()
        self.define_pointer()

    def define_blit_positions(self):#set positions
        items = self.iventory_UI.items.copy()#a list if empty items
        key_items = self.iventory_UI.key_items#a dict of empty key items
        index = 0
        for key in self.game_objects.player.inventory.keys():#crease the object in inventory and sepeerate between useable items and key items
            item = getattr(sys.modules[Entities.__name__], key)([0,0],self.game_objects)#make the object based on the string
            if hasattr(item, 'use_item'):
                item.rect.topleft = items[index].rect.topleft
                item.number = self.game_objects.player.inventory[key]#number of items euirepped
                items[index] = item
                index += 1
            else:
                item.rect.topleft = key_items[key].rect.topleft
                item.number = self.game_objects.player.inventory[key]#number of items euirepped
                key_items[key] = item

        stones = self.iventory_UI.stones#a dict of emppty stones
        for key in self.game_objects.player.sword.stones.keys():
            self.game_objects.player.sword.stones[key].rect.topleft = stones[key].rect.topleft
            stones[key] = self.game_objects.player.sword.stones[key]

        self.items = {'sword':list(stones.values()),'key_items':list(key_items.values()),'items':items}#organised items: used to select the item

    def define_pointer(self,size = [16,16]):#called everytime we move from one area to another
        self.pointer = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(self.pointer,[200,50,50,255],(0,0,size[0],size[1]),width=1,border_radius=5)

    def update(self):
        self.letter_frame += self.game_objects.game.dt

    def render(self):
        self.blit_inventory_BG()
        self.blit_inventory()
        self.blit_sword()
        self.blit_pointer()
        self.blit_description()

    def blit_inventory_BG(self):
        self.iventory_UI.BG.set_alpha(230)
        self.game_objects.game.screen.blit(self.iventory_UI.BG,(0,0))

    def blit_inventory(self):
        for index, item in enumerate(self.items['items']):#items we can use
            item.animation.update()
            self.game_objects.game.screen.blit(pygame.transform.scale(item.image,(16,16)),item.rect.topleft)
            number = self.game_objects.font.render(text = str(item.number))
            number.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
            self.game_objects.game.screen.blit(number,item.rect.center)

        for index, item in enumerate(self.items['key_items']):
            item.animation.update()
            self.game_objects.game.screen.blit(pygame.transform.scale(item.image,(16,16)),item.rect.topleft)
            number = self.game_objects.font.render(text = str(item.number))
            number.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
            self.game_objects.game.screen.blit(number,item.rect.center)

    def blit_sword(self):
        self.iventory_UI.sword.animation.update()
        self.game_objects.game.screen.blit(self.iventory_UI.sword.image,self.iventory_UI.sword.rect.topleft)

        for stone in self.items['sword']:
            stone.animation.update()
            self.game_objects.game.screen.blit(stone.image,stone.rect.topleft)

    def blit_pointer(self):
        self.game_objects.game.screen.blit(self.pointer,self.items[self.state.state_name][self.item_index[0]].rect.topleft)#pointer

    def blit_description(self):
        self.conv = self.items[self.state.state_name][self.item_index[0]].description
        text = self.game_objects.font.render((152,80), self.conv, int(self.letter_frame//2))
        text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
        self.game_objects.game.screen.blit(text,(380,120))

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()
            elif input[-1] == 'rb':#nezt page
                self.enter_state('Omamori')
            elif input[-1] == 'lb':#previouse page
                self.enter_state('Map')
            elif input[-1]=='a' or input[-1]=='return':
                self.use_item()
            self.state.handle_input(input)
            self.letter_frame = 0

    def use_item(self):
        if not hasattr(self.items[self.state.state_name][self.item_index[0]], 'use_item'): return#if it is a item
        if self.items[self.state.state_name][self.item_index[0]].number <= 0: return#if we have more than 0 item
        self.items[self.state.state_name][self.item_index[0]].use_item()

class Omamori(Select_menu):
    def __init__(self, game_state):
        super().__init__(game_state)
        self.omamori_UI = UI_loader.UI_loader(self.game_objects,'omamori')

        self.letter_frame = 0#for description
        self.define_blit_positions()
        self.define_pointer()
        self.omamori_index = 0

    def define_blit_positions(self):
        for index, key in enumerate(self.game_objects.player.omamoris.equipped):#the equiped ones
            pos = self.omamori_UI.equipped[index].rect.center
            self.game_objects.player.omamoris.equipped[key].set_pos(pos)

        omamori_dict = self.omamori_UI.inventory#copy all empty ones and then overwrite with the rellavant ones in inventory
        for index, key in enumerate(self.game_objects.player.omamoris.inventory):#the ones in inventory
            pos = self.omamori_UI.inventory[key].rect.center
            self.game_objects.player.omamoris.inventory[key].set_pos(pos)
            omamori_dict[key] = self.game_objects.player.omamoris.inventory[key]
        self.omamori_list = list(omamori_dict.values())

    def define_pointer(self,size = [16,16]):#called everytime we move from one area to another
        size = self.omamori_list[0].rect.size
        self.pointer = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(self.pointer,[200,50,50,255],(size[0]*0.5-8,size[1]*0.5+8,16,16),width=1,border_radius=5)

    def update(self):
        super().update()
        self.letter_frame += self.game_objects.game.dt

    def render(self):
        super().render()
        self.blit_omamori_BG()
        self.blit_omamori_menu()
        self.blit_pointer()
        self.blit_description()

    def blit_omamori_BG(self):
        self.omamori_UI.BG.set_alpha(230)
        self.game_objects.game.screen.blit(self.omamori_UI.BG,(0,0))

    def blit_omamori_menu(self):
        for omamori in self.game_objects.player.omamoris.equipped.values():#equipped ones
            omamori.animation.update()
            self.game_objects.game.screen.blit(omamori.image,omamori.rect.topleft)

        for omamori in self.omamori_list:
            omamori.animation.update()
            self.game_objects.game.screen.blit(omamori.image,omamori.rect.topleft)

    def blit_description(self):
        self.conv = self.omamori_list[self.omamori_index].description
        text = self.game_objects.font.render((152,80), self.conv, int(self.letter_frame//2))
        text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
        self.game_objects.game.screen.blit(text,(380,120))

    def blit_pointer(self):
        pos = self.omamori_list[self.omamori_index].rect.topleft
        self.game_objects.game.screen.blit(self.pointer,pos)#pointer

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()
            elif input[-1] == 'rb':#nezt page
                if self.game_objects.world_state.statistics['kill']:#if we have killed something
                    self.enter_state('Journal')
            elif input[-1] == 'lb':#previouse page
                self.enter_state('Inventory')
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
        self.game_objects.player.omamoris.equip_omamori(name)

        for index, omamori in enumerate(self.game_objects.player.omamoris.equipped.values()):#update the positions of the equiped ones
            pos = self.omamori_UI.equipped[index].rect.center
            omamori.set_pos(pos)

class Journal(Select_menu):
    def __init__(self, game_sate):
        super().__init__(game_sate)
        self.journal_UI = UI_loader.UI_loader(self.game_objects,'journal')
        self.letter_frame = 0
        self.journal_index = [0,0]
        self.enemies = []
        self.enemy_index = self.journal_index.copy()
        self.number = 8 #number of enemies per page

        for enemy in self.game_objects.world_state.statistics['kill']:
            self.enemies.append(getattr(sys.modules[Entities.__name__], enemy.capitalize())([0,0],self.game_objects))#make the object based on the string

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
        self.letter_frame += self.game_objects.game.dt

    def render(self):
        super().render()
        self.blit_journal_BG()
        self.blit_names()
        self.blit_pointer()
        self.blit_enemy()
        self.blit_description()

    def blit_journal_BG(self):
        self.journal_UI.BG.set_alpha(230)
        self.game_objects.game.screen.blit(self.journal_UI.BG,(0,0))

    def blit_names(self):
        for index, enemy in enumerate(self.selected_enemies):
            name = enemy.__class__.__name__
            text = self.game_objects.font.render((152,80), name, 100)
            text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
            self.game_objects.game.screen.blit(text,self.journal_UI.name_pos[index])

    def blit_pointer(self):
        pos = [self.journal_UI.name_pos[self.journal_index[0]][0],self.journal_UI.name_pos[self.journal_index[0]][1]-5]#add a offset
        self.game_objects.game.screen.blit(self.pointer,pos)#pointer

    def blit_enemy(self):
        enemy = self.selected_enemies[self.journal_index[0]]
        enemy.rect.midbottom = self.journal_UI.image_pos#allign based on bottom
        enemy.animation.update()
        self.game_objects.game.screen.blit(enemy.image,[enemy.rect.center[0]-enemy.rect.width*0.5,enemy.rect.center[1]-enemy.rect.height*0.5])#it blits the top left courner so need to correct based on the rectanle size

    def blit_description(self):
        self.conv = self.selected_enemies[self.journal_index[0]].description
        text = self.game_objects.font.render((152,80), self.conv, int(self.letter_frame//2))
        text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
        self.game_objects.game.screen.blit(text,(380,120))

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()
            elif input[-1] == 'rb':#nezt page
                pass
            elif input[-1] == 'lb':#previouse page
                self.enter_state('Omamori')
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

class Map(Select_menu):
    def __init__(self, game):
        super().__init__(game)
        self.map_UI = UI_loader.UI_loader(self.game_objects,'map')

        self.scroll = [0,0]
        self.index = 0
        self.pos = [-0.5*(self.map_UI.BG.get_width() - self.game_objects.game.WINDOW_SIZE[0]),-0.5*(self.map_UI.BG.get_height() - self.game_objects.game.WINDOW_SIZE[1])]#start offset position

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
        elif self.pos[0] < self.game_objects.game.WINDOW_SIZE[0] - self.map_UI.BG.get_width():
            self.pos[0] = self.game_objects.game.WINDOW_SIZE[0] - self.map_UI.BG.get_width()
            self.scroll[0] = 0
        if self.pos[1] > 0:
            self.pos[1] = 0
            self.scroll[1] = 0
        elif self.pos[1] < self.game_objects.game.WINDOW_SIZE[1] - self.map_UI.BG.get_height():
            self.pos[1] = self.game_objects.game.WINDOW_SIZE[1] - self.map_UI.BG.get_height()
            self.scroll[1] = 0

    def render(self):
        super().render()
        self.game_objects.game.screen.blit(self.map_UI.BG,self.pos)
        for object in self.map_UI.objects:
            self.game_objects.game.screen.blit(object.image,object.rect.topleft)

    def calculate_position(self):
        scroll = [-self.map_UI.objects[self.index].rect.center[0]+self.game_objects.game.WINDOW_SIZE[0]*0.5,-self.map_UI.objects[self.index].rect.center[1]+self.game_objects.game.WINDOW_SIZE[1]*0.5]
        for object in self.map_UI.objects:
            object.update(scroll)
        self.update_pos(scroll)

    def handle_events(self,input):
        self.scroll = [-2*input[2]['r_stick'][0],-2*input[2]['r_stick'][1]]#right analog stick

        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()
            elif input[-1] == 'rb':#nezt page
                self.enter_state('Inventory')
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

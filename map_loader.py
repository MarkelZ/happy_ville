import pygame, csv, Entities, math, random, Read_files

class Level():
    def __init__(self, level, game_objects):
        self.PLAYER_CENTER = game_objects.player_center
        self.SCREEN_SIZE = game_objects.game.WINDOW_SIZE
        self.TILE_SIZE = 16
        self.game_objects = game_objects
        self.level_name = level
        self.platforms = pygame.sprite.Group()
        self.platforms_pause=pygame.sprite.Group()
        self.npc_collision = pygame.sprite.Group()
        self.init_player_pos = (0,0)
        self.cameras = [Auto(self.PLAYER_CENTER),Auto_CapX(self.PLAYER_CENTER),Auto_CapY(self.PLAYER_CENTER),Fixed()]
        self.camera = self.cameras[0]
        self.load_map_data()

    def load_map_data(self):
        self.map_data = Read_files.read_json("maps/%s/%s.json" % (self.level_name,self.level_name))
        self.map_data = Read_files.format_tiled_json(self.map_data)
        for tileset in self.map_data['tilesets']:
            if 'source' in tileset.keys():
                self.map_data['statics_firstgid'] = tileset['firstgid']


    def set_camera(self, camera_number):
        self.camera = self.cameras[camera_number]

    def scrolling(self,player,shake):
        self.camera.scrolling(player,shake)

    def read_all_spritesheets(self):
        sprites = {}

        for tileset in self.map_data['tilesets']:
            if 'source' in tileset.keys():
                continue

            sheet = pygame.image.load("maps/%s/%s" % (self.level_name, tileset['image'])).convert_alpha()
            rows = int(sheet.get_rect().h/self.TILE_SIZE)
            columns = int(sheet.get_rect().w/self.TILE_SIZE)
            n = tileset['firstgid']

            for row in range(rows):
                for column in range(columns):
                    y = row * self.TILE_SIZE
                    x = column * self.TILE_SIZE
                    rect = pygame.Rect(x, y, x + self.TILE_SIZE, y + self.TILE_SIZE)
                    image = pygame.Surface((self.TILE_SIZE,self.TILE_SIZE),pygame.SRCALPHA,32)
                    image.blit(sheet,(0,0),rect)
                    sprites[n] = image
                    n += 1

        return sprites

    def load_bg_music(self):
        return pygame.mixer.Sound("Audio/" + self.level_name + "/default.wav")

    def load_collision_layer(self):#load the whole map

        map_collisions = self.map_data["collision"]

        for obj in map_collisions:
            id = obj['gid'] - (self.map_data['statics_firstgid'] + 6) #the last in depends on postion of COL stamp in stamp png
            object_position = (int(obj['x']),int(obj['y']))
            object_size = (int(obj['width']),int(obj['height']))
            #normal collision blocks
            if id == 0:
                new_block = Entities.Collision_block(object_position,object_size)
                self.game_objects.platforms.add(new_block)
            #spike collision blocks
            elif id == 1:
                new_block = Entities.Spikes(object_position,object_size)
                self.game_objects.platforms.add(new_block)


    def load_statics(self):

        map_statics = self.map_data["statics"]

        for obj in map_statics:
            id = obj['gid'] - self.map_data['statics_firstgid']
            object_position = (int(obj['x']),int(obj['y']))
            #player
            if id == 0:
                self.game_objects.player.set_pos(object_position)
                self.init_player_pos = object_position
            #npcs
            elif id == 1:
                properties = obj['properties']
                for property in properties:
                    if property['name'] == 'class':
                        npc_name = property['value']
                new_npc = getattr(Entities, npc_name)
                self.game_objects.npcs.add(new_npc(object_position))
            #enemies
            elif id == 2:
                properties = obj['properties']
                for property in properties:
                    if property['name'] == 'class':
                        enemy_name = property['value']
                new_enemy = getattr(Entities, enemy_name)
                self.game_objects.enemies.add(new_enemy(object_position, self.game_objects.eprojectiles,self.game_objects.loot))

    def load_bg(self):
    #returns one surface with all backround images blitted onto it, for each bg/fg layer
        bg_list = ['bg_fixed','bg_far','bg_mid','bg_near','fg_fixed','fg_parallax']
        deco_lists = {}
        top_left = {}
        bg_flags = {}

        for layer in list(self.map_data['tile_layers'].keys()):
            if '_deco' in layer:
                bg_list.append(layer)
                deco_base = layer[:layer.find('_deco')]
                if deco_base in deco_lists.keys():
                    deco_lists[deco_base].append(layer)
                else:
                    deco_lists[deco_base] = [layer]

        for bg in bg_list:
            bg_flags[bg] = True

        #all these figures below should be passed and not hardcoded, will break if we change UI etc.
        screen_center = self.PLAYER_CENTER
        new_map_diff = (self.init_player_pos[0] - screen_center[0], self.init_player_pos[1] - screen_center[1])

        cols = self.map_data['tile_layers'][list(self.map_data['tile_layers'].keys())[0]]['width']
        rows = self.map_data['tile_layers'][list(self.map_data['tile_layers'].keys())[0]]['height']

        blit_surfaces = {}
        for bg in bg_list:
            blit_surfaces[bg] = pygame.Surface((cols*self.TILE_SIZE,rows*self.TILE_SIZE), pygame.SRCALPHA, 32).convert_alpha()

        bg_sheets = {}
        bg_maps = {}

        spritesheet_dict = self.read_all_spritesheets()

        #try loading all parallax backgrounds
        for bg in bg_list:
            try:
                bg_maps[bg] = self.map_data['tile_layers'][bg]['data']
                top_left[bg] = (0,0)
            except:
                bg_flags[bg] = False
                #print("Failed to read %s" % bg)



        #blit background to one image, mapping tile set data to image data
        for bg in bg_list:
            if bg_flags[bg]:
                for index, tile_number in enumerate(bg_maps[bg]):
                    if tile_number == 0:
                        continue
                    else:
                        print(tile_number)
                        y = math.floor(index/cols)
                        x = (index - (y*cols))
                        blit_pos = (x * self.TILE_SIZE, y * self.TILE_SIZE)
                        blit_surfaces[bg].blit(spritesheet_dict[tile_number], blit_pos)
                        if top_left[bg] == (0,0):
                            top_left[bg] = blit_pos

        #blit deco over corresponding layer
        for bg in list(deco_lists.keys()):
            deco_lists[bg].sort()
            for deco in deco_lists[bg]:
                blit_surfaces[bg].blit(blit_surfaces[deco],(0,0))

        #print(top_left)
        backgrounds = []
        for i, bg in enumerate(bg_list):
            if bg == 'bg_fixed':
                backgrounds.append(Entities.BG_Block((0,0),blit_surfaces[bg]))#pos,img,parallax
            elif bg == 'bg_far':
                backgrounds.append(Entities.BG_Block((-int(0.97*new_map_diff[0]),-int(0.97*new_map_diff[1])),blit_surfaces[bg],0.03))#pos,img,parallax
            elif bg == 'bg_mid':
                backgrounds.append(Entities.BG_Block((-int(0.5*new_map_diff[0]),-int(0.5*new_map_diff[1])),blit_surfaces[bg],0.5))#pos,img,parallax
            elif bg == 'bg_near':
                backgrounds.append(Entities.BG_Block((-int(0.25*new_map_diff[0]),-int(0.25*new_map_diff[1])),blit_surfaces[bg],0.75))#pos,img,parallax
            elif bg == 'fg_fixed':
                backgrounds.append(Entities.BG_Block((0,0),blit_surfaces[bg]))#pos,img,parallax
            elif bg == 'fg_parallax':
                backgrounds.append(Entities.BG_Block((int(0.25*new_map_diff[0]),int(0.25*new_map_diff[1])),blit_surfaces[bg],1.25))#pos,img,parallax
        del blit_surfaces, bg_sheets, bg_maps
        return backgrounds

class Sprite_sheet():

    def __init__(self, filename):
        try:
            self.sheet =  pygame.image.load(filename).convert()
        except:
            #print(f"Unable to load spritesheet image: {filename}")
            raise SystemExit(e)

    def image_at(self, rectangle, colorkey = None):
        #Loads image from x, y, x+tilesize, y+tilesize.

        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def images_at(self, rects, colorkey = None):
        #returns list of all images in sheet
        return [self.image_at(rect, colorkey) for rect in rects]


#scrolling

class Camera():
    def __init__(self, center = (240,180)):
        self.scroll=[0,0]
        self.true_scroll=[0,0]
        self.center = center

    def update_scroll(self,shake):
        if shake>0:#inprinciple we do not need this if
            screen_shake=[random.randint(-shake,shake),random.randint(-shake,shake)]
        else:
            screen_shake=[0,0]

        self.scroll=self.true_scroll.copy()
        self.scroll[0]=int(self.scroll[0])+screen_shake[0]
        self.scroll[1]=int(self.scroll[1])+screen_shake[1]

class Auto(Camera):
    def __init__(self, center):
        super().__init__(center)

    def scrolling(self,knight,shake):
        self.true_scroll[0]+=(knight.center[0]-8*self.true_scroll[0]-self.center[0])/15
        self.true_scroll[1]+=(knight.center[1]-self.true_scroll[1]-self.center[1])
        self.update_scroll(shake)

class Auto_CapX(Camera):
    def __init__(self, center):
        super().__init__(center)

    def scrolling(self,knight,shake):
        self.true_scroll[1]+=(knight.center[1]-self.true_scroll[1]-self.center[1])
        self.update_scroll(shake)

class Auto_CapY(Camera):
    def __init__(self, center):
        super().__init__(center)

    def scrolling(self,knight,shake):
        self.true_scroll[0]+=(knight.center[0]-8*self.true_scroll[0]-self.center[0])/15
        self.update_scroll(shake)

class Fixed(Camera):
    def __init__(self):
        super().__init__()

    def scrolling(self,knight,shake):
        self.update_scroll(shake)

class Autocap(Camera):
    def __init__(self):
        super().__init__()

    def scrolling(self,knight,distance,shake):
        if knight.center[0]>400:
            self.true_scroll[0]+=5
        elif knight.center[0]<30:
            self.true_scroll[0]-=5
        elif knight.center[0]>150 and knight.center[0]<220:
            self.true_scroll[0]=0

        if knight.center[1]>200:
            self.true_scroll[1]+=0.5
        elif knight.center[1]<70:
            self.true_scroll[1]-=0.5
        elif knight.center[1]>130 and knight.center[1]<190:
            self.true_scroll[1]=0

        self.update_scroll(shake)

class Border(Camera):
    def __init__(self):
        super().__init__()

    def scrolling(self,knight,total_distance,shake):
        self.true_scroll[1]+=(knight.center[1]-self.true_scroll[1]-180)
        if -40 < total_distance[0]<1400:#map boundaries
            self.true_scroll[0]+=(knight.center[0]-4*self.true_scroll[0]-240)/20
        else:
            if knight.center[0]<60:
                self.true_scroll[0]-=1
            elif knight.center[0]>440:
                self.true_scroll[0]+=1
            else:
                self.true_scroll[0]=0
        self.update_scroll(shake)

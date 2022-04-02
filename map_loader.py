import pygame, csv, Entities, math, random, Read_files

class Level():
    def __init__(self, level, game_objects, spawn):
        self.PLAYER_CENTER = game_objects.player_center
        self.SCREEN_SIZE = game_objects.game.WINDOW_SIZE
        self.TILE_SIZE = 16
        self.game_objects = game_objects
        self.level_name = level
        self.spawn = spawn
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

    def scrolling(self,player):
        self.camera.update(player)

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

        def convert_points_to_list(points):
            points_list = []
            for point in points:
                points_list.append((point['x'],point['y']))
            return points_list

        for obj in map_collisions:

            object_position = (int(obj['x']),int(obj['y']))
            object_size = (int(obj['width']),int(obj['height']))

            #check for polygon type first
            if 'polygon' in obj.keys():
                new_block = Entities.Collision_right_angle(object_position, convert_points_to_list(obj['polygon']))
                self.game_objects.platforms_ramps.add(new_block)
                continue

            id = obj['gid'] - (self.map_data['statics_firstgid'] + 6) #the last in depends on postion of COL stamp in stamp png
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
                for property in obj['properties']:
                    if property['name'] == 'spawn':
                        if property['value'] == self.spawn:
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
                self.game_objects.enemies.add(new_enemy(object_position, self.game_objects.eprojectiles, self.game_objects.loot))

            elif id == 9:
                object_size = (int(obj['width']),int(obj['height']))
                for property in obj['properties']:
                    if property['name'] == 'path_to':
                        destination = property['value']
                    if property['name'] == 'spawn':
                        spawn = property['value']
                new_path = Entities.Path_col(object_position,object_size,destination,spawn)
                self.game_objects.triggers.add(new_path)
            elif id == 12:
                object_size = (int(obj['width']),int(obj['height']))
                new_camera_stop = Entities.Camera_Stop(object_size, object_position, 'right')
                self.game_objects.camera_blocks.add(new_camera_stop)
            elif id == 13:
                object_size = (int(obj['width']),int(obj['height']))
                new_camera_stop = Entities.Camera_Stop(object_size, object_position, 'top')
                self.game_objects.camera_blocks.add(new_camera_stop)
            elif id == 14:
                object_size = (int(obj['width']),int(obj['height']))
                new_camera_stop = Entities.Camera_Stop(object_size, object_position, 'left')
                self.game_objects.camera_blocks.add(new_camera_stop)
            elif id == 15:
                object_size = (int(obj['width']),int(obj['height']))
                new_camera_stop = Entities.Camera_Stop(object_size, object_position, 'bottom')
                self.game_objects.camera_blocks.add(new_camera_stop)


    #TODO: Make sure all FG layers are added to all_fgs!!
    def load_bg(self):
    #returns one surface with all backround images blitted onto it, for each bg/fg layer
        base_bg_list = ['bg_behindfar','bg_far','bg_behindmid','bg_mid','bg_behindnear','bg_near','bg_fixed','fg_fixed','fg_near','fg_mid']
        #bg_list = ['bg_farfar','bg_far','bg_midmid','bg_mid','bg_nearnear','bg_near','bg_fixed','fg_fixed','fg_near','fg_mid']
        bg_list = []
        parallax_values = {'bg_behindfar': 0.01,
                            'bg_far': 0.03,
                            'bg_behindmid': 0.4,
                            'bg_mid': 0.5,
                            'bg_behindnear': 0.7,
                            'bg_near': 0.8,
                            'bg_fixed': 1,
                            'fg_fixed': 1,
                            'fg_near': 1.25,
                            'fg_mid': 1.5}
        animation_list = {}
        top_left = {}
        bg_flags = {}
        blit_dict = {}

        #check for animation and deco layers in map data
        for bg in base_bg_list:
            for layer in list(self.map_data['tile_layers'].keys()):
                if '_animated' in layer:
                    animation_base_layer = layer[:layer.find('_animated')]
                    animation_list[animation_base_layer] = layer
                elif bg in layer:
                    if bg in blit_dict.keys():
                        blit_dict[bg].append(layer)
                    else:
                        blit_dict[bg] = [layer]
                    bg_list.append(layer)


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
                        y = math.floor(index/cols)
                        x = (index - (y*cols))
                        blit_pos = (x * self.TILE_SIZE, y * self.TILE_SIZE)
                        blit_surfaces[bg].blit(spritesheet_dict[tile_number], blit_pos)
                        if top_left[bg] == (0,0):
                            top_left[bg] = blit_pos

        #blit all sublayers onto one single parallax layer in order
        for bg in list(blit_dict.keys()):
            if len(blit_dict[bg]) == 1:
                continue
            blit_dict[bg].sort(reverse = True)
            for i in range(1,len(blit_dict[bg])):
                blit_surfaces[blit_dict[bg][0]].blit(blit_surfaces[blit_dict[bg][i]],(0,0))

        animation_entities = {}
        #create animation layers
        for bg in animation_list.keys():
            for index, tile_number in enumerate(self.map_data['tile_layers'][animation_list[bg]]['data']):
                if tile_number == 0:
                    continue
                else:
                    for tileset in self.map_data['tilesets']:
                        if tile_number == tileset['firstgid']:
                            path = 'maps/%s/%s' % (self.level_name, Read_files.get_folder(tileset['image']))
                            y = math.floor(index/cols)
                            x = (index - (y*cols))
                            parallax = parallax_values[bg]
                            print(new_map_diff[0], ' ', x)
                            #blit_pos = (x * self.TILE_SIZE -int((1-parallax)*new_map_diff[0]), y * self.TILE_SIZE - int((1-parallax)*new_map_diff[1]))
                            blit_pos = (x * self.TILE_SIZE -int((1-parallax)*new_map_diff[0]) + int((self.init_player_pos[0]-x*self.TILE_SIZE)*(1-parallax)), y * self.TILE_SIZE - int((1-parallax)*new_map_diff[1]) + int((self.init_player_pos[1]-y*self.TILE_SIZE)*(1-parallax)))
                            new_animation = Entities.BG_Animated(blit_pos,path,parallax)
                            try:
                                animation_entities[bg].append(new_animation)
                            except KeyError:
                                animation_entities[bg] = [new_animation]


        for bg in base_bg_list:
            parallax = parallax_values[bg]

            if bg in blit_dict.keys():
                if 'fg' in bg:
                    self.game_objects.all_fgs.add(Entities.BG_Block((int((1-parallax)*new_map_diff[0]),int((1-parallax)*new_map_diff[1])),blit_surfaces[blit_dict[bg][0]],parallax))
                else:
                    pos=(-math.ceil((1-parallax)*new_map_diff[0]),-math.ceil((1-parallax)*new_map_diff[1]))
                    self.game_objects.all_bgs.add(Entities.BG_Block(pos,blit_surfaces[blit_dict[bg][0]],parallax))#pos,img,parallax
            try:
                for bg_animation in animation_entities[bg]:
                    self.game_objects.all_bgs.add(bg_animation)
            except KeyError:
                pass
        del blit_surfaces, bg_sheets, bg_maps

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

    def update(self):
        #if shake>0:#inprinciple we do not need this if
        #    screen_shake=[random.randint(-shake,shake),random.randint(-shake,shake)]
        #else:
        #    screen_shake=[0,0]
        screen_shake=[0,0]

        self.scroll=self.true_scroll.copy()
        self.scroll[0]=int(self.scroll[0])+screen_shake[0]
        self.scroll[1]=int(self.scroll[1])+screen_shake[1]

class Auto(Camera):
    def __init__(self, center):
        super().__init__(center)

    def update(self,player):
        self.true_scroll[0]+=(player.center[0]-8*self.true_scroll[0]-self.center[0])/15
        self.true_scroll[1]+=(player.center[1]-self.true_scroll[1]-self.center[1])
        super().update()

class Auto_CapX(Camera):
    def __init__(self, center):
        super().__init__(center)

    def update(self,player):
        self.true_scroll[1]+=(player.center[1]-self.true_scroll[1]-self.center[1])
        super().update()

class Auto_CapY(Camera):
    def __init__(self, center):
        super().__init__(center)

    def update(self,player):
        self.true_scroll[0]+=(player.center[0]-8*self.true_scroll[0]-self.center[0])/15
        super().update()

class Fixed(Camera):
    def __init__(self):
        super().__init__()

    def update(self,player):
        super().update()

class Autocap(Camera):
    def __init__(self):
        super().__init__()

    def update(self,player,distance):
        if player.center[0]>400:
            self.true_scroll[0]+=5
        elif player.center[0]<30:
            self.true_scroll[0]-=5
        elif player.center[0]>150 and player.center[0]<220:
            self.true_scroll[0]=0

        if player.center[1]>200:
            self.true_scroll[1]+=0.5
        elif player.center[1]<70:
            self.true_scroll[1]-=0.5
        elif player.center[1]>130 and player.center[1]<190:
            self.true_scroll[1]=0

        super().update()

class Border(Camera):
    def __init__(self):
        super().__init__()

    def update(self,player,total_distance):
        self.true_scroll[1]+=(player.center[1]-self.true_scroll[1]-180)
        if -40 < total_distance[0]<1400:#map boundaries
            self.true_scroll[0]+=(player.center[0]-4*self.true_scroll[0]-240)/20
        else:
            if player.center[0]<60:
                self.true_scroll[0]-=1
            elif player.center[0]>440:
                self.true_scroll[0]+=1
            else:
                self.true_scroll[0]=0
        super().update()

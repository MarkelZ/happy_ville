import pygame
from os import listdir, walk
from os.path import isfile, join

#sprires and fonts

class Sprites():
    #use for animation sprites
    def __init__(self):
        # Add lists for each sprite animation here, in sub classes
        pass

    def load_all_sprites(self,base_path):
        #loads all sprites in all sub directories in base_path, stores list of sprites with keys corresponding to folder name

        sprite_dict = {}
        for subdir in [d[0] for d in walk(base_path)]:
            if subdir == base_path:
                pass
            sprite_dict[subdir.split("/")[-1]] = self.load_sprites(subdir)

        return sprite_dict


    def load_sprites(self,path_to_folder):
        #use this to load multiple sprites in a path_to_folder

        list_of_sprites = [join(path_to_folder, f) for f in listdir(path_to_folder) if isfile(join(path_to_folder, f))]
        if join(path_to_folder,'.DS_Store') in list_of_sprites:
            list_of_sprites.remove(join(path_to_folder,'.DS_Store'))

        list_of_sprites.sort()
        return [pygame.image.load(file) for file in list_of_sprites]

    def load_single_sprite(self,path_to_sprite):
        #use to load single sprite, full path must be provided

        return pygame.image.load(path_to_sprite)

    def generic_sheet_reader(self, path_to_sheet, w, h, r, c):
    #width, height, no o sprites in row, no o sprites in column
    #loads all sprites from a sheet,
    #this method requires all sprites to have the same dimension in the sheet
        sprite_dict = {}
        sheet = pygame.image.load(path_to_sheet).convert_alpha()
        sprite_size = (w,h) #[width, height] of sprite in sheet
        sprite_count = [r,c] # nomber of sprites per [row,column]
        n = 0

        for i in range(sprite_count[0]):
            for j in range(sprite_count[1]):
                rect = pygame.Rect(j*sprite_size[0], i*sprite_size[1], j*sprite_size[0] + sprite_size[0], i*sprite_size[1] + sprite_size[1])
                image = pygame.Surface(sprite_size,pygame.SRCALPHA,32)
                image.blit(sheet,(0,0),rect)
                sprite_dict[n] = image
                n+=1

        return sprite_dict

#class containing sprites for player
class Sprites_player(Sprites):

    player_path = "Sprites/player/"
    def __init__(self):
        super().__init__()
        self.sprite_dict = self.load_all_sprites(self.player_path)

    def get_image(self, input, timer, dir):
        if input=='sword' and dir[1]>0:
            input=input+'_up'
        elif input=='sword' and dir[1]<0:
            input=input+'_down'

        if dir[0] >= 0:
            return self.sprite_dict[input][timer]
        elif dir[0] < 0:
            return pygame.transform.flip(self.sprite_dict[input][timer],True,False)

    def get_frame_number(self, input,dir):
        if input=='sword' and dir[1]>0:
            input=input+'_up'
        elif input=='sword' and dir[1]<0:
            input=input+'_down'

        return len(self.sprite_dict[input])

class NPC(Sprites):

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.sprite_dict = self.load_all_sprites("Sprites/NPC/" + name + "/")

    def get_image(self, input, timer,dir):

        if dir[0] < 0:
            return self.sprite_dict[input][timer]
        elif dir[0] >= 0:
            return pygame.transform.flip(self.sprite_dict[input][timer],True,False)

    def get_frame_number(self, input,dir):

        return len(self.sprite_dict[input])

class Sprites_evil_knight(Sprites):

    player_path = "Sprites/player/"
    def __init__(self):
        super().__init__()
        self.sprite_dict = self.load_all_sprites(self.player_path)

    def get_image(self, input, timer, dir):
        if dir[0] >= 0:
            return self.sprite_dict[input][timer]
        elif dir[0] < 0:
            return pygame.transformation.flip(self.sprite_dict[input][timer], True, False)

class Chest(Sprites):

    def __init__(self):
        super().__init__()
        self.path = "Sprites/animations/chest.png"
        self.sprites = self.generic_sheet_reader(self.path,16,21,1,3)

    def get_sprites(self):
        return self.sprites

class Hearts(Sprites):

    def __init__(self):
        super().__init__()
        self.path = "Sprites/hearts.png"
        self.sprites = self.generic_sheet_reader(self.path,7,6,2,2)

    def get_sprites(self):
        return self.sprites

class Hearts_Black(Sprites):

    def __init__(self):
        super().__init__()
        self.path = "Sprites/hearts_black.png"
        self.sprites = self.generic_sheet_reader(self.path,9,8,2,3)

    def get_sprites(self):
        return self.sprites

#reading fonts
class Alphabet():#scale needs to be larger than one, for reasons
    def __init__(self, path,scale=1):
        self.spacing=1
        self.scale=scale
        self.letter_height=16*self.scale
        self.character_order=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        sheet=pygame.image.load(path).convert()
        self.characters={}
        current_char_width=0
        character_count=0

        for x in range(sheet.get_width()):
            c=sheet.get_at((x,0))

            if character_count>=len(self.character_order):
                break
            else:
                if c[0]==238:#check for red color
                    char_img=Alphabet.clip(sheet,x-current_char_width,0, current_char_width,self.letter_height)
                    self.characters[self.character_order[character_count]]=char_img.copy()
                    character_count+=1
                    current_char_width=0
                else:
                    current_char_width+=1
        self.space_width=self.characters['A'].get_width()*self.scale

    def render(self,screen,text,loc):
        x_offset=0
        y_offset=0
        for char in text:
            if char!=' ' and char!='\n' and char!='*':
                scaled_letter=pygame.transform.scale(self.characters[char], (int(self.scale*self.characters[char].get_width()), int(self.scale*self.letter_height)))
                screen.blit(scaled_letter,(loc[0]+x_offset,loc[1]+y_offset))
                x_offset+=self.characters[char].get_width()+self.spacing
            elif char=='*':#new line
                x_offset=0
                y_offset+=self.letter_height
            else:#spacing
                x_offset+=self.space_width+self.spacing

    @staticmethod
    def clip(surf,x,y,x_size,y_size):
        handle_surf=surf.copy()
        clipR=pygame.Rect(x,y,x_size,y_size)
        handle_surf.set_clip(clipR)
        image=surf.subsurface(handle_surf.get_clip())
        return image.copy()

class Conversations():#Make a dictinoary of conversations available
    def __init__(self, path):
        f = open(path, "r")
        contents=f.readlines()
        f.close()

        number_of_worldstates=2
        w, h = 1, number_of_worldstates;
        Matrix = [[0 for x in range(w)] for y in range(h)]#place hodlers

        text={}#place holder
        i=0
        j=1
        for line in contents:
            if line=='\n':#skip these
                continue
            elif line == 'worldstate_'+str(j)+'\n':
                j+=1

            Matrix[j-2].append(line)
            i+=1
        for i in range(0,len(Matrix)):
            Matrix[i]=Matrix[i][2:]#remove the first 0 and world state from list

        #make a dictinoary
        for key in range(0,number_of_worldstates):
            text[key]=Matrix[key]

        self.text=text

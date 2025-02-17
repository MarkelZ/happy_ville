import pygame

class Shader_layered_group(pygame.sprite.LayeredUpdates):
    def __init__(self):
        super().__init__()
        self.surface = pygame.Surface([640,360], pygame.SRCALPHA, 32)

    def draw(self, screen):
        for s in self.sprites():
            surface = self.surface.copy()#make an empty surface

            surface.blit(s.image, s.rect.topleft)#blit the rellavant portion onto it
            #newrect = surface.blit(s.image, s.rect)
            s.shader.render(surface)#blit the rellacvant portion onto display via OPENGL framework

class Shader_group(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def draw(self,screen):
        for s in self.sprites():
            s.shader.render(s.image)

class Specialdraw_Group(pygame.sprite.Group):#a group for the reflection object which need a special draw method
    def __init__(self):
        super().__init__()

    def draw(self):
        for s in self.sprites():
            s.draw()

class Group_player(pygame.sprite.Group):#a group for the reflection object which need a special draw method
    def __init__(self,game_objects):
        super().__init__()
        self.game_objects = game_objects

    def draw(self,surface):
        for spr in self.sprites():
            self.spritedict[spr] = surface.blit(spr.image, (round(spr.true_pos[0]-self.game_objects.camera.true_scroll[0]),round(spr.true_pos[1]-self.game_objects.camera.true_scroll[1])))#round seem nicer than int

class Group(pygame.sprite.Group):
    def __init__(self,game_objects):
        super().__init__()
        self.game_objects = game_objects

    def draw(self,surface):
        for spr in self.sprites():
            self.spritedict[spr] = surface.blit(spr.image, (int(spr.rect[0]-self.game_objects.camera.scroll[0]),int(spr.rect[1]-self.game_objects.camera.scroll[1])))#int seem nicer than round

class LayeredUpdates(pygame.sprite.LayeredUpdates):#a group for the reflection object which need a special draw method
    def __init__(self,game_objects):
        super().__init__()
        self.game_objects = game_objects

    def draw(self,surface):
        for spr in self.sprites():
            newrect = surface.blit(spr.image, (int(spr.true_pos[0]-spr.parallax[0]*self.game_objects.camera.scroll[0]),int(spr.true_pos[1]-spr.parallax[0]*self.game_objects.camera.scroll[1])))#int seem nicer than round

class PauseLayer(pygame.sprite.Group):#the pause group when parallax objects are outside the boundaries
    def __init__(self):
        super().__init__()

    def update(self):
        for s in self.sprites():
            self.group_distance(s)

    @staticmethod
    def group_distance(s):
        if s.true_pos[0]-s.parallax[0]*s.game_objects.camera.scroll[0] < s.bounds[0] or s.true_pos[0]-s.parallax[0]*s.game_objects.camera.scroll[0] > s.bounds[1] or s.true_pos[1]-s.parallax[1]*s.game_objects.camera.scroll[1]<s.bounds[2] or s.true_pos[1]-s.parallax[1]*s.game_objects.camera.scroll[1]>s.bounds[3]: #or abs(entity.rect[1])>300:#this means it is outside of screen
            pass#s.update_pos(pos)
        else:#manually add to a specific layer
            sprites = s.game_objects.all_bgs.sprites()
            bg = s.game_objects.all_bgs.reference[tuple(s.parallax)]
            index = sprites.index(bg)#find the index in which the static layer is located

            s.game_objects.all_bgs.spritedict[s] = s.game_objects.all_bgs._init_rect#in add internal
            s.game_objects.all_bgs._spritelayers[s] = 0
            s.game_objects.all_bgs._spritelist.insert(index,s)#it goes behind the static layer of reference
            s.add_internal(s.game_objects.all_bgs)
            s.remove(s.pause_group)#remove from pause

class PauseGroup(pygame.sprite.Group):#the pause group when enteties are outside the boundaries
    def __init__(self):
        super().__init__()

    def update(self):
        for s in self.sprites():
            self.group_distance(s)

    @staticmethod
    def group_distance(s):
        if s.true_pos[0]-s.game_objects.camera.scroll[0] < s.bounds[0] or s.true_pos[0]-s.game_objects.camera.scroll[0] > s.bounds[1] or s.true_pos[1]-s.game_objects.camera.scroll[1]<s.bounds[2] or s.true_pos[1]-s.game_objects.camera.scroll[1]>s.bounds[3]: #or abs(entity.rect[1])>300:#this means it is outside of screen
            pass#s.update_pos(pos)
        else:
            s.add(s.group)#add to group
            s.remove(s.pause_group)#remove from pause

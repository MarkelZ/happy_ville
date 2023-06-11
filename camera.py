import random, sys, math

class Camera():
    def __init__(self,game_objects):
        self.game_objects = game_objects
        self.true_scroll = [0,0]
        self.scroll = [0,0]
        self.center = list(game_objects.map.PLAYER_CENTER)
        self.original_center = self.center.copy()

    def update(self):
        self.check_camera_border_new()#this need to be checked before the camera calculates the scroll
        #self.true_scroll[0] += (self.game_objects.player.rect.centerx - 8*self.true_scroll[0] - self.center[0])/15
        #self.true_scroll[1] += (self.game_objects.player.rect.centery - 8*self.true_scroll[1] - self.center[1])/15
        self.true_scroll[0] += (self.game_objects.player.true_pos[0] - 8*self.true_scroll[0] - self.center[0])/15
        self.true_scroll[1] += (self.game_objects.player.true_pos[1] - 8*self.true_scroll[1] - self.center[1])/15
        self.scroll = self.true_scroll.copy()

        #self.scroll[0] = int(self.scroll[0])
        #self.scroll[1] = int(self.scroll[1])
        print(self.true_scroll)
        if abs(self.scroll[0]) < 0.5:
            self.scroll[0] = 0
        if abs(self.scroll[1]) < 0.5:
            self.scroll[1] = 0


    def set_camera(self, camera):
        new_camera = getattr(sys.modules[__name__], camera)(self.game_objects)
        self.game_objects.camera = new_camera

    def camera_shake(self,amp=3,duration=100):
        self.game_objects.camera = Camera_shake(self.game_objects,amp,duration)

    def reset_player_center(self):
        self.center = self.original_center.copy()

    def check_camera_border_new(self):
        for block in self.game_objects.camera_blocks:
            block.currentstate.update()

class Camera_shake(Camera):
    def __init__(self, game_objects,amp,duration):
        super().__init__(game_objects)
        self.amp = amp
        self.duration = duration

    def camera_shake(self,amp=3,duration=100):
        pass

    def update(self):
        super().update()
        self.scroll[0] += random.randint(-self.amp,self.amp)
        self.scroll[1] += random.randint(-self.amp,self.amp)
        self.duration -= self.game_objects.game.dt
        self.exit_state()

    def exit_state(self):#go back to the cameera
        if self.duration < 0:
            self.set_camera('Camera')

#cutscene cameras
class Cutscenes(Camera):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.shaking = False

    def update(self):
        super().update()
        self.shakeit()

    def camera_shake(self,amp = 3, duration = 100):#if camera shake is called during a cutscene, set a flag so that it shakes
        self.shaking = True
        self.amp = amp
        self.duration = duration

    def shakeit(self):
        if not self.shaking: return
        self.duration -= self.game_objects.game.dt
        self.scroll[0] += random.randint(-self.amp,self.amp)
        self.scroll[1] += random.randint(-self.amp,self.amp)
        if self.duration < 0:
            self.shaking = False

    def exit_state(self):#called from cutscenes
        self.set_camera('Camera')

class Deer_encounter(Cutscenes):
    def __init__(self, game_objects):
        super().__init__(game_objects)

    def update(self):
        self.center[0] -= 5*self.game_objects.game.dt
        self.center[0] = max(200,self.center[0])
        super().update()

class Cultist_encounter(Cutscenes):
    def __init__(self, game_objects):
        super().__init__(game_objects)

    def update(self):
        self.center[0] += 2*self.game_objects.game.dt
        self.center[0] = min(500,self.center[0])
        super().update()

class New_game(Cutscenes):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.center[1] = 1000

    def update(self):
        self.center[1] -= 2*self.game_objects.game.dt
        self.center[1] = max(self.game_objects.map.PLAYER_CENTER[1],self.center[1])
        super().update()

class Title_screen(Cutscenes):
    def __init__(self, game_objects):
        super().__init__(game_objects)

    def update(self):
        self.center[1] += 2*self.game_objects.game.dt
        self.center[1] = min(1000,self.center[1])

        self.true_scroll[1]+=(self.game_objects.player.rect.center[1]-self.true_scroll[1]-self.center[1])
        self.check_camera_border_new()
        self.scroll=self.true_scroll.copy()
        self.scroll[1]=int(self.scroll[1])

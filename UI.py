import pygame, sys

class Game_UI():

    def __init__(self):
        pygame.init()#initilise
        self.WINDOW_SIZE = (480,270)
        self.scale = 1
        self.WINDOW_SIZE_scaled = tuple([int(x*self.scale) for x in self.WINDOW_SIZE])
        self.screen=pygame.Surface(self.WINDOW_SIZE)
        self.display = pygame.display.set_mode(self.WINDOW_SIZE_scaled, vsync = 1)
        self.start_BG=pygame.transform.scale(pygame.image.load('sprites/start_menu.jpg'),self.WINDOW_SIZE)
        self.clock=pygame.time.Clock()
        self.gameover=False
        self.ESC=False
        self.click=False
        self.font=pygame.font.Font('freesansbold.ttf',40)

    def start_menu(self):
        self.screen.blit(self.start_BG,(0,0))
        self.display.blit(pygame.transform.scale(self.screen,self.WINDOW_SIZE_scaled),(0,0))

        while self.ESC:

            start_surface=self.font.render('Start Game',True,(255,255,255))#antialias flag
            start_rect=start_surface.get_rect(center=(200,100))#position
            option_surface=self.font.render('Options',True,(255,255,255))#antialias flag
            option_rect=start_surface.get_rect(center=(200,200))#position
            exit_surface=self.font.render('Exit game',True,(255,255,255))#antialias flag
            exit_rect=start_surface.get_rect(center=(200,400))#position

            if start_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
                self.ESC=False#exhit the start menue
                self.click=False
            elif option_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
                self.click=False
                self.option=True
                self.option_menu()#go to option
            elif exit_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
                pygame.quit()
                sys.exit()

            self.screen.blit(start_surface,start_rect)
            self.screen.blit(option_surface,option_rect)
            self.screen.blit(exit_surface,exit_rect)
            Game_UI.input_quit(self)

    def option_menu(self):
        self.screen.blit(self.start_BG,(0,0))
        self.display.blit(pygame.transform.scale(self.screen,self.WINDOW_SIZE),(0,0))

        while self.option:

            Resolution_surface=self.font.render('Resoltion',True,(255,255,255))#antialias flag
            Resolution_rect=Resolution_surface.get_rect(center=(200,100))#position

            self.screen.blit(Resolution_surface,Resolution_rect)

            if Resolution_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
                self.click=False
                self.screen.blit(self.start_BG,(0,0))
                self.resolution=True
                self.resolution_menu()#go to resolution selections

            Game_UI.input_quit(self)

        self.ESC=True

    def resolution_menu(self):

        while self.resolution:

            Resolution_surface=self.font.render('1000x800',True,(255,255,255))#antialias flag
            Resolution_rect=Resolution_surface.get_rect(center=(200,100))#position

            self.screen.blit(Resolution_surface,Resolution_rect)

            if Resolution_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
                self.screen=pygame.display.set_mode((1000,800))
                self.start_BG=pygame.transform.scale(self.start_BG,(1000,800))#recale the BG
                self.screen.blit(self.start_BG,(0,0))
                self.resolution=False

            Game_UI.input_quit(self)

        self.option=True

    def input_quit(self):#to exits between option menues
        pygame.display.update()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                self.click=True
            if event.type==pygame.MOUSEBUTTONUP:
                self.click=False
            if event.type == pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:#escape button
                    self.screen.blit(self.start_BG,(0,0))
                    self.resolution=False
                    self.option=False
                    self.ESC=False

    def input(self,player_class):#input while playing
        #game input
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:#escape button
                    self.ESC=True
                    self.start_menu()

                if event.key == pygame.K_RIGHT:
                    player_class.action['run']=True
                    player_class.action['stand']=False
                    player_class.dir[0]=1

                if event.key == pygame.K_LEFT:
                    player_class.action['run']=True
                    player_class.action['stand']=False
                    player_class.dir[0]=-1

                if event.key == pygame.K_UP:#press up
                    player_class.dir[1]=1
                if event.key == pygame.K_DOWN:#press down
                    player_class.dir[1]=-1
                if event.key==pygame.K_SPACE and player_class.action['jump']==False:#jump
                    player_class.movement[1]=-11
                    player_class.action['jump']=True

                if event.key==pygame.K_f:
                    player_class.action['sword']=True


            elif event.type == pygame.KEYUP:#lift bottom
                if event.key == pygame.K_RIGHT and player_class.dir[0]>0:
                    player_class.action['stand']=True
                    player_class.action['run']=False

                if event.key == pygame.K_LEFT and player_class.dir[0]<0:
                    player_class.action['stand']=True
                    player_class.action['run']=False
                if event.key == pygame.K_UP:
                    player_class.dir[1]=0
                if event.key == pygame.K_DOWN:
                    player_class.dir[1]=0

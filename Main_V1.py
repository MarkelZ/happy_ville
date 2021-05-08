import pygame
import Engine
import Entities
import Level
import Action
import UI
import Sprites

platforms = pygame.sprite.Group()
hero = pygame.sprite.Group()
enemies = pygame.sprite.Group()

game=UI.Game_UI()#initilise the game

knight=Entities.Player([200,130])
hero.add(knight)

sprites = {'knight': Sprites.Sprites_player()}

map=Level.Tilemap()
map.define_chunks('./Tiled/Level1.csv')

#tePlatforms,teEnemies=map.load_tiles('./Tiled/Level1.csv')
#platforms.add(tePlatforms)#whole map
#enemies.add(teEnemies)#whole map

def draw():
    platforms.draw(game.screen)
    hero.draw(game.screen)
    enemies.draw(game.screen)

    game.display.blit(pygame.transform.scale(game.screen,game.WINDOW_SIZE_scaled),(0,0))

def scrolling():
    map.scrolling(knight.rect)

    platforms.update([-map.scroll[0],-map.scroll[1]])
    hero.update([-map.scroll[0],-map.scroll[1]])
    enemies.update([-map.scroll[0],-map.scroll[1]])

while True:
    game.screen.fill((255,255,255))#fill game.screen

    platforms,enemies=map.load_chunks()

    scrolling()

    game.input(knight)

    for entity in enemies.sprites():
        entity.AI(knight)#the enemy Ai movement, based on knight position

    Engine.Physics.movement(hero)
    Engine.Physics.movement(enemies)
    Engine.Collisions.check_collisions(hero,platforms)
    Engine.Collisions.check_collisions(enemies,platforms)
    Engine.Animation.set_img(hero,sprites['knight'])
    Engine.Animation.set_img(enemies,sprites['knight'])

    Action.f_action(hero,platforms,enemies,game.screen)#f_action swinger, target1,target2
    Action.f_action(enemies,platforms,hero,game.screen)#f_action swinger, target1,target2

    pygame.draw.rect(game.screen, (255,0,0), knight.rect,2)#checking hitbox
    pygame.draw.rect(game.screen, (0,255,0), knight.hitbox,2)#checking hitbox

    draw()
    pygame.display.update()#update after every change
    game.clock.tick(60)#limmit FPS

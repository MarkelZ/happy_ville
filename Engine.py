import pygame

class Collisions():
    def __init__(self):
        pass

    @staticmethod
    def check_collisions(dynamic_entties,platforms):
        collision_types=Collisions.collide(dynamic_entties,platforms)

        for entity in dynamic_entties.sprites():
            if collision_types['bottom']:
                entity.action['jump']=False
                if entity.dir[1]<0:#if on ground, cancel sword swing
                    entity.action['sword']=False
                    entity.frame = 0
            elif not collision_types['bottom']:
                entity.action['jump']=True
            if collision_types['top']:#knock back when hit head
                entity.movement[1]=1

    #collisions between enteties-groups: a dynamic and a static one
    @staticmethod
    def collide(dynamic_entties,static_enteties):
        collision_types = {'top':False,'bottom':False,'right':False,'left':False}

        #move in x every dynamic sprite
        for entity in dynamic_entties.sprites():
            entity.rect.center = [round(entity.rect.center[0] + entity.movement[0]), entity.rect.center[1] + 0]
            entity.hitbox.center = entity.rect.center#follow with hitbox

        collided=Collisions.collided#make the hitbox collide and not rect
        #check for collisions and get a dictionary of sprites that collides
        collisions=pygame.sprite.groupcollide(dynamic_entties,static_enteties,False,False,collided)
        for dyn_entity, stat_entity in collisions.items():
            if dyn_entity.movement[0]>0:#going to the right
                dyn_entity.hitbox.right = stat_entity[0].rect.left
                collision_types['right'] = True

            elif dyn_entity.movement[0]<0:#going to the left
                dyn_entity.hitbox.left = stat_entity[0].rect.right
                collision_types['left'] = True
            dyn_entity.rect.center=dyn_entity.hitbox.center

        #move in y every dynamic sprite
        for entity in dynamic_entties.sprites():
            entity.rect.center = [entity.rect.center[0], round(entity.rect.center[1] + entity.movement[1])]
            entity.hitbox.center = entity.rect.center#follow with hitbox

        collided=Collisions.collided#make the hitbox collide and not rect
        #check for collisions and get a dictionary of sprites that collides
        collisions=pygame.sprite.groupcollide(dynamic_entties,static_enteties,False,False,collided)
        for dyn_entity, stat_entity in collisions.items():
            if dyn_entity.movement[1]>0:#going down
                dyn_entity.hitbox.bottom = stat_entity[-1].rect.top
                collision_types['bottom'] = True

            elif dyn_entity.movement[1]<0:#going up
                dyn_entity.hitbox.top = stat_entity[-1].rect.bottom
                collision_types['top'] = True
            dyn_entity.rect.center=dyn_entity.hitbox.center

        return collision_types

    @staticmethod
    def collided(dynamic_entties,static_enteties):
        return dynamic_entties.hitbox.colliderect(static_enteties.rect)

class Physics():
    def __init__(self):
        pass

    @staticmethod
    def movement(dynamic_entties):
        for entity in dynamic_entties.sprites():

            entity.movement[1]+=entity.acceleration[1]#gravity
            if entity.movement[1]>7:#set a y max speed
                entity.movement[1]=7

            if entity.action['run'] and entity.dir[0]>0:#accelerate right
                entity.velocity[0]+=entity.acceleration[0]
                if entity.velocity[0]>10:#max speed
                    entity.velocity[0]=10
            elif entity.action['run'] and entity.dir[0]<0:#accelerate left
                entity.velocity[0]+=-entity.acceleration[0]
                if entity.velocity[0]<-10:#max speed
                    entity.velocity[0]=-10

            entity.velocity[0]=entity.velocity[0]-entity.friction*entity.velocity[0]#friction
            entity.movement[0]=entity.velocity[0]#set the horizontal velocity

class Animation():
    def __init__(self):
        #super().__init__()
        pass

    ### FIX frame rate thingy
    @staticmethod
    def set_img(enteties,sprite_img):

        for entity in enteties.sprites():#go through the group

            for action in entity.prioriy_list:
                if entity.action[action]:
                    if action != entity.state:
                        entity.state = action
                        entity.reset_timer()

                    entity.image = sprite_img.get_image(action,entity.frame//3,entity.dir[0])
                    entity.frame += 1

                    if entity.frame == sprite_img.get_frame_number(action,entity.dir[0])*3:
                        if action == 'death':
                            entity.kill()
                        else:
                            entity.reset_timer()
                            if action != 'run':
                                entity.action[action] = False
                    break
                else:
                    pass

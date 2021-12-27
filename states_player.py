import sys, pygame
from states_entity import Entity_States

class Player_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        super().update()
        self.increase_spirit()


    def enter_state(self,newstate):
        self.entity.currentstate=getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def increase_spirit(self):
        self.entity.spirit += 0.1
        self.entity.spirit=min(self.entity.max_spirit,self.entity.spirit)

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
        elif self.phase=='main':
            self.phase=self.phases[-1]
        elif self.phase=='post':
            self.phase='pre'

class Idle(Player_states):#this object will never pop
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]

    def update_state(self):
        if not self.entity.collision_types['bottom']:
            self.enter_state('Fall_stand')

    def change_state(self,input):
        if input[0]:
            if input[-1]=='a':
                self.enter_state('Jump_stand')
            elif input[-1]=='left':
                self.entity.dir[0] = -1
                self.enter_state('Walk')
            elif input[-1]=='right':
                self.entity.dir[0] = 1
                self.enter_state('Walk')
            elif input[-1]=='lb':
                self.enter_state('Dash')
            elif input[-1]=='x':
                self.enter_state('Sword_stand')
            elif input[-1]=='b' and input[0]:
                #statename=str(type(self.entity.ability).__name__)
                self.enter_state(self.entity.equip)

    def horizontal_velocity(self):
        pass

class Walk(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]

    def update_state(self):
        if not self.entity.collision_types['bottom']:
            self.enter_state('Fall_run')

    def change_state(self,input):
        if input[0]:#press
            if input[-1]=='a':
                self.enter_state('Jump_run')
            elif input[-1]=='lb':
                self.enter_state('Dash')
            elif input[-1]=='x':
                self.enter_state('Sword_run')
        elif input[1]:#release
            if ((input[-1] == 'right' and self.entity.dir[0] == 1) or (input[-1] == 'left' and self.entity.dir[0] == -1)):
                self.enter_state('Idle')

class Jump_run(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.velocity[1] = -11
        self.phases=['pre','main']
        self.phase=self.phases[0]

    def update_state(self):
        if self.entity.velocity[1]>0:
            self.enter_state('Fall_run')

    def change_state(self,input):
        if input[-1]=='lb':
            self.enter_state('Dash')
        elif input[-1]=='x':
            self.enter_state('Sword_run')
        elif input[-1]=='left' and input[0]:
            self.entity.dir[0] = -1
        elif input[-1]=='right' and input[0]:
            self.entity.dir[0] = 1
        elif input[1] and input[-1] == 'right' or input[1] and input[-1] == 'left':
            self.enter_state('Jump_stand')

class Jump_stand(Jump_run):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        if self.entity.velocity[1]>0:
            self.enter_state('Fall_stand')

    def change_state(self,input):
        if input[-1]=='lb':
            self.enter_state('Dash')
        elif input[-1]=='x':
            self.enter_state('Sword_stand')
        elif input[-1]=='left':
            self.entity.dir[0] = -1
            self.enter_state('Jump_run')
        elif input[-1]=='right':
            self.entity.dir[0] = 1
            self.enter_state('Jump_run')

#        elif input[-1]=='left' or input[-1]=='right':
#            self.enter_state('Jump_run')

    def horizontal_velocity(self):
        pass

class Fall_run(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','main']
        self.phase=self.phases[0]

    def update_state(self):
        if self.entity.collision_types['bottom']:
            self.enter_state('Walk')
        elif self.entity.collision_types['right'] or self.entity.collision_types['left']:#on wall and not on ground
            self.enter_state('Wall')

    def change_state(self,input):
        if input[1] and input[-1] == 'right' or input[1] and input[-1] == 'left':
            self.enter_state('Fall_stand')

class Fall_stand(Fall_run):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        if self.entity.collision_types['bottom']:
            self.enter_state('Idle')
        elif self.entity.collision_types['right'] or self.entity.collision_types['left']:#on wall and not on ground
            self.enter_state('Wall')

    def change_state(self,input):
        if input[0]:#press
            if input[-1]=='left':
                self.entity.dir[0] = -1
                self.enter_state('Fall_run')
            elif input[-1]=='right':
                self.entity.dir[0] = 1
                self.enter_state('Fall_run')

    def horizontal_velocity(self):
        pass

class Wall(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()
        self.phases=['pre','main']
        self.phase=self.phases[0]
        self.entity.friction[1]=0.4
        self.walk=True

    def update_state(self):
        if self.entity.collision_types['bottom']:
            self.entity.friction[1]=0
            self.enter_state('Idle')

        elif not self.entity.collision_types['right'] and not self.entity.collision_types['left']:#non wall and not on ground
            self.entity.friction[1]=0
            if self.walk:
                self.enter_state('Fall_run')
            else:
                self.enter_state('Fall_stand')

    def change_state(self,input):
        if input[0]:
            if input[-1]=='a':
                self.entity.friction[1]=0
                self.enter_state('Jump_run')
            elif input[-1] == 'right' and self.entity.dir[0]==-1 or input[-1] == 'left' and self.entity.dir[0]==1:
                self.entity.dir[0]=-1*self.entity.dir[0]
                self.entity.friction[1]=0
                self.entity.velocity[0]=0
                self.enter_state('Fall_run')
        elif input[1]:
            if input[-1]=='right' or input[-1]=='left':
                self.walk=False

class Dash(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()
        self.phases=['pre','main','post']
        self.phase=self.phases[0]
        self.entity.spirit -= 10
        self.done=False#animation flag
        self.walking()#check if we were walking are idle before dash
        self.entity.velocity[0] = 30*self.dir[0]

    def walking(self):
        if abs(self.entity.velocity[0])>0.5:
            self.walk=True
        else:
            self.walk=False

    def update_state(self):
        self.entity.velocity[1]=0
        self.entity.velocity[0]=self.dir[0]*max(10,abs(self.entity.velocity[0]))#max horizontal speed

        if self.done:
            if self.walk:
                self.enter_state('Walk')
            else:
                self.enter_state('Idle')

        elif self.entity.collision_types['right'] or self.entity.collision_types['left']:
            self.enter_state('Wall')

    def change_state(self,input):
        if input[0]:#press
            if input[-1] == 'right' and self.entity.dir[0]==1 or input[-1] == 'left' and self.entity.dir[0]==-1:
                self.walk=True
        elif input[1]:#release
            if input[-1] == 'right' and self.entity.dir[0]==1 or input[-1] == 'left' and self.entity.dir[0]==-1:
                self.walk=False

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
        elif self.phase=='main':
            self.phase=self.phases[-1]
        elif self.phase=='post':
            self.done=True

class Death(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.phase='main'
        self.done=False

    def update_state(self):
        if self.done:
            #self.entity.loot()
            self.entity.kill()

    def increase_phase(self):
        self.done=True

    def horizontal_velocity(self):
        pass

class Hurt(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.phase='main'
        self.done=False

    def update_state(self):
        if self.done:
            self.enter_state('Idle')

    def increase_phase(self):
        self.done=True

    def horizontal_velocity(self):
        pass

class Sword(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.sword1=False#flag to check if we shoudl go to next sword attack
        self.done=False#animation flag
        self.sword2=False#flag to check if we shoudl go to third sword attack
        self.dir=self.entity.dir.copy()#animation direction
        self.entity.sword.dir=self.dir#sword direction

    def increase_phase(self):
        if self.phase==self.phases[-1]:
            self.done=True
        elif self.phase=='pre':
            self.entity.projectiles.add(self.entity.sword)#add sword to group but in main phase

        super().increase_phase()

class Sword_run(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]
        self.entity.sword.lifetime=10#swrod hitbox duration
        self.entity.projectiles.add(self.entity.sword)#add sword to group

    def update_state(self):
        if self.done and self.sword1:
            self.enter_state('Sword1_stand')
        elif self.done:
            self.enter_state('Walk')

    def change_state(self,input):
        if input[-1]=='x' and input[0]:
            self.sword1=True
        elif input[-1]=='left' and input[1] or input[-1]=='right' and input[1]:#if release left or right
            self.enter_state('Sword_stand')

class Sword_stand(Sword_run):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        if self.done and self.sword1:
            self.enter_state('Sword1_stand')
        elif self.done:#if animation is done
            self.enter_state('Idle')

    def horizontal_velocity(self):
        pass

class Sword1_stand(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','main']
        self.phase=self.phases[0]
        self.entity.sword.lifetime=15#swrod hitbox duration

    def update_state(self):
    #    self.update_hitbox()
        if self.done and self.sword2:
            self.enter_state('Sword2_stand')
        elif self.done:#if animation is done
            self.enter_state('Idle')

    def change_state(self,input):
        if input[-1]=='x' and input[0]:
            self.sword2=True

    def horizontal_velocity(self):
        pass

class Abillitites(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.done=False#animation flag
        self.dir=self.entity.dir.copy()#animation direction

        abilityname=str(type(self).__name__)
        self.entity.ability=self.entity.abilities[abilityname](self.entity)#make the ability object
        self.entity.ability.dir=self.dir#sword direction

    def update_state(self):
        if self.done:
            self.enter_state('Idle')

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='charge'
        elif self.phase==self.phases[-1]:
            self.done=True
        elif self.phase=='main':
            self.phase='post'


    def horizontal_velocity(self):
        pass

class Hammer(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','charge','main']
        self.phase=self.phases[0]
        self.entity.spirit -= 10
        self.entity.ability.lifetime=7

    def change_state(self,input):
        if input[1]:#release
            if input[-1]=='b' and self.phase=='charge':#when release the botton
                self.phase='main'
                self.reset_timer()
                self.entity.projectiles.add(self.entity.ability)#add sword to group
            #else:#relasing during pre pahse
                #self.done=True

class Force(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','main']
        self.phase=self.phases[0]
        self.entity.spirit -= 10

        self.entity.ability.velocity[0]=10*self.dir[0]
        self.entity.ability.lifetime=30
        self.entity.ability.phase='pre'
        self.entity.ability.update_hitbox()

    def change_state(self,input):
        if input[1]:
            if input[-1]=='b' and self.phase=='charge':#when release the botton
                self.phase='main'
                self.reset_timer()
                self.entity.projectiles.add(self.entity.ability)#add sword to group
            else:#relasing during pre pahse
                self.done=True

class Shield(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','charge','main']
        self.phase=self.phases[0]
        self.entity.spirit -= 10

        self.entity.ability.lifetime=100#need to be changed depending on the animation of sword of player
        self.entity.ability.health=200

    def change_state(self,input):
        if input[1]:
            if input[-1]=='b' and self.phase=='charge':#when release the botton
                self.phase='main'
                self.reset_timer()
                self.entity.projectiles.add(self.entity.ability)#add sword to group
            else:#relasing during pre pahse
                self.done=True

class Heal(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','main']
        self.phase=self.phases[0]

    def heal(self):
        self.entity.spirit-=20
        self.entity.health+=20

    def change_state(self,input):
        if input[1]:
            self.done=True

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
        elif self.phase=='main':
            self.heal()
            self.done=True

class Stone(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['pre','charge','main','post']
        self.phase=self.phases[0]

        self.entity.spirit -= 10

        self.entity.ability.phase='pre'
        self.entity.ability.action='small'
        self.entity.ability.lifetime=100
        self.entity.ability.velocity=[0,0]
        self.entity.ability.update_hitbox()
        self.entity.projectiles.add(self.entity.ability)#add sword to group

    def change_state(self,input):
        if input[1]:
            if input[-1]=='b' and self.phase=='charge':#when release the botton
                self.phase='main'
                self.reset_timer()
                self.entity.ability.frame=0
                self.entity.ability.phase='main'
                self.entity.ability.velocity[0]=self.entity.ability.charge_velocity#set the velocity
            else:#relasing during pre pahse
                self.done=True
                self.entity.ability.frame=0
                self.entity.ability.phase='main'

import sys
from states_entity import Entity_States
#from Entities import Vatt

class Vatt_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases=['main']
        self.phase=self.phases[0]

    def enter_state(self,newstate):
        self.entity.currentstate=getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
        elif self.phase=='main':
            self.phase=self.phases[-1]
        elif self.phase=='post':
            self.done=True

    def change_state(self,input):
        self.enter_state(input)

class Idle(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def update_state(self):
        pass
    #    if not self.entity.collision_types['bottom']:
    #        self.enter_state('Fall_stand')

class Idle_aggro(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def update_state(self):
        pass
    #    if not self.entity.collision_types['bottom']:
    #        self.enter_state('Fall_stand')


class Walk(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()

    def update_state(self):
        pass
        #if not self.entity.collision_types['bottom']:
        #    self.enter_state('Fall_run')

class Fall_stand(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()

    def update_state(self):
        if self.entity.collision_types['bottom']:
            self.enter_state('Idle')

    def handle_input(self, input):
        if input=='Hurt' and not self.entity.aggro:
            self.enter_state('Hurt')

class Fall_stand_aggro(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.walk()

    def update_state(self):
        if self.entity.collision_types['bottom']:
            self.enter_state('Idle')

    def handle_input(self, input):
        if input=='Hurt' and not self.entity.aggro:
            self.enter_state('Hurt')

class Run(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.acceleration = [1.6,0.8]

    def update_state(self):
        pass

    def handle_input(self, input):
        if input == str(type(self).__name__):
            pass
        else:
            self.change_state(input)
        #if not self.entity.collision_types['bottom']:
        #    self.enter_state('Fall_run')

class Run_aggro(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.acceleration = [1.5,0.8]

    def update_state(self):
        pass

    def handle_input(self, input):
        if input == str(type(self).__name__):
            pass
        else:
            self.change_state(input)
        #if not self.entity.collision_types['bottom']:
        #    self.enter_state('Fall_run')

class Death(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False

    def update_state(self):
        if self.done:
            self.entity.loots()
            self.entity.kill()

    def increase_phase(self):
        self.done=True

    def change_state(self,input):
        pass

class Hurt(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False

    def update_state(self):
        if self.done:
            self.enter_state('Transform')

    def increase_phase(self):
        self.done=True

    def change_state(self,input):
        pass

class Hurt_aggro(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done=False

    def update_state(self):
        if self.done:
            self.enter_state('Idle')

    def increase_phase(self):
        self.done=True

    def change_state(self,input):
        pass

class Transform(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()
        self.done = False

    def update_state(self):
        pass

    def update_state(self):
        if self.done:
            type(self.entity).aggro = True
            #self.entity.set_aggro_animation()#go into aggro animaetion
            self.enter_state('Idle')


    def increase_phase(self):
        self.done=True

    def change_state(self,input):
        pass

    def handle_input(self, input):
        pass

class Stun(Vatt_states):
    def __init__(self,entity,duration):
        super().__init__(entity)
        self.stay_still()
        self.lifetime=duration

    def update_state(self):
        self.lifetime-=1
        if self.lifetime<0:
            self.enter_state('Idle')

    def change_state(self,input):
        pass

class Javelin(Vatt_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.phases = ['pre','main','post']
        self.phase = 'pre'
        self.entity.acceleration = [0,0]
        self.entity.velocity = [0,0]
        self.counter = 0
        self.done = False
        self.pre_pos_increment = [-3,-2,-1,-1,-1,-1]

    def update_state(self):
        if self.phase == 'pre':
            if int(self.counter/4) >= len(self.pre_pos_increment):
                pass
            elif self.counter%4 == 0:
                self.entity.update_pos((0,self.pre_pos_increment[int(self.counter/4)]))
        elif self.phase == 'main':
            if self.counter > 24:
                self.phase = 'post'
        elif self.done:
            self.enter_state('Fall_stand')
        self.counter += 1

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
            self.counter = 0
            self.entity.acceleration = [6,0]
        elif self.phase=='main':
            pass
        elif self.phase=='post':
            self.done=True


    def change_state(self,input):
        pass

    def handle_input(self, input):
        pass

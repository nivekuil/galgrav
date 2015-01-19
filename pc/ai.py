import pygame.locals
import events as ev

class AI(object):
    def __init__(self, evm, color, difficulty=2):
        self.evm = evm
        self.evm.register(self)
    
        self.color = color
    
        self.wait_counter = 0
    
        self.is_ai = True
        self.target_rect = pygame.Rect(0, 0, 300,250)
    
        #Tracks number of planets controlled in one wait cycle, so the AI
        #can't control every planet at once
        self.control_counter = 0
            
        if difficulty == 0:
            self.wait_cycle = 120
            self.value_until_shoot = 20
            self.can_control = 10
        elif difficulty == 1:
            self.wait_cycle = 90
            self.value_until_shoot = 15
            self.can_control = 10
        elif difficulty == 2:
            self.wait_cycle = 60
            self.value_until_shoot = 10
            self.can_control = 10
        elif difficulty == 3:
            self.wait_cycle = 40
            self.value_until_shoot = 10
            self.can_control = 10
        elif difficulty == 4:
            self.wait_cycle = 20
            self.value_until_shoot = 10
            self.can_control = 10
    
    def update(self):
        #Make sure we check if we reset the wait counter BEFORE we increment
        #the counter, so that the Model can know when the wait cycle ends
        if self.wait_counter > self.wait_cycle:
            self.wait_counter = 0
        self.wait_counter += 1
            
        #Reset the control counter so it can control planets again 
        self.control_counter = 0
    
    def process(self, planet, planet_list):
        pass
    
    def notify(self, evt):
        pass
        
class PeacefulAI(AI):
    def __init__(self, evm, color, difficulty=2):
        super(PeacefulAI, self).__init__(evm, color, difficulty)
    
    def process(self, planet, planet_list):
        self.control_counter += 1
        target_planets = []
    
        self.target_rect.center = planet.rect.center
            
        for p in planet_list:
            if p == planet:
                #Ignore the planet its being shot from as a potential target
                continue
            if self.target_rect.colliderect(p):
                target_planets.append(p)
    
        target_planets.sort(key=lambda x: x.value)
    
        #Go over the list of possible targets - if any of them have owners,
        #ignore them as targets for now.
        target_planet = None
    
        for t in target_planets:
            if t.owner:
                continue
            target_planet = t
            break
    
        #If every planet in range is owned, then shoot enemies or neutrals.
        if not target_planet:
            for t in target_planets:
                if t.owner != self and not t.shielded:
                    target_planet = t
                    break
    
        #Otherwise, just shoot at the strongest one.
        if not target_planet:
            target_planet = target_planets[-1]
                
        vect = planet.get_vector(target_planet.rect.center)
    
        self.evm.post(ev.ShootProjectile(planet, vect))
    
    def notify(self, evt):
        pass
        
class NormalAI(AI):
    def __init__(self, evm, color, difficulty=2):
        super(NormalAI, self).__init__(evm, color, difficulty)
    
    def process(self, planet, planet_list):
        self.control_counter += 1
        target_planets = []
    
        self.target_rect.center = planet.rect.center
            
        for p in planet_list:
            if p == planet:
                #Ignore the planet it's being shot as a potential target
                continue
            if self.target_rect.colliderect(p):
                target_planets.append(p)
    
        target_planets.sort(key=lambda x: x.value)
    
        target_planet = None
    
    
        #Prioritize enemies and neutrals.
        for t in target_planets:
            if t.owner != self and not t.shielded:
                target_planet = t
                break
    
        '''#If no enemies in range, prioritize neutrals
        if not target_planet:
            for t in target_planets:
                if t.owner:
                    continue
                target_planet = t
                break'''
    
        #Otherwise, just shoot at the strongest one.
        if not target_planet:
            target_planet = target_planets[-1]
                
        vect = planet.get_vector(target_planet.rect.center)
    
        self.evm.post(ev.ShootProjectile(planet, vect))
    
    def notify(self, evt):
        pass
    

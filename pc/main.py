from __future__ import division
  
#Neccesary for building the exe
#import pygame._view
  
try:
    import android
except ImportError:
    android = None
  
import sys
import math
from random import randint
  
import pygame.locals
import pygame.display
from pygame.sprite import collide_circle
try:
    import pygame.mixer as mixer
except ImportError:
    import android.mixer as mixer

import events as ev
import sprites as sp
import ai
import constants
  
  
  
class Planet:
    def __init__(self, evm, pos, radius):
        self.evm = evm
        self.evm.register(self)
          
        self.pos = pos
        self.radius = radius
        self.rect = pygame.Rect(pos, (radius*2, radius*2) )
          
        #Round down to the nearest tens
        self.max_value = (radius**2 // 10) - ((radius**2 // 10) % 10)
          
        self.production = 1 - self.max_value/200
        self.value = self.max_value // 2
        self.value_counter = 0
        self.value_color = (25,25,25)
  
        self.is_clicked = False
        self.is_dragged = False
  
        self.owner = None
          
        self.hotkey = None
        self.hotkey_name = None
        
        self.shield_frames = 0
        self.shielded = False
          
    def update(self):
        if self.shielded:
            self.shield_frames -= 1
            if self.shield_frames == 0:
                self.shielded = False

              
              
        if self.value < self.max_value:
            self.value_color = (25,25,25)
            self.value_counter += self.production
            if self.value_counter > 60:
                self.value += 1
                self.value_counter -= 60
                  
        elif self.value > self.max_value:
            self.value_color = (200,50,50)
            self.value_counter += (self.value/self.max_value)**1.5
            if self.value_counter > 80:
                self.value -= 1
                self.value_counter -= 80
            if self.value_counter > 80:
                self.value -= 1
                self.value_counter -= 80
  
        else:
            self.value_color = (255,255,255)
                                      
    def get_vector(self, p2):
        #It doesn't actually return a vector, but the x distance and y distance
        #from the planet's center to a point (the mouse pos) instead
        p1 = self.rect.center
          
        y = (p2[1] - p1[1])
        x = (p2[0] - p1[0])
            
        return x*0.04, y*0.04
      
    def mouseover(self, pos):
        #Determines if cursor is over planet
        x, y = pos
        center_x, center_y = self.rect.center
        return (x-center_x)**2 + (y - center_y)**2 < self.radius**2
          
  
    def clear_clicked(self):
        self.is_clicked = False
        self.is_dragged = False
  
    def shoot_projectile(self, vector):
  
        #This may leave the planet's value as a decimal if it was odd.
        #When the resulting projectile is initialized, it will take on
        #the rounded up value of the planet and leave the planet with
        #the floored value.
        self.value_counter = 0
          
        self.evm.post(ev.ShootProjectile(self, vector))
  
  
    def on_projectile_collided(self, proj):
        if self.owner == proj.owner:
            self.value += proj.value
        else:
            self.value -= proj.value
  
            if self.value < 0:
                self.owner = proj.owner
                self.value *= -1
                self.value_counter = 0
  
                self.shield_frames = 240
                self.shielded = True
                  
                self.evm.post(ev.UpdatePlanetColor(self))
          
  
    def notify(self, evt):
        if evt.id == 'LMBUP':
            if self.is_dragged and self.value > 0:
                vector = self.get_vector(evt.pos)
                self.shoot_projectile(vector)
            self.clear_clicked()
                  
        elif evt.id == 'LMBDOWN':
            if self.mouseover(evt.pos):
                self.is_clicked = True

        elif evt.id == 'RMBUP':
            self.clear_clicked()
  
  
  
  
class Projectile:
    def __init__(self, parent_planet, vector):
        self.parent_planet = parent_planet
        self.owner = parent_planet.owner
          
        self.radius = 8
        self.rect = pygame.Rect(0,0, 16,16)
        self.rect.center = parent_planet.rect.center
        self.pos = self.rect.topleft
  
        #The parent planet's value may a decimal. The projectile
        #takes on the rounded up value of the parent and leaves it
        #with the floored value.
        #self.value = int(math.ceil(parent_planet.value))
        #parent_planet.value = int(parent_planet.value) * 0.5
        self.value = parent_planet.value
        parent_planet.value = 0
  
        self.ax, self.ay = 0, 0
        self.dx, self.dy = vector
  
    def update(self):
        #Euler integration FTW! Nobody got the time for RK4.
        if self.ax > 0.1:
            self.ax = 0.1
        elif self.ax < -0.1:
            self.ax = -0.1
        if self.ay > 0.1:
            self.ay = 0.1
        elif self.ay < -0.1:
            self.ay = -0.1
  
        self.dx += self.ax
        self.dy += self.ay

        if self.dx ** 2 + self.dy ** 2 > 64:
            angle = math.atan2(self.dy, self.dx)
            self.dx = math.cos(angle) * 8
            self.dy = math.sin(angle) * 8
  
        self.pos = self.pos[0] + self.dx, self.pos[1] + self.dy        
  
        self.rect.topleft = self.pos
  
class EventManager:
    def __init__(self):
        self.event_queue = []
        self.listeners = []
          
    def register(self, listener):
        #Register object as a listener which must have a notify() function
        #to be called every pump()
        self.listeners.append(listener)
          
    def post(self, event):
        self.event_queue.append(event)
        if event.id == 'Tick':
            self.pump()
          
    def pump(self):
        #Cannot use "for evt in queue" because other events will be added
        #while the queue is being emptied
        i = 0
        while i < len(self.event_queue):
            evt = self.event_queue[i]
            i += 1            
            for listener in self.listeners:
                listener.notify(evt)
                  
        self.event_queue = []
  
class MediaManager:
    def __init__(self, evm):
        self.evm = evm
        self.evm.register(self)
        self.music_list = ['RoccoW_-_Weather.mp3']
          
        mixer.init()
  
        self.load_music()
          
        mixer.music.play(-1)
  
    def load_music(self):
        index = randint(0, len(self.music_list) - 1)
        mixer.music.load('data/music/'+self.music_list[index])
              
    def notify(self, evt):
        pass
          
class View:
    def __init__(self, evm):
        pygame.init()
          
        self.evm = evm
        self.evm.register(self)
          
  
        if android:
            info = pygame.display.Info()
            ratio = info.current_w / info.current_h
            width, height = ratio * 600, 600
            self.display = pygame.display.set_mode((int(width), height))
        else:
            width, height = 1024, 600
            self.display = pygame.display.set_mode((width, height))
		
        self.foreground = pygame.Surface((width, height),
                                         pygame.RLEACCEL).convert()
        self.foreground.set_colorkey((0,0,0))
  
        self.planet_sprites = []
        self.projectile_sprites = []
  
        self.planet_font = pygame.font.Font('data/fonts/Laconic_Bold.otf', 16)

        sp.load_base_sprites()
        bg = sp.load_background('background1.png')
        self.background_img = pygame.transform.smoothscale(bg, (1024, 600))
  
    def draw(self):
        selected_planets = []
        self.foreground.fill((0,0,0))

        self.display.blit(self.background_img, (0,0))
  
  
        for spr in self.projectile_sprites:
            self.display.blit(spr.image, spr.model.pos)
          
        for spr in self.planet_sprites:
            model = spr.model
  
            #If the planet is selected, we'll draw it after.
            if model.is_dragged:
                selected_planets.append(spr)
                continue
              
            text = str(int(model.value))
            x, y = self.planet_font.size(text)
            value_text = self.planet_font.render(text, True, model.value_color)
            value_pos = model.rect.centerx - x//2, model.rect.centery - y//2
  
  
            self.display.blit(spr.image, model.pos)
  
            if model.shielded:
                self.display.blit(spr.get_border(), model.pos)
  
            self.display.blit(value_text, value_pos)
            if model.hotkey_name:
                text = model.hotkey_name
                  
                hotkey_color = (150,150,150)
                hotkey_text = self.planet_font.render(text, True, hotkey_color)
                if model.radius > 25:
                    hotkey_pos = model.rect.right - 12, model.rect.bottom - 15
                else:
                    hotkey_pos = model.rect.right - 6, model.rect.bottom - 10
                self.foreground.blit(hotkey_text, hotkey_pos)
                  
        #Draw line, and then draw the selected planet to keep the planet
        #on top of the line but the line on top of the other planets
        mpos = pygame.mouse.get_pos()
        for spr in selected_planets:
              
            model = spr.model
            pygame.draw.line(self.display, (0,255,0), model.rect.center, mpos)
              
            text = str(int(model.value))
            x, y = self.planet_font.size(text)
            value_text = self.planet_font.render(text, True, model.value_color)
            value_pos = model.rect.centerx - x//2, model.rect.centery - y//2
  
  
            self.display.blit(spr.image, model.pos)
            if model.shielded:
                self.display.blit(spr.get_border(), model.pos)
                  
            self.display.blit(value_text, value_pos)
            if model.hotkey_name:
                text = model.hotkey_name
                  
                hotkey_color = (150,150,150)
                hotkey_text = self.planet_font.render(text, True, hotkey_color)
                if model.radius > 25:
                    hotkey_pos = model.rect.right - 12, model.rect.bottom - 15
                else:
                    hotkey_pos = model.rect.right - 6, model.rect.bottom - 10
                self.foreground.blit(hotkey_text, hotkey_pos)
                  
        self.display.blit(self.foreground, (0,0))
              
  
        pygame.display.flip()        
          
    def add_planet(self, model):
        self.planet_sprites.append(sp.Planet(model))
          
    def add_projectile(self, model):
        new_proj = sp.Projectile(model)
        new_proj.set_color(model.parent_planet.owner)
          
        self.projectile_sprites.append(new_proj)
  
        #Set a cap on the number of projectile sprites in existence. Remove
        #in first-in-first-out fashion
        if len(self.projectile_sprites) > 500:
            self.projectile_sprites.pop(0)
  
    def update_planet_color(self, model):
        #Updates the color of the planet when its owner changes
        for spr in self.planet_sprites:
            if spr.model == model:
                spr.set_color(model.owner)
      
    def clear(self):
        self.planet_sprites = []
        self.projectile_sprites = []
          
    def notify(self, evt):
        if evt.id == 'Tick':
            self.draw()
            return
        elif evt.id == 'PlanetCreated':
            self.add_planet(evt.model)
        elif evt.id == 'ProjectileCreated':
            self.add_projectile(evt.model)
        elif evt.id == 'UpdatePlanetColor':
            self.update_planet_color(evt.model)
  
        elif evt.id == 'ClearGame':
            self.clear()
  
      
class Controller:
    def __init__(self, evm):
        self.evm = evm
        self.evm.register(self)
                  
        self.fps_clock = pygame.time.Clock()
  
        if android:
            android.init()
            android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
            android.map_key(android.KEYCODE_MENU, pygame.K_SPACE)
    
    def tick(self):
        while 1:
            self.evm.post(ev.Tick())
              
    def update(self):
  
            if android:
                if android.check_pause():
                    android.wait_for_resume()
                      
            self.fps_clock.tick(60)
            mpos = pygame.mouse.get_pos()
  
              
              
            for evt in pygame.event.get():
                if evt.type == pygame.QUIT:
                    program_quit()
                      
                elif evt.type == pygame.MOUSEBUTTONDOWN:
                    if evt.button == 1:
                        self.evm.post(ev.LMBDOWN(mpos))
                      
                    if android:
                        self.evm.post(ev.MOUSEDRAG())
                          
                    if evt.button == 3:
                        self.evm.post(ev.RMBDOWN(mpos))
  
                elif evt.type == pygame.MOUSEBUTTONUP:
                    if evt.button == 1:
                        self.evm.post(ev.LMBUP(mpos))
                    elif evt.button == 3:
                        self.evm.post(ev.RMBUP(mpos))
  
                elif evt.type == pygame.MOUSEMOTION:
                    if pygame.mouse.get_pressed()[0]:
                        self.evm.post(ev.MOUSEDRAG(evt.pos))
                          
  
                elif evt.type == pygame.KEYDOWN:
                    if evt.key == pygame.K_ESCAPE:
                        program_quit()
                    elif evt.key == pygame.K_RETURN:
                        self.evm.post(ev.StartGame())
                    elif evt.key == pygame.K_SPACE:
                        self.evm.post(ev.ClearGame())
                        self.evm.post(ev.StartGame())
                          
                    if evt.key in constants.valid_hotkeys:
                        if not pygame.key.get_pressed()[pygame.K_LCTRL]:
                            self.evm.post(ev.SelectHotkey(evt.key))
                              
            #Check to set hotkeys every frame.
            if pygame.key.get_pressed()[pygame.K_LCTRL]:
                for key in constants.valid_hotkeys:
                    if pygame.key.get_pressed()[key]:
                        self.evm.post(ev.SetHotkey(mpos, key))
        
  
  
    def notify(self, evt):
        if evt.id == 'Tick':
            self.update()
  
class Player:
    def __init__(self, evm, color):
        self.evm = evm
        self.evm.register(self)
  
        self.color = color
  
        self.is_ai = False
  
    def update(self):
        pass
  
    def notify(self, evt):
        pass

  
class Model:
    def __init__(self, evm):
          
        self.evm = evm
        self.evm.register(self)
  
  
        self.planets = []
        self.projectiles = []
  
        player1 = Player(evm, (200,25,50))
        player2 = ai.NormalAI(evm, (0,0,255), difficulty=2)
        player3 = ai.PeacefulAI(evm, (0,255,0), difficulty=2)
        player4 = ai.PeacefulAI(evm, (150,150,0), difficulty=2)
          
        self.players = [player2, player1, player3, player4]
          
        self.active_player = player1
      
  
    def init_game(self):
        size = 1024,600
        self.field_rect = pygame.Rect((0,0), size)
        '''
        Desolate
        for x in xrange(9):
            for y in xrange(6):
                radius = randint(15, 30)
                pos = (randint(x*100, x*115+50),
                       randint(y*80, y*100+40))
                self.create_planet(pos, radius)'''
        '''
        Sparse'''
        for x in xrange(10):
            for y in xrange(7):
                radius = randint(15, 30)
                pos = (randint(x*95, x*100+50),
                       randint(y*65, y*90+20))
                self.create_planet(pos, radius)
        '''
        Average
        for x in xrange(11):
            for y in xrange(7):
                radius = randint(15, 35)
                pos = (randint(x*90, x*90+50),
                       randint(y*65, y*85+40))
                self.create_planet(pos, radius)'''
          
        '''
        Rich
        for x in xrange(12):
            for y in xrange(8):
                radius = randint(15, 30)
                pos = (randint(x*75, x*80+90),
                       randint(y*55, y*75+30))
                self.create_planet(pos, radius)'''
        '''
        Dense
        for x in xrange(13):
            for y in xrange(9):
                radius = randint(15, 30)
                pos = (randint(x*70, x*75+80),
                       randint(y*50, y*65+30))
                self.create_planet(pos, radius)'''
  
        self.planets[0].owner = self.players[0]
        self.planets[4].owner = self.players[2]
        self.planets[55].owner = self.players[3]
        self.planets[-1].owner = self.players[1]
          
        self.planets[0].value = 10+self.planets[0].radius//3
        self.planets[4].value = 10+self.planets[4].radius//3
        self.planets[55].value = 10+self.planets[55].radius//3
        self.planets[-1].value = 10+self.planets[-1].radius//3
  
        self.evm.post(ev.UpdatePlanetColor(self.planets[0]))
        self.evm.post(ev.UpdatePlanetColor(self.planets[4]))        
        self.evm.post(ev.UpdatePlanetColor(self.planets[55]))
        self.evm.post(ev.UpdatePlanetColor(self.planets[-1]))
  
  
    def create_planet(self, pos, radius):
        new_planet = Planet(self.evm, pos, radius)
        for planet in self.planets:
            if collide_circle(planet, new_planet):
                return
              
        self.planets.append(new_planet)
        self.evm.post(ev.PlanetCreated(new_planet))
  
    def create_projectile(self, parent_planet, vector):
        new_proj = Projectile(parent_planet, vector)
          
        self.projectiles.append(new_proj)
        self.evm.post(ev.ProjectileCreated(new_proj))
  
    def remove_projectile(self, proj):
        #Try-except block here, as projectiles can go way out of bounds and be
        #automatically garbage-collected without being properly disposed of.
        #Might implement an actual fix later.
  
        #It's worth noting that this only removes the projectile from the
        #Model; nothing is done to remove it from the View, so it keeps being
        #drawn despite having nothing
        try:
            self.projectiles.remove(proj)
        except:
            print proj.owner
  
      
    def select_planet(self):
        #Only allow one planet to be selected at a time, so if we already
        #find a selected planet, quit trying to select another one
        #This is to prevent selecting 2 planets with hotkey + drag
        for planet in self.planets:
            if planet.is_dragged:
                return
              
        #Now loop through the rest of the planets only if there isn't one
        #already selected
        for planet in self.planets:
            if planet.is_clicked:
                planet.is_dragged = True
                  
    def set_hotkey(self, pos, key):
        '''#First loop through all the planets and make sure the key is unassigned
        for planet in self.planets:
            if planet.hotkey == key:
                planet.hotkey = None
                planet.hotkey_name = None'''
  
        #Then loop through and add the hotkey
        for planet in self.planets:
            if planet.mouseover(pos):
                planet.hotkey = key
                  
                planet.hotkey_name = constants.valid_hotkeys[key]
                #We can only mouseover one planet at a time so end the loop if
                #we find one
                break
                  
    def select_hotkey(self, key):
        #Use a list comprehension here to get the planets that the player owns
        owned_planets = [p for p in self.planets
                         if p.owner == self.active_player]
          
        for planet in owned_planets:            
            #Clear all selected planets while looping through so only one can
            #be selected at a time
            if planet.is_dragged:
                planet.is_dragged = False
                  
            if planet.hotkey == key:
                planet.is_dragged = True
                  
    '''def out_of_bounds(self, proj):
        #Checks if projectile is out of bounds, apply forces to bring it back
        #Boolean math gimmick, if any one of these is True then it returns True
        return ((proj.pos[0] < 0) + (proj.pos[0] > self.field_rect.width) +
                (proj.pos[1] < 0) + (proj.pos[1] > self.field_rect.height) )'''
  
                  
    def update(self):
        for player in self.players:
            player.update()
          
        for proj in self.projectiles:
            proj.update()
              
            #Bounce off the walls
            if proj.pos[0] < 0:
                proj.dx *= -1
                proj.ax *= -1
            elif proj.pos[0] > self.field_rect.width:
                proj.dx *= -1
                proj.ax *= -1
            if proj.pos[1] < 0:
                proj.dy *= -1
                proj.ay *= -1
            elif proj.pos[1] > self.field_rect.height:
                proj.dy *= -1
                proj.ay *= -1
  
            '''if self.out_of_bounds(proj):
                angle = math.atan2((proj.rect.centery- self.field_rect.centery),
                                   (proj.rect.centerx- self.field_rect.centerx))
                proj.ax -= math.cos(-angle) * 0.002
                proj.ay += math.sin(-angle) * 0.002'''
  
        for planet in self.planets:
            #Neutral planets don't gain value, so we don't call update on them
            if planet.owner:
                planet.update()
                  
                ai = planet.owner
                if planet.owner.is_ai and ai.wait_counter > ai.wait_cycle:
                    if planet.value > ai.value_until_shoot:
                        if ai.control_counter < ai.can_control:
                            ai.process(planet, self.planets)
                          
  
  
            if planet.is_dragged:
                #Don't allow the player to select planets that aren't his
                if planet.owner == self.active_player:
                    #Set the planet's text to yellow when it's selected
                    planet.value_color = (255, 255, 0)
                else:
                    planet.clear_clicked()
  
                  
  
            for proj in self.projectiles:
                #Ignore projectle if this planet is where the it was shot from.
  
                if planet == proj.parent_planet:
                        continue
  
                dist = find_distance(planet.rect.center, proj.rect.center)
  
                  
                #Ignore projectile if it is too far away
                if dist > 40000:
                    continue
                #If dist is 0, set it to something to avoid making a big mistake
                elif dist == 0:
                    dist = 0.001
  
                m1 = planet.radius
                m2 = proj.radius
                force = (m1*1000) / (dist**2)
                      
                angle = math.atan2((proj.rect.centery - planet.rect.centery),
                                   (proj.rect.centerx - planet.rect.centerx))
                proj.ax -= math.cos(-angle) * force * 3
                proj.ay += math.sin(-angle) * force * 3
                  
                if collide_circle(proj, planet):
                    if planet.shielded and planet.owner != proj.owner:
                        proj.dx *= -1
                        proj.dy *= -1
                    else:
                        planet.on_projectile_collided(proj)
  
                        self.remove_projectile(proj)
  
                    #Right now the view does not pick up this event, so we don't
                    #need to send it
                    '''self.evm.post(ev.ProjectileCollided(proj, planet))'''
              
              
                  
    def clear(self):
        self.planets = []
        self.projectiles = []
          
    def notify(self, event):
        if event.id == 'Tick':
            self.update()
            return
        elif event.id == 'StartGame':
            self.init_game()        
        elif event.id == 'CreatePlanet':
            self.create_planet(event.pos, event.radius)
        elif event.id == 'ShootProjectile':
            self.create_projectile(event.parent_planet, event.vector)
        elif event.id == 'SetHotkey':
            self.set_hotkey(event.pos, event.key)
        elif event.id == 'SelectHotkey':
            self.select_hotkey(event.key)
        elif event.id == 'MOUSEDRAG':
            self.select_planet()
              
        elif event.id == 'ClearGame':
            self.clear()
  
def find_distance(p1, p2):
    #Technically this returns distance squared, but it needs to be bigger anyway.
    dist = (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2
    return dist
  
def program_quit():
    pygame.quit()
    sys.exit()
  
def main():
      
    evm = EventManager()
    controller = Controller(evm)
    model = Model(evm)
    view = View(evm)
    media_manager = MediaManager(evm)
  
      
    controller.tick()
if __name__ == '__main__':
    main() 

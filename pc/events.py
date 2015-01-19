class StartGame:
    def __init__(self):
        self.id = 'StartGame'

class ClearGame:
    def __init__(self):
        self.id = 'ClearGame'





class Tick:
    #Called to update the game each frame.
    def __init__(self):
        self.id = 'Tick'
        
class LMBDOWN:
    def __init__(self, pos):
        self.id = 'LMBDOWN'
        self.pos = pos

        
class LMBUP:
    def __init__(self, pos):
        self.id = 'LMBUP'
        self.pos = pos

class RMBDOWN:
    def __init__(self, pos):
        self.id = 'RMBDOWN'
        self.pos = pos

        
class RMBUP:
    def __init__(self, pos):
        self.id = 'RMBUP'
        self.pos = pos

   
class MOUSEDRAG:
    def __init__(self, pos):
        self.id = 'MOUSEDRAG'
        self.pos = pos

        
class UpdatePlanetColor:
    #Called by Planet when its owner changes
    #Notifies the View to update the planet's color to that of its new owner
    def __init__(self, model):
        self.id = 'UpdatePlanetColor'
        self.model = model

        
class CreatePlanet:
    #Used to initialize a planet in the model
    def __init__(self, pos, radius):
        self.id = 'CreatePlanet'
        self.pos = pos
        self.radius = radius

        
class PlanetCreated:
    #Called by the Model after creating a Planet
    #Notifies the View to render it
    def __init__(self, model):
        self.id = 'PlanetCreated'
        self.model = model

        
class ShootProjectile:
    #Called by the Planet class when a projectile is fired
    #Notifies the Model
    def __init__(self, parent_planet, vector):
        self.id = 'ShootProjectile'
        self.parent_planet = parent_planet
        self.vector = vector

        
class ProjectileCreated:
    #Called by the Model after creating a Projectile
    #Notifies the View to render it
    def __init__(self, model):
        self.id = 'ProjectileCreated'
        self.model = model


class ProjectileCollided:
    #Called by the Model when a projectile collides with a Planet
    #Notifies the View to stop rendering the Planet/render a death animation
    ####View currently does not respond to this event
    def __init__(self, proj, planet):
        self.id = 'ProjectileCollided'
        self.proj = proj
        self.planet = planet


class SetHotkey:
    def __init__(self, pos, key):
        self.id = 'SetHotkey'
        self.pos = pos
        self.key = key

class SelectHotkey:
    def __init__(self, key):
        self.id = 'SelectHotkey'
        self.key = key

import pygame.image

from pygame.surface import Surface
from pygame.transform import smoothscale

def load_image(filename):
    return pygame.image.load(filename).convert_alpha()
class Planet:
    def __init__(self, model):
        self.id = 'Planet'
        
        self.model = model

        self.size = model.radius*2, model.radius*2
        
        self.base_image = load_image('planet.png')
        self.image = smoothscale(self.base_image, self.size)

        self.border4 = load_image('border4.png')
        self.border3 = load_image('border3.png')
        self.border2 = load_image('border2.png')
        self.border1 = load_image('border1.png')

    def get_border(self):
        '''if self.model.lockdown_frames > 180:
            return smoothscale(self.border4, self.size)
        elif self.model.lockdown_frames > 120:
            return smoothscale(self.border3, self.size)
        elif self.model.lockdown_frames > 60:
            return smoothscale(self.border2, self.size)
        else:
            return smoothscale(self.border1, self.size)'''
        return smoothscale(self.border4, self.size)
        
    def set_color(self, player):
        #Reset the image to the base_image first so we don't fill the colored
        #image, and end up mixing the colors
        self.image = smoothscale(self.base_image, self.size)
        self.image.fill(player.color, None, pygame.BLEND_ADD)

class Projectile:
    def __init__(self, model):
        self.id = 'Projectile'

        self.size = (model.radius*2, model.radius*2)

        self.base_image = load_image('planet.png')
        self.image = smoothscale(self.base_image, self.size)

        self.model = model
        
    def set_color(self, player):
        #Reset the image to the base_image first so we don't fill the colored
        #image, and end up mixing the colors
        self.image = smoothscale(self.base_image, self.size)
        self.image.fill(player.color, None, pygame.BLEND_ADD)

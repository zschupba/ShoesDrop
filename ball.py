import pygame
import random

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800

WHITE = (255, 255, 255)
BLACK = (0,0,0)
class Ball(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()

        self.image = pygame.image.load("zachsCat.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))

        self.rect = self.image.get_rect()
        
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = 20
        
        self.velocity_y = 0
        self.gravity = 0.2  
        self.round = 1
    
    def update(self):
        self.velocity_y += self.gravity
        
        self.rect.y += self.velocity_y
        
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity_y = 0 
        
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            
    def reset(self):

        self.image = pygame.image.load("zachsCat.png").convert_alpha()

        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))

        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = 20
        self.velocity_y = 0
        self.round += 1



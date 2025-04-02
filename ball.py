import pygame
import random

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800

WHITE = (255, 255, 255)
BLACK = (0,0,0)
class Ball(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()

        # Create a surface for the ball
        self.image = pygame.Surface([width, height])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)

        r = random.randint(200, 255)
        g = random.randint(0, 155)
        b = random.randint(0, 100)
        randomColor = (r, g, b)

        # Draw a circle on the surface
        radius = min(width, height) // 2
        center_x = width // 2
        center_y = height // 2


        pygame.draw.circle(self.image, randomColor, (center_x, center_y), radius)

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

        r = random.randint(200, 255)
        g = random.randint(0, 155)
        b = random.randint(0, 100)
        randomColor = (r, g, b)

        self.image.fill(WHITE)
        radius = min(self.rect.width, self.rect.height) // 2
        center_x = self.rect.width // 2
        center_y = self.rect.height // 2



        pygame.draw.circle(self.image, randomColor, (center_x, center_y), radius)
    
        self.color = randomColor

        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = 20
        self.velocity_y = 0
        self.round += 1



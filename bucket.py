import pygame
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800

class Bucket(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
    
    # Draw left side
        pygame.draw.rect(self.image, color, [0, 0, 3, height])

    # Draw right side
        pygame.draw.rect(self.image, color, [width-3, 0, 3, height])
    
    # Draw bottom
        pygame.draw.rect(self.image, color, [0, height-3, width - 2, 3])
    
    # Get the rectangle of the surface
        self.rect = self.image.get_rect()

        self.rect.x = 290
        self.rect.y = 600

        self.baseSpeed = 3

    def moveRight(self, baseSpeed):
        if self.rect.x + 30 <= SCREEN_WIDTH: 
            self.rect.x += baseSpeed
            

    def moveLeft(self, baseSpeed):
        if self.rect.x >= 0:
            self.rect.x -= baseSpeed

    def resetBucket(self):
        self.rect.x = 290
        self.rect.y = 600
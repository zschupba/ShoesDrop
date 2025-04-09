import pygame
import sys
import math
import random
import socket
import threading
import json
import time

from ball import Ball
from bucket import Bucket

#initialize game and fonts
pygame.init()
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Falling Ball Game - Server")

font = pygame.font.SysFont(None, 36)
title_font = pygame.font.SysFont(None, 72)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# GAME STATES
START_SCREEN = 0
PLAYING = 1
GAME_OVER = 2
current_state = START_SCREEN

# Game parameters
baseSpeed = 4
bucketSpeed = baseSpeed
baseGravity = 0.1
show_speed_message = False
message_timer = 0
score = 0

# Create game objects
all_sprites = pygame.sprite.Group()
ball = Ball(50, 30) 
playerBucket = Bucket(BLACK, 50, 50) 
all_sprites.add(playerBucket, ball)

stars = []
for _ in range(50):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    speed = random.uniform(0.5, 2.0)
    stars.append([x, y, speed])

#global command input (network)
client_command = None

def network_thread():
    global client_command, current_state, score, bucketSpeed, ball, playerBucket

    host = socket.gethostbyname(socket.gethostname())
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        host = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    port = 5000
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(1)
    print("Server enabled on: ", host, "port: ", port)
    conn, addr = server_socket.accept()
    print("Connection from: ", addr)
    while True:
        try:
            data = conn.recv(1024).decode().strip()
            if not data:
                break
            print("Received command: ", data)
            if data == 'left':
                client_command = 'left'
            elif data == 'right':
                client_command = 'right'
            elif data == 'space':
                if current_state in [START_SCREEN, GAME_OVER]:
                    current_state = PLAYING
                    ball.reset()
                    playerBucket.resetBucket()
                    score = 0
                    bucketSpeed = baseSpeed
                    ball.gravity = baseGravity
        except Exception as e:
            print("Network Error: ", e)
            break
    conn.close()
    server_socket.close()

def draw_start_screen():
    for y in range(SCREEN_HEIGHT):
        blue_val = int(150 * (y / SCREEN_HEIGHT))
        color = (30, 50, 150 - blue_val)
        pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
    for star in stars:
        star[1] += star[2]
        if star[1] > SCREEN_HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, SCREEN_WIDTH)
        pygame.draw.circle(screen, WHITE, (int(star[0]), int(star[1])), 2)
    title = title_font.render("BALL DROP", True, YELLOW)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//4))
    current_time = pygame.time.get_ticks()
    ball_y = SCREEN_HEIGHT//2 + 50 + 30 * math.sin(current_time / 200)
    pygame.draw.circle(screen, RED, (SCREEN_WIDTH//2, int(ball_y)), 25)
    pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH//2 - 30, SCREEN_HEIGHT//2 + 120, 60, 40))
    instruction = font.render("Press SPACE to Start", True, WHITE)
    screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, SCREEN_HEIGHT*3//4))
   
def draw_game_over_screen():
    for y in range(SCREEN_HEIGHT):
        red_val = int(100 * (y / SCREEN_HEIGHT))
        color = (150 - red_val, 20, 30)
        pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
    game_over = title_font.render("GAME OVER", True, RED)
    screen.blit(game_over, (SCREEN_WIDTH//2 - game_over.get_width()//2, SCREEN_HEIGHT//4))
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))
    restart = font.render("Press SPACE to Play Again", True, YELLOW)
    screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, SCREEN_HEIGHT*3//4))

clock = pygame.time.Clock()
game_running = True

threading.Thread(target=network_thread, daemon=True).start()

while game_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if current_state in [START_SCREEN, GAME_OVER]:
                    current_state = PLAYING
                    ball.reset()
                    playerBucket.resetBucket()
                    score = 0
                    bucketSpeed = baseSpeed
                    ball.gravity = baseGravity

    if current_state == START_SCREEN:
        draw_start_screen()
    elif current_state == PLAYING:
        all_sprites.update()

        #check collision
        if pygame.sprite.collide_rect(ball, playerBucket):
            score += 1
            difficultyLevel = math.floor(score / 5)
            if score % 5 == 0:
                bucketSpeed = baseSpeed * (1 + difficultyLevel * 0.25)
                ball.gravity = baseGravity * (1 + difficultyLevel * 0.4)
                show_speed_message = True
                message_timer = 60
            ball.reset()

        if ball.rect.bottom >= SCREEN_HEIGHT:
            current_state = GAME_OVER

        if client_command == 'left':
            playerBucket.moveLeft(bucketSpeed)
        elif client_command == 'right':
            playerBucket.moveRight(bucketSpeed)
        elif client_command == 'up':
            playerBucket.moveUp(bucketSpeed)
        elif client_command == 'down':
            playerBucket.moveDown(bucketSpeed)
            
        client_command = None

        for y in range(SCREEN_HEIGHT):
            blue_val = int(155 * (y / SCREEN_HEIGHT))
            color = (100, 170 - blue_val, 255 - blue_val)
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))

        # Draw moving clouds as decorative elements
        for i in range(6):
            cloud_x = (i * 150 + pygame.time.get_ticks() // 20) % (SCREEN_WIDTH + 300) - 150
            cloud_y = 50 + i * 30
            for j in range(3):
                pygame.draw.circle(screen, (240, 240, 240), (int(cloud_x + j * 20), int(cloud_y)), 25)

        all_sprites.draw(screen)
        scoreText = font.render(f"Score: {score}", True, BLACK)
        screen.blit(scoreText, (10, 10))

        if show_speed_message:
            speedIncreaseText = font.render("SPEED INCREASE!!!", True, RED)
            screen.blit(speedIncreaseText, (SCREEN_WIDTH//2 - speedIncreaseText.get_width()//2, SCREEN_HEIGHT//2))
            message_timer -= 1
            if message_timer <= 0:
                show_speed_message = False

    elif current_state == GAME_OVER:
        draw_game_over_screen()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
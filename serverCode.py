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

#GAME SCREEN
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800

#COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
SKYBLUE = (135, 206, 235)
YELLOW = (255, 255, 0)

#GAME STATES
START_SCREEN = 0
PLAYING = 1
GAME_OVER = 2

#VARIABLES NEEDED BY BOTH THREADS
current_state = START_SCREEN
score = 0
bucketPos = 300
baseSpeed = 4
bucketSpeed = baseSpeed
baseGravity = 0.1
show_speed_message = False
message_timer = 0

#NETWORKING SETUP
#nic_name = "wlan1"
host = "10.22.0.47"
port = 5000
server_socket = None
client_connections = []
lock = threading.Lock() #THREAD SAFETY

def client_handler(conn, addr):
    global bucketPos, current_state, score

    print(f"New connection from {addr}")

    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
                
            print(f"From {addr}: {data}")

            #HANDLE COMMANDS FROM USER
            with lock:
                if data == 'a':
                    bucketPos = min(0, bucketPos - 10)
                elif data == 'd':
                    bucketPos = min(SCREEN_WIDTH - 50, bucketPos + 10)
                elif data == ('space') and (current_state == START_SCREEN or current_state == GAME_OVER):
                    current_state = PLAYING
                    score = 0
                    bucketPos = SCREEN_WIDTH//2
    except Exception as e:
        print(f"Error Handling Client {addr}: {e}")
    finally:
        with lock:
            if conn in client_connections:
                client_connections.remove(conn)
        conn.close()
        print(f"Connection Closed: {addr}")

def server_thread():
    global server_socket, host, client_connections

    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind(("0.0.0.0", port))
        server_socket.listen(5)
        print(f"Server running on {host}:{port}")

        while True:
            conn, addr = server_socket.accept()
            with lock:
                client_connections.append(conn)

            client_thread = threading.Thread(target=client_handler, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()

    except Exception as e:
        print(f"Server error: {e}")
    finally:
        if server_socket:
            server_socket.close()

def broadcast_game_state():
    global client_connections, current_state, score, bucketPos

    with lock:
        if not client_connections:
            return
        
        game_state = {
            'state': current_state,
            'score': score,
            'bucket_pos': bucketPos
        }

        data = json.dumps(game_state).encode()

        for conn in client_connections[:]:
            try:
                conn.send(data)
            except:
                if conn in client_connections:
                    client_connections.remove(conn)
                try:
                    conn.close()
                except:
                    pass

def game_thread():
    global current_state, score, bucketPos, bucketSpeed, baseGravity, show_speed_message, message_timer

    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Falling Ball Game")

    all_sprites = pygame.sprite.Group()
    ball = Ball(50, 30)
    playerBucket = Bucket(BLACK, 50, 50)
    all_sprites.add(playerBucket, ball)

    font = pygame.font.SysFont(None, 36)
    title_font = pygame.font.SysFont(None, 72)

    stars = []
    for _ in range(50):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        speed = random.uniform(0.5, 2.0)
        stars.append([x, y, speed])

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

        net_info = font.render(f"Server: {host}:{port}", True, WHITE)
        screen.blit(net_info, (10, SCREEN_HEIGHT - 40))

    def draw_game_over_screen():
        for y in range(SCREEN_HEIGHT):
            red_val = int(100 * (y / SCREEN_HEIGHT))
            color = (150 - red_val, 20, 30)
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))

        game_over = title_font.render("GAME OVER", True, RED)
        screen.blit(game_over, (SCREEN_WIDTH//2 - game_over.get_width()//2, SCREEN_HEIGHT//4))

        score_text = font.render(f"Final Score: {score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT*3//4))

        restart = font.render("Press SPACE to Play Again", True, YELLOW)
        screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, SCREEN_HEIGHT*3//4))

    clock = pygame.time.Clock()
    game_running = True

    #START SERVER THREAD
    server = threading.Thread(target=server_thread)
    server.daemon = True
    server.start()

    last_broadcast = time.time()

    while game_running:
        current_time = time.time()
        if current_time - last_broadcast >= 0.1:
            broadcast_game_state()
            last_broadcast = current_time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if current_state == START_SCREEN or current_state == GAME_OVER:
                        current_state = PLAYING
                        ball.reset()
                        playerBucket.resetBucket()
                        score = 0
                        bucketSpeed = baseSpeed
                        ball.gravity = baseGravity

        with lock:
            playerBucket.rect.x = bucketPos

        if current_state == START_SCREEN:
            draw_start_screen()

        elif current_state == PLAYING:
            ball.update()

            if pygame.sprite.collide_rect(ball, playerBucket):
                with lock:
                    score += 1
                difficultyLevel = math.floor(score / 5)
                bucketSpeed = baseSpeed * (1 + difficultyLevel * 0.25)
                ball.gravity = baseGravity * (1 + difficultyLevel * 0.4)

                if score % 5 == 0:
                    show_speed_message = True
                    message_timer = 60

                ball.reset()

            if ball.rect.bottom >= SCREEN_HEIGHT:
                current_state = GAME_OVER

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                with lock:
                    bucketPos = max(0, bucketPos - bucketSpeed)
                playerBucket.rect.x = bucketPos
            if keys[pygame.K_RIGHT]:
                with lock:
                    bucketPos = min(SCREEN_WIDTH - playerBucket.rect.width, bucketPos + bucketSpeed)
                playerBucket.rect.x = bucketPos
            
            for y in range(SCREEN_HEIGHT):
                blue_val = int(155 * (y / SCREEN_HEIGHT))
                color = (100, 170 - blue_val, 255 - blue_val)
                pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
            
            # Draw clouds
            for i in range(6):
                cloud_x = (i * 150 + pygame.time.get_ticks() // 20) % (SCREEN_WIDTH + 300) - 150
                cloud_y = 50 + i * 30
                for j in range(3):
                    pygame.draw.circle(screen, (240, 240, 240), 
                                     (int(cloud_x + j * 20), int(cloud_y)), 25)
            
            # Draw sprites
            screen.blit(ball.image, ball.rect)
            screen.blit(playerBucket.image, playerBucket.rect)
            
            # Draw score
            scoreText = font.render(f"Score: {score}", True, BLACK)
            screen.blit(scoreText, (10, 10))
            
            # Draw connected clients count
            with lock:
                clients_text = font.render(f"Players: {len(client_connections)}", True, BLACK)
            screen.blit(clients_text, (10, 50))
            
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
    
    # Clean up before exit
    with lock:
        for conn in client_connections:
            try:
                conn.close()
            except:
                pass
        client_connections.clear()
    
    if server_socket:
        server_socket.close()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_thread()
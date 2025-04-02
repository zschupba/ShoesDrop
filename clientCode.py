import pygame
import sys
import socket
import pickle
import threading
import math
import random
import time
import struct

# Client configuration
SERVER_HOST = '127.0.0.1'  # Change to server's IP address if on different machine
SERVER_PORT = 12345

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
SKYBLUE = (135, 206, 235)
YELLOW = (255, 255, 0)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Falling Ball Game - Client")

# Game states
START_SCREEN = 0
PLAYING = 1
GAME_OVER = 2

# Fonts
font = pygame.font.SysFont(None, 36)
title_font = pygame.font.SysFont(None, 72)

# Background stars
stars = []
for _ in range(50):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    speed = random.uniform(0.5, 2.0)
    stars.append([x, y, speed])

# Game state variables (will be updated from server)
current_state = START_SCREEN
ball_pos = {"x": 0, "y": 0}
bucket_pos = {"x": SCREEN_WIDTH//2, "y": SCREEN_HEIGHT - 60}
score = 0
show_speed_message = False
client_connected = False

# Network variables
game_state_received = False
server_socket = None
stop_thread = False

def connect_to_server():
    """Connect to the game server."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_HOST, SERVER_PORT))
        print(f"Connected to server at {SERVER_HOST}:{SERVER_PORT}")
        return sock
    except socket.error as e:
        print(f"Connection error: {e}")
        return None

def receive_game_state(sock):
    """Thread function to receive game state updates from server."""
    global current_state, ball_pos, bucket_pos, score, show_speed_message
    global client_connected, game_state_received, stop_thread
    
    while not stop_thread:
        try:
            # First, get the message size (4 bytes for an int)
            size_data = receive_exactly(sock, 4)
            if not size_data:
                break
                
            message_size = struct.unpack("!I", size_data)[0]
            
            # Now receive the exact amount of data for the pickled object
            data = receive_exactly(sock, message_size)
            if not data:
                break
                
            # Unpickle the game state
            state = pickle.loads(data)
            
            # Update game state
            current_state = state["state"]
            ball_pos = state["ball"]
            bucket_pos = state["bucket"]
            score = state["score"]
            show_speed_message = state["speed_message"]
            client_connected = state["client_connected"]
            
            game_state_received = True
            
        except Exception as e:
            print(f"Error receiving game state: {e}")
            break
    
    print("Receive thread stopped")

def receive_exactly(sock, n):
    """Receive exactly n bytes from the socket."""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def draw_start_screen():
    # Background gradient
    for y in range(SCREEN_HEIGHT):
        blue_val = int(150 * (y / SCREEN_HEIGHT))
        color = (30, 50, 150 - blue_val)
        pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
    
    # Stars
    for star in stars:
        star[1] += star[2]
        if star[1] > SCREEN_HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, SCREEN_WIDTH)
        pygame.draw.circle(screen, WHITE, (int(star[0]), int(star[1])), 2)
    
    # Title
    title = title_font.render("BALL DROP", True, YELLOW)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//4))
    
    # Animated ball
    current_time = pygame.time.get_ticks()
    ball_y = SCREEN_HEIGHT//2 + 50 + 30 * math.sin(current_time / 200)
    pygame.draw.circle(screen, RED, (SCREEN_WIDTH//2, int(ball_y)), 25)
    
    # Bucket
    pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH//2 - 30, SCREEN_HEIGHT//2 + 120, 60, 40))
    
    # Instructions
    if client_connected:
        instruction = font.render("Press SPACE to Start", True, WHITE)
    else:
        instruction = font.render("Connecting to server...", True, WHITE)
    screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, SCREEN_HEIGHT*3//4))

def draw_game_screen():
    # Background gradient
    for y in range(SCREEN_HEIGHT):
        blue_val = int(155 * (y / SCREEN_HEIGHT))
        color = (100, 170 - blue_val, 255 - blue_val)
        pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
    
    # Clouds
    for i in range(6):
        cloud_x = (i * 150 + pygame.time.get_ticks() // 20) % (SCREEN_WIDTH + 300) - 150
        cloud_y = 50 + i * 30
        for j in range(3):
            pygame.draw.circle(screen, (240, 240, 240), 
                             (int(cloud_x + j * 20), int(cloud_y)), 25)
    
    # Draw ball and bucket
    pygame.draw.rect(screen, BLACK, (bucket_pos["x"], bucket_pos["y"], 50, 50))
    pygame.draw.rect(screen, RED, (ball_pos["x"], ball_pos["y"], 50, 30))
    
    # Score
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    
    # Speed increase message
    if show_speed_message:
        speedIncreaseText = font.render("SPEED INCREASE!!!", True, RED)
        screen.blit(speedIncreaseText, (SCREEN_WIDTH//2 - speedIncreaseText.get_width()//2, SCREEN_HEIGHT//2))

def draw_game_over_screen():
    # Background gradient
    for y in range(SCREEN_HEIGHT):
        red_val = int(100 * (y / SCREEN_HEIGHT))
        color = (150 - red_val, 20, 30)
        pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
    
    # Game over text
    game_over = title_font.render("GAME OVER", True, RED)
    screen.blit(game_over, (SCREEN_WIDTH//2 - game_over.get_width()//2, SCREEN_HEIGHT//4))
    
    # Final score
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))
    
    # Restart instruction
    restart = font.render("Press SPACE to Play Again", True, YELLOW)
    screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, SCREEN_HEIGHT*3//4))

def draw_connecting_screen():
    screen.fill(BLACK)
    message = font.render("Connecting to server...", True, WHITE)
    screen.blit(message, (SCREEN_WIDTH//2 - message.get_width()//2, SCREEN_HEIGHT//2))

def main():
    global stop_thread, game_state_received
    
    # Connect to server
    server_socket = connect_to_server()
    
    if not server_socket:
        # Show error and wait for a moment
        screen.fill(BLACK)
        error_msg = font.render("Failed to connect to server", True, RED)
        retry_msg = font.render("Check server address and try again", True, WHITE)
        screen.blit(error_msg, (SCREEN_WIDTH//2 - error_msg.get_width()//2, SCREEN_HEIGHT//2 - 30))
        screen.blit(retry_msg, (SCREEN_WIDTH//2 - retry_msg.get_width()//2, SCREEN_HEIGHT//2 + 30))
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()
    
    # Start receive thread
    receive_thread = threading.Thread(target=receive_game_state, args=(server_socket,))
    receive_thread.daemon = True
    receive_thread.start()
    
    # Wait for first game state
    max_wait = 50  # Wait up to 5 seconds (50 * 0.1)
    wait_count = 0
    while not game_state_received and wait_count < max_wait:
        draw_connecting_screen()
        pygame.display.flip()
        pygame.time.wait(100)
        wait_count += 1
    
    # Main game loop
    running = True
    clock = pygame.time.Clock()
    
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Key press events
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    try:
                        server_socket.send("LEFT".encode())
                    except:
                        print("Error sending LEFT command")
                
                elif event.key == pygame.K_RIGHT:
                    try:
                        server_socket.send("RIGHT".encode())
                    except:
                        print("Error sending RIGHT command")
                
                elif event.key == pygame.K_SPACE:
                    try:
                        server_socket.send("SPACE".encode())
                    except:
                        print("Error sending SPACE command")
            
            # Key release events
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    try:
                        server_socket.send("STOP".encode())
                    except:
                        print("Error sending STOP command")
        
        # Draw appropriate screen based on game state
        if current_state == START_SCREEN:
            draw_start_screen()
        elif current_state == PLAYING:
            draw_game_screen()
        elif current_state == GAME_OVER:
            draw_game_over_screen()
        
        pygame.display.flip()
        clock.tick(60)
    
    # Cleanup
    stop_thread = True
    server_socket.close()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
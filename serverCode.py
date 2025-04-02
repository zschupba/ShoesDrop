import socket
import threading
import random
import time
import pickle
import sys
import struct

# Import Ball and Bucket classes
from ball import Ball
from bucket import Bucket

# Server configuration
HOST = '0.0.0.0'  # Bind to all network interfaces
PORT = 12345      # Port to listen on

# Game configuration
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
BUCKET_WIDTH = 50
BUCKET_HEIGHT = 50

# Game variables
baseSpeed = 4
bucketSpeed = baseSpeed
baseGravity = 0.1
score = 0
current_state = 0  # START_SCREEN = 0, PLAYING = 1, GAME_OVER = 2
game_over = False
show_speed_message = False
message_timer = 0

# Create game objects (but don't render them)
ball_x = random.randrange(0, SCREEN_WIDTH - 50)
ball_y = 0
ball_speed = 0
ball_gravity = baseGravity

bucket_x = (SCREEN_WIDTH - BUCKET_WIDTH) // 2
bucket_y = SCREEN_HEIGHT - BUCKET_HEIGHT - 10

# Set up server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"Server started on {HOST}:{PORT}")

# Client handling variables
client_socket = None
client_address = None
current_movement = None
restart_requested = False

def reset_game():
    global score, bucketSpeed, ball_speed, ball_gravity, ball_x, ball_y, bucket_x, bucket_y, show_speed_message, message_timer, game_over
    
    ball_x = random.randrange(0, SCREEN_WIDTH - 50)
    ball_y = 0
    ball_speed = 0
    ball_gravity = baseGravity
    
    bucket_x = (SCREEN_WIDTH - BUCKET_WIDTH) // 2
    bucket_y = SCREEN_HEIGHT - BUCKET_HEIGHT - 10
    
    score = 0
    bucketSpeed = baseSpeed
    show_speed_message = False
    message_timer = 0
    game_over = False

def handle_client_connection(sock):
    global current_movement, current_state, restart_requested, game_over
    
    while True:
        try:
            data = sock.recv(1024).decode().strip()
            if not data:
                break
                
            # Parse client input
            if data == "LEFT":
                current_movement = "LEFT"
            elif data == "RIGHT":
                current_movement = "RIGHT"
            elif data == "STOP":
                current_movement = None
            elif data == "SPACE":
                if current_state == 0:  # START_SCREEN
                    current_state = 1  # PLAYING
                    reset_game()
                elif current_state == 2:  # GAME_OVER
                    restart_requested = True
        except:
            break
    
    print("Client disconnected")
    sock.close()
    global client_socket
    client_socket = None

def accept_clients():
    global client_socket, client_address
    
    while True:
        print("Waiting for client connection...")
        sock, addr = server_socket.accept()
        client_socket = sock
        client_address = addr
        print(f"Client connected from {addr}")
        
        # Start a new thread to handle client communication
        client_handler = threading.Thread(target=handle_client_connection, args=(sock,))
        client_handler.daemon = True
        client_handler.start()

def update_game_state():
    global ball_x, ball_y, ball_speed, bucket_x, bucket_y, score, current_state, game_over
    global bucketSpeed, ball_gravity, show_speed_message, message_timer
    
    # Only update if in playing state
    if current_state != 1:  # PLAYING
        return
        
    # Update ball position
    ball_speed += ball_gravity
    ball_y += ball_speed
    
    # Process client movement
    if current_movement == "LEFT":
        bucket_x -= bucketSpeed
        if bucket_x < 0:
            bucket_x = 0
    elif current_movement == "RIGHT":
        bucket_x += bucketSpeed
        if bucket_x > SCREEN_WIDTH - BUCKET_WIDTH:
            bucket_x = SCREEN_WIDTH - BUCKET_WIDTH
    
    # Check for collision with bucket
    if (ball_y + 30 > bucket_y and 
        ball_y < bucket_y + BUCKET_HEIGHT and
        ball_x + 50 > bucket_x and
        ball_x < bucket_x + BUCKET_WIDTH):
        
        score += 1
        difficultyLevel = score // 5
        bucketSpeed = baseSpeed * (1 + difficultyLevel * 0.25)
        ball_gravity = baseGravity * (1 + difficultyLevel * 0.4)
        
        if score % 5 == 0:
            show_speed_message = True
            message_timer = 60
        
        # Reset ball
        ball_x = random.randrange(0, SCREEN_WIDTH - 50)
        ball_y = 0
        ball_speed = 0
    
    # Check for ball hitting bottom (game over)
    if ball_y >= SCREEN_HEIGHT:
        current_state = 2  # GAME_OVER
        game_over = True
    
    # Update message timer
    if show_speed_message:
        message_timer -= 1
        if message_timer <= 0:
            show_speed_message = False

def send_game_state_to_client():
    if client_socket:
        # Create game state object
        game_state = {
            "state": current_state,
            "ball": {"x": ball_x, "y": ball_y},
            "bucket": {"x": bucket_x, "y": bucket_y},
            "score": score,
            "speed_message": show_speed_message,
            "client_connected": client_socket is not None
        }
        
        try:
            # Serialize with pickle
            data = pickle.dumps(game_state)
            
            # Send message size first, then the pickled data
            message_size = struct.pack("!I", len(data))
            client_socket.sendall(message_size + data)
        except:
            print("Error sending game state to client")

# Start client acceptance thread
accept_thread = threading.Thread(target=accept_clients)
accept_thread.daemon = True
accept_thread.start()

# Main game loop
game_running = True
last_update_time = time.time()

try:
    while game_running:
        # Check for restart
        if restart_requested and current_state == 2:  # GAME_OVER
            current_state = 1  # PLAYING
            reset_game()
            restart_requested = False
        
        # Update game state
        update_game_state()
        
        # Send updates to client approximately 30 times per second (reduced to help with lag)
        current_time = time.time()
        if current_time - last_update_time >= 1/30:
            send_game_state_to_client()
            last_update_time = current_time
        
        # Small delay to prevent high CPU usage
        time.sleep(0.01)

except KeyboardInterrupt:
    print("Server shutting down...")
    
finally:
    # Clean up
    if client_socket:
        client_socket.close()
    server_socket.close()
    print("Server stopped.")
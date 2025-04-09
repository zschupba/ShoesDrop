import pygame
import sys
import socket
import subprocess
import threading
import os

# Import server module (assuming it's in the same directory)
# Note: We'll import it only when needed to avoid running it immediately

# Initialize pygame
pygame.init()
pygame.font.init()

# Screen setup
screen_width, screen_height = 400, 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Game Lobby")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
LIGHT_GRAY = (220, 220, 220)

# Fonts
title_font = pygame.font.SysFont('Arial', 32)
normal_font = pygame.font.SysFont('Arial', 24)
small_font = pygame.font.SysFont('Arial', 18)

class Button:
    def __init__(self, x, y, width, height, color, text, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.text_color = text_color
        self.font = normal_font
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)  # Border
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class TextBox:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = WHITE
        self.text = ""
        self.active = False
        self.font = normal_font
    
    def draw(self, surface):
        if self.active:
            border_color = BLACK
        else:
            border_color = LIGHT_GRAY
        
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=5)
        
        text_surface = self.font.render(self.text, True, BLACK)
        surface.blit(text_surface, (self.rect.x + 10, self.rect.y + (self.rect.height - text_surface.get_height()) // 2))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True  # Signal that Enter was pressed
            else:
                self.text += event.unicode
        return False

def run_server():
    """Run the server code from serverCode.py"""
    # Import and run the server code
    import serverCode
    # The serverCode will take over the pygame window

def connect_to_server(ip_address):
    """Connect to a server at the given IP address"""
    try:
        # Parses IP and port
        if ':' in ip_address:
            host, port_str = ip_address.split(':')
            port = int(port_str)
        else:
            host = ip_address
            port = 5000  # Default port
        
        # Creates a socket and connect
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)  # Set timeout to 5 seconds
        client_socket.connect((host, port))
        
        # Sets the thread up to pass to server
        def client_thread(sock):
            while True:
                keys = pygame.key.get_pressed()
                
                if keys[pygame.K_LEFT]:
                    sock.send('left'.encode())
                elif keys[pygame.K_RIGHT]:
                    sock.send('right'.encode())
                elif keys[pygame.K_SPACE]:
                    sock.send('space'.encode())
                
                # Lower delay to make faster
                pygame.time.delay(30)
        
        threading.Thread(target=client_thread, args=(client_socket,), daemon=True).start()
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

def main_menu():
    host_button = Button(screen_width//2 - 100, screen_height//2 - 60, 200, 50, ORANGE, "Host Game")
    join_button = Button(screen_width//2 - 100, screen_height//2 + 10, 200, 50, GREEN, "Join Game")
    
    while True:
        screen.fill(WHITE)
        
        # Draws title
        title_text = title_font.render("BALL DROP", True, BLACK)
        screen.blit(title_text, (screen_width//2 - title_text.get_width()//2, 50))
        
        # Draws buttons
        host_button.draw(screen)
        join_button.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if host_button.is_clicked(event.pos):
                    # It is now the servers job
                    run_server()
                    return
                
                elif join_button.is_clicked(event.pos):
                    join_screen()

def join_screen():
    ip_textbox = TextBox(screen_width//2 - 150, screen_height//2 - 30, 300, 40)
    join_button = Button(screen_width//2 - 75, screen_height//2 + 40, 150, 50, GREEN, "Connect")
    back_button = Button(20, 20, 60, 30, LIGHT_GRAY, "Back", BLACK)
    
    instruction_text = small_font.render("Enter Server IP Address", True, BLACK)
    default_port_text = small_font.render("Default port is 5000", True, BLACK)
    
    while True:
        screen.fill(WHITE)
        
        # Draws title and instruction
        title_text = title_font.render("Join Game", True, BLACK)
        screen.blit(title_text, (screen_width//2 - title_text.get_width()//2, 50))
        
        screen.blit(instruction_text, (screen_width//2 - instruction_text.get_width()//2, screen_height//2 - 70))
        screen.blit(default_port_text, (screen_width//2 - default_port_text.get_width()//2, screen_height//2 - 50))
        
        # Draws textbox and buttons
        ip_textbox.draw(screen)
        join_button.draw(screen)
        back_button.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            enter_pressed = ip_textbox.handle_event(event)
            if enter_pressed:
                # Trys to connect when Enter is pressed
                if connect_to_server(ip_textbox.text):
                    success_screen("Connected successfully! Have fun playing!")
                    pygame.time.delay(1000)
                    return
                else:
                    error_screen("Connection failed!")
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if join_button.is_clicked(event.pos):
                    # Trys to connect to server when they click button
                    if connect_to_server(ip_textbox.text):
                        success_screen("Connected successfully! Have fun playing!")
                        pygame.time.delay(1000)
                        return
                    else:
                        error_screen("Connection failed!")
                
                elif back_button.is_clicked(event.pos):
                    return  


def success_screen(message):
    ok_button = Button(screen_width//2 - 75, screen_height//2 + 40, 150, 50, GREEN, "OK")
    
    while True:
        screen.fill(WHITE)
        
        # Draw message
        message_text = normal_font.render(message, True, BLACK)
        screen.blit(message_text, (screen_width//2 - message_text.get_width()//2, screen_height//2 - 50))
        
        # Draw button
        ok_button.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ok_button.is_clicked(event.pos):
                    return  

def error_screen(message):
    ok_button = Button(screen_width//2 - 75, screen_height//2 + 40, 150, 50, RED, "OK")
    
    while True:
        screen.fill(WHITE)
        
        message_text = normal_font.render(message, True, RED)
        screen.blit(message_text, (screen_width//2 - message_text.get_width()//2, screen_height//2 - 50))
        
        ok_button.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ok_button.is_clicked(event.pos):
                    return  

# Start the main menu
if __name__ == "__main__":
    main_menu()
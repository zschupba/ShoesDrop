import pygame
import socket
import sys

def sendCommand(sock, command):
    try:
        sock.sendall(command.encode())
    except Exception as e:
        print("Error sending command: ", e)

def main():
    pygame.init()
    screen = pygame.display.set_mode((300, 200))
    pygame.display.set_caption("Game Controls - Client")

    server_ip = input("Enter server IP address: ")
    port = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server_ip, port))
        print("Connected to server: ", server_ip, "on port: ", port)
    except Exception as e:
        print("Could not connect to server: ", e)
        sys.exit()

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
        keys = pygame.key.get_pressed()
        command = None

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            command = 'left'
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            command = 'right'
        elif keys[pygame.K_SPACE]:
            command = 'space'
            
        if command is not None:
            if command != last_command or command in ['left', 'right']:
                sendCommand(sock, command)
                last_command = command
        else:
            last_command = None  # Reset if no key is pressed            

        pygame.display.flip()
        clock.tick(60)
    
    sock.close()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
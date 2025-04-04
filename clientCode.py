import keyboard
import socket
import time
import sys

def client_program():
    #GET SERVER IP
    server_ip = input("Enter server IP address: ")
    port = 5000

    print(f"Trying to connect to server at {server_ip}:{port}")

    try:
        client_socket = socket.socket()
        client_socket.connect((server_ip, port))
        print("Connected to server!")

        print("Controls: ")
        print("  'Left Arrow' - Move bucket left")
        print("  'Right Arrow' - Move bucket right")
        print("  'Space' - Start/restart game")
        print("  'q' - Quit")
        print("\nWaiting for keyboard input...")
        
        # Main loop for capturing keyboard input
        while not keyboard.is_pressed('q'):
            if keyboard.is_pressed('left'):
                client_socket.send('a'.encode())  # We still send 'a' to the server
                time.sleep(0.1)
            if keyboard.is_pressed('right'):
                client_socket.send('d'.encode())  # We still send 'd' to the server
                time.sleep(0.1)
            if keyboard.is_pressed('space'):
                # Space can be used for both starting and restarting
                client_socket.send('space'.encode())  # Space maps to 'w' for start game
                time.sleep(0.1)
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.01)
            
    except ConnectionRefusedError:
        print(f"Connection refused. Make sure the server is running at {server_ip}:{port}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            client_socket.close()  # close the connection
        except:
            pass
        print("Connection closed")

if __name__ == '__main__':
    try:
        client_program()
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
        sys.exit(0)       
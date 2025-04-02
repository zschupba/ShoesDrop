# Ball Drop Network Game

## Overview
This is a client-server implementation of a "bucket catch" game developed as a final project for CS 35201 Computer Communication Networks (Spring 2025) at Kent State University. The project demonstrates socket programming concepts through an interactive game application.

## Team Members
- Ethan Hicks
- Zach

## Game Description
The game follows a classic "bucket catch" model with network communication:
- **Server**: Manages the game state and displays the game interface
- **Client**: Handles player input and communicates commands to the server

### Game Rules
- A bucket moves horizontally to collect falling objects
- Objects are randomly generated at the top of the screen
- Both falling objects and the bucket accelerate as the game progresses
- Game ends when any object reaches the bottom of the screen
- Score is displayed based on successfully caught objects

## Technical Implementation
- Built using Python and Pygame
- Utilizes socket programming for client-server communication
- Implements multithreading for handling game logic and network communications

## Controls
- Arrow keys for bucket movement
- SPACE to start / restart the game

## Requirements
- Python 3.12.3
- Pygame library
- Network connectivity between client and server machines

## Project Structure
- `serverCode.py`: Main server application
- `clientCode.py`: Client interface
- `ball.py`: Ball Object (dropping ball)
- `bucket.py`: Bucket Object (catches ball)
- `balldropgame.py`: Local Version of the game without networking

## Course Information
- **Course**: CS 35201 Computer Communication Networks
- **Semester**: Spring 2025
- **Department**: Computer Science, Kent State University




import pygame
import os, sys
from grid_multi import Grid
import socket
import threading

def create_thread(target):
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()

pygame.init()

HOST = '0.0.0.0' ###
PORT = 9009

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)
print(f"Server listening on {HOST}:{PORT}")

conn, addr = None, None
connection_established = False

# Game setup
grid = Grid()
running = True
player = "X"
turn = True
playing = "True"

# Wait for client
def wait_connect():
    global connection_established, conn, addr
    print("Waiting for connection...")
    conn, addr = sock.accept()
    print(f"[Client connected] {addr}")
    connection_established = True
    grid.game_over = False
    receive_data()

create_thread(wait_connect)

def receive_data():
    global turn, connection_established
    while True:
        try:
            data = conn.recv(1024).decode()
            data = data.split('-')
            x, y = int(data[0]), int(data[1])
            if data[2] == 'Yourturn':
                turn = True
            if data[3] == "False":
                grid.game_over = True
            while playing != "True":
                pass  # Busy wait
            if grid.get_cell_value(x, y) == 0:
                grid.set_cell_value(x, y, "O")
        except:
            print('Remote connection terminated')
            connection_established = False
            grid.clear_grid()
            grid.game_over = True
            create_thread(wait_connect)
            break

surface = pygame.display.set_mode((600, 630))
pygame.display.set_caption('Tic-Tac-Toe: Server')

# Function to display status bar
def status_bar():
    font = pygame.font.Font('assets/04b19.ttf', 16)
    if not connection_established:
        whoturn = "Not connected to opponent"
    elif grid.game_over:
        if grid.winner != 0:
            if player == "X":
                whoturn = "You win | Press ESC to quit"
            else:
                whoturn = "Opponent wins | Press ESC to quit"
        else:
            whoturn = "Game over | Press ESC to quit"
    elif turn:
        whoturn = "Your Turn"
    else:
        whoturn = "Opponent Turn"
    text = font.render(f'Player X | {whoturn}', True, (25, 25, 112))
    textRect = text.get_rect()
    textRect.center = (300, 615)
    surface.blit(text, textRect)

# Mainloop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.display.quit()
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and connection_established:
            if pygame.mouse.get_pressed()[0]:
                if turn and not grid.game_over:
                    pos = pygame.mouse.get_pos()
                    cellx, celly = pos[0] // 200, pos[1] // 200
                    grid.set_mouse_input(cellx, celly, player)
                    if grid.game_over:
                        playing = "False"
                    send_data = '{}-{}-{}-{}'.format(cellx, celly, 'Yourturn', playing).encode()
                    conn.send(send_data)
                    turn = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    surface.fill((250, 128, 114))
    grid.draw(surface)
    status_bar()
    pygame.display.flip()

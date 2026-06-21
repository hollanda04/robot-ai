import pygame 
import sys
import random
import time
import pickle

# mudança de tamanho do mapa
WIDTH, HEIGHT = 100*5, 100*5 # controle do tamanho e largura do mapa
W = 5*5 #controla o tamanho dos corredores
SHOW = True
SAVE_MAZE = True
OUTPUT_IMAGE = True
MAZE_NAME = 'mapa A3' # caso queira criar um mapa novo mude o nome do arquivo senão ira apenas sobreescrever o antigo
DELAY = 0.01 # controla a velocidade de criação, sem ele apenas mostraria o mapa completo e não a sua criação

#configuração dos itens
NUM_DIAMANTE = 15

#constantes responsaveis pela aparencia do labirinto
ROWS = HEIGHT // W
COLS = WIDTH // W
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
BLUE = (255, 210, 0)
outlineThickness = W // 5
T = outlineThickness//2

print(f"numero de colunas: {ROWS}")
print(f"area da superfice: {ROWS*COLS}")

WIDTH, HEIGHT = HEIGHT+W, WIDTH+W

cells = []
stack = []
items = []

pygame.init()
if SHOW:
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
else:
    SCREEN = pygame.Surface((WIDTH, HEIGHT))
pygame.display.set_caption('labirinto')

def returnCellindex(row, col):
    if row < 0 or col < 0 or row > ROWS-1 or col > COLS-1:
        return False
    else:
        return cells [row][col]


class Cell:
    def __init__(self, row, col, lines, inPath, inMaze, highlighted, arrows):
        self.row = row
        self.col = col
        self.lines = lines
        self.inPath = inPath
        self.inMaze = inMaze
        self.highlighted = highlighted
        self.arrows = arrows
    
    def draw(self):
        if self.inMaze:
            pygame.draw.rect(SCREEN, DARK_GREEN, pygame.Rect(self.row*W, self.col*W, W, W))
        if self.highlighted:
            pygame.draw.rect(SCREEN, WHITE, pygame.Rect(self.row*W, self.col*W, W, W))
        if self.lines[0]:
            pygame.draw.line(SCREEN, GREEN, (self.row*W, self.col*W), (self.row*W+W+T, self.col*W), outlineThickness)
        if self.lines[1]:
            pygame.draw.line(SCREEN, GREEN, (self.row*W+W, self.col*W), (self.row*W+W, self.col*W+W+T), outlineThickness)
        if self.lines[2]:
            pygame.draw.line(SCREEN, GREEN, (self.row*W, self.col*W+W), (self.row*W+W+T, self.col*W+W), outlineThickness)
        if self.lines[3]:
            pygame.draw.line(SCREEN, GREEN, (self.row*W, self.col*W), (self.row*W, self.col*W+W+T), outlineThickness)
        
    def checkNearCells(self):
        nearCells = []

        topCell = returnCellindex(self.row-1, self.col)
        rightCell = returnCellindex(self.row, self.col+1)
        bottomCell = returnCellindex(self.row+1, self.col)
        leftCell = returnCellindex(self.row, self.col-1)

        if topCell != False and not(topCell.inMaze):
            nearCells.append(topCell)

        if rightCell != False and not(rightCell.inMaze):
            nearCells.append(rightCell)

        if bottomCell != False and not(bottomCell.inMaze):
            nearCells.append(bottomCell)

        if leftCell != False and not(leftCell.inMaze):
            nearCells.append(leftCell)
        
        if len(nearCells) != 0:
            if len(nearCells) > 1:
                return random.choice(nearCells)
            else:
                return nearCells[0]
        else:
            return False


class Item:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.collected = False
 
    def draw(self):
        if self.collected:
            return
 
        centerX = self.row*W + W//2
        centerY = self.col*W + W//2
 
        pygame.draw.circle(SCREEN, BLUE, (centerX, centerY), W//4)
        

def deleteWalls(currentCell, nextCell):
    x = currentCell.row - nextCell.row

    if x == 1:
        currentCell.lines[3] = False
        nextCell.lines[1] = False
    elif x == -1:
        currentCell.lines[1] = False
        nextCell.lines[3] = False
    
    y = currentCell.col - nextCell.col 
    if y == 1:
        currentCell.lines[0] = False
        nextCell.lines[2] = False
    elif y == -1:
        currentCell.lines[2] = False
        nextCell.lines[0] = False

def save_data():
    with open(f"./A3 sistemas/ {MAZE_NAME}.dat", "wb") as f: #nome do arquivo onde o labirinto sera guardado, mudar para arquivo com nome diferente
        pickle.dump({'cells': cells, 'items': items}, f)

def setUp():
    for i in range(ROWS):
        cells.append([])
        for j in range(COLS):
            cells[i].append(Cell(i,j, [True,True, True, True], False, False, False, [False, False, False, False]))

def spawnItems(numDiamante=NUM_DIAMANTE):
    occupied = {(0, 0)} # a célula inicial (entrada) não recebe itens
 
    placed = 0
    while placed < numDiamante and len(occupied) < ROWS*COLS:
        r = random.randint(0, ROWS-1)
        c = random.randint(0, COLS-1)
        if (r, c) not in occupied:
            occupied.add((r, c))
            items.append(Item(r, c))
            placed += 1

def round_to_tenths(number):
    if number < 10:
        return
    else:
        return (number // 10) + 10
    
def main():
    global SHOW
    global SAVE_MAZE
    global OUTPUT_IMAGE
    global MAZE_NAME
    global DELAY

    setUp()

    current = cells [0][0]
    current.inMaze = True
    current.highlighted = True

    running = True
    print("algoritmo de labirinto iniciado")
    while running:

        next = current.checkNearCells()

        if next != False:
            next.inMaze = True

            stack.append(current)

            deleteWalls(current, next)

            current.highlighted = False
            next.highlighted = True

            current = next
        elif len(stack) > 0:
            current.highlighted = False
            current = stack.pop(len(stack)-1)
            current.highlighted = True
        else:
            print("algoritmo de labirinto finalizado")

            spawnItems()
            print(f"{len(items)} itens espalhados pelo labirinto")

            SCREEN.fill(BLACK)
            for i in range(ROWS):
                for j in range(COLS):
                    cells[i][j].draw()
            for item in items:
                item.draw()

            if SHOW:
                    pygame.display.update()

            if SAVE_MAZE == True:
                print("salvando labirinto")
                save_data()
                SAVE_MAZE = False
                print("labirinto salvo")

            if OUTPUT_IMAGE:
                print("salvando imagem!")
                pygame.image.save(SCREEN, f"./imagems/{MAZE_NAME}.png")
                print("imagem salva!")

            if SHOW:
                print("labirinto pronto! feche a janela para terminar")
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            waiting = False

            running = False
            break

        if SHOW:
            SCREEN.fill(BLACK)
            for i in range(ROWS):
                for j in range(COLS):
                    cells[i][j].draw()
            pygame.display.update()
            if DELAY:
                time.sleep(DELAY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

start = time.time()
main()
end = time.time()
print(f"tempo total: {(end - start)}")
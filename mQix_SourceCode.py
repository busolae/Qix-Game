import pygame
import sys
import math
import random

#pyinstaller mQix.py --onefile --noconsole


# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)



directions = ['L', 'U', 'R', 'D']
dirToVector = {'L': (-1, 0), 'U': (0, -1), 'R': (1, 0), 'D': (0, 1)}
EPSILON = 0.001


def loopList(L, i, j):
    if i >= len(L):
        i = i%len(L)
    if i >= j:
        return L[i:] + L[:j]
    return L[i:j]

def getDir(v1, v2):
    #print(v1, v2)
    dx = v2[0]-v1[0]
    dy = v2[1]-v1[1]
    if dy == 0:
        if dx > 0:
            return 'R'
        else:
            return 'L'
    elif dx == 0:
        if dy > 0:
            return 'D'
        else:
            return 'U'
    print("value error: ", v1, v2)
    raise ValueError

def calcArea(vertices):
    n = len(vertices)
    area = 0.0
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        area += (x1 * y2 - x2 * y1)
    return abs(area) / 2.0

class textObject:
    def __init__(self, text, position, colour=(0, 0, 0), font=None):
        self.font = font
        if font is None:
            self.font = pygame.font.Font(None, 30)   
        self.colour = colour
        self.surface = self.font.render(text, True, self.colour)
        self.position = position

    def updateText(self, text):
        self.surface = self.font.render(text, True, self.colour)

class Qix:
    def __init__(self, pos):
        self.pos = pos

class Field:
    def __init__(self, vertices):
        self.goal = 0.3
        
        self.vertices = vertices
        self.startArea = calcArea(self.vertices)
        self.currentArea = self.startArea
        self.percentArea = self.currentArea / self.startArea * 100        

    def updateArea(self):
        self.currentArea = calcArea(self.vertices)
        self.percentArea = self.currentArea / self.startArea * 100
        if (self.currentArea / self.startArea) < self.goal:
            print("You Win")
            # winText = textObject("You Win", (400, 300), (255, 0, 0))
            # textObjects.append(winText)


class Sparx:
    def __init__(self, currentVertexIndex):
        self.radius = 5
        self.color = (51, 51, 255)
        self.velocity = 0.03
        self.direction = random.randint(1,2)

        self.prevVertexIndex = currentVertexIndex
        self.prevVertexPreMerge = f.vertices[self.prevVertexIndex]
        self.pos = list(f.vertices[currentVertexIndex])
        self.prevPos = self.pos[:]
        self.moving_clockwise = False
        self.moving_counterclockwise = False
        self.pushDirection = ""
        self.newPushDirection = ""
        self.pushAcc = []


    def getNextVertex(self):
        return f.vertices[(self.prevVertexIndex + 1) % len(f.vertices)]


    def draw(self, screen):
        if self.pushDirection != "":
            for i in range(len(self.pushAcc)-1):
                pygame.draw.line(screen, (0, 0, 255), self.pushAcc[i], self.pushAcc[i+1])
            pygame.draw.line(screen, (0, 0, 255), self.pushAcc[-1], (round(self.pos[0]), round(self.pos[1])))        
        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)


    def move(self):
        if self.direction == 1:
            self.move_clockwise()
        else:
            self.move_counterclockwise()


    def move_clockwise(self):
        target_x, target_y = self.getNextVertex()
        dx, dy = target_x - self.pos[0], target_y - self.pos[1]
        distance_to_target = math.sqrt(dx ** 2 + dy ** 2)
        if distance_to_target > self.velocity:
            angle = math.atan2(dy, dx)
            self.pos[0] += self.velocity * math.cos(angle)
            self.pos[1] += self.velocity * math.sin(angle)
        else:
            self.pos[0], self.pos[1] = target_x, target_y
            self.prevVertexIndex = (self.prevVertexIndex + 1) % len(f.vertices)


    def move_counterclockwise(self):
        target_x, target_y = f.vertices[self.prevVertexIndex]
        dx, dy = target_x - self.pos[0], target_y - self.pos[1]
        distance_to_target = math.sqrt(dx ** 2 + dy ** 2)
        if distance_to_target > self.velocity:
            #unnecessary math
            angle = math.atan2(dy, dx)
            self.pos[0] += self.velocity * math.cos(angle)
            self.pos[1] += self.velocity * math.sin(angle)
        else:
            self.pos[0], self.pos[1] = target_x, target_y
            self.prevVertexIndex = (self.prevVertexIndex - 1) % len(f.vertices)

class Player:
    def __init__(self, currentVertexIndex):
         # Adjust as needed
        self.radius = 5
        self.color = (255, 0, 0)
        self.velocity = 0.05

        self.prevVertexIndex = currentVertexIndex
        self.pos = list(f.vertices[currentVertexIndex])
        self.prevPos = self.pos[:]
        self.moving_clockwise = False
        self.moving_counterclockwise = False
        self.pushDirection = ""
        self.newPushDirection = ""
        self.pushAcc = []

    def getNextVertex(self):
        return f.vertices[(self.prevVertexIndex + 1) % len(f.vertices)]

    def draw(self, screen):
        if self.pushDirection != "":
            for i in range(len(self.pushAcc)-1):
                pygame.draw.line(screen, (0, 0, 255), self.pushAcc[i], self.pushAcc[i+1])
            pygame.draw.line(screen, (0, 0, 255), self.pushAcc[-1], (round(self.pos[0]), round(self.pos[1])))        
        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)

    def move(self):
        if self.pushDirection != "":
            if self.newPushDirection != "":
                self.continuePush(self.newPushDirection)
        elif self.moving_clockwise:
            self.move_clockwise()
        elif self.moving_counterclockwise:
            self.move_counterclockwise()

    def move_clockwise(self):
        target_x, target_y = self.getNextVertex()
        dx, dy = target_x - self.pos[0], target_y - self.pos[1]
        distance_to_target = math.sqrt(dx ** 2 + dy ** 2)
        if distance_to_target > self.velocity:
            angle = math.atan2(dy, dx)
            self.pos[0] += self.velocity * math.cos(angle)
            self.pos[1] += self.velocity * math.sin(angle)
        else:
            self.pos[0], self.pos[1] = target_x, target_y
            self.prevVertexIndex = (self.prevVertexIndex + 1) % len(f.vertices)

    def move_counterclockwise(self):
        target_x, target_y = f.vertices[self.prevVertexIndex]
        dx, dy = target_x - self.pos[0], target_y - self.pos[1]
        distance_to_target = math.sqrt(dx ** 2 + dy ** 2)
        if distance_to_target > self.velocity:
            #unnecessary math
            angle = math.atan2(dy, dx)
            self.pos[0] += self.velocity * math.cos(angle)
            self.pos[1] += self.velocity * math.sin(angle)
        else:
            self.pos[0], self.pos[1] = target_x, target_y
            self.prevVertexIndex = (self.prevVertexIndex - 1) % len(f.vertices)

    def isItValidPushDirection(self, direction):
        #return false if on a vertex
        self.pos = [round(self.pos[0]), round(self.pos[1])]
        if self.pos[0] == f.vertices[self.prevVertexIndex][0] and self.pos[1] == f.vertices[self.prevVertexIndex][1]: return ""
       
        x, y = f.vertices[(self.prevVertexIndex + 1) % len(f.vertices)]
        #check if the direction is the direction yielded from turning right when facing next vertex
        if direction == 'U' and self.pos[0] > x:
            self.pushAcc.append((round(self.pos[0]), round(self.pos[1])))
            return 'U'
        elif direction == 'D' and self.pos[0] < x:
            self.pushAcc.append((round(self.pos[0]), round(self.pos[1])))
            return 'D'
        elif direction == 'L' and self.pos[1] < y:
            self.pushAcc.append((round(self.pos[0]), round(self.pos[1])))
            return 'L'
        elif direction == 'R' and self.pos[1] > y:
            self.pushAcc.append((round(self.pos[0]), round(self.pos[1])))
            return 'R'
        return ""
    
    def continuePush(self, direction):
        if self.pushDirection == direction:
            # Get the vector corresponding to the direction
            vector = dirToVector[direction]
            self.pos[0] += self.velocity * vector[0]
            self.pos[1] += self.velocity * vector[1]
        else:
            self.pushAcc.append((round(self.pos[0]), round(self.pos[1])))
            self.pushDirection = direction
            self.continuePush(direction)

        if len(self.pushAcc) > 0:
            for i in range(len(f.vertices)):
                v1 = f.vertices[i]
                v2 = f.vertices[(i+1) % len(f.vertices)]
                if line_intersection((v1, v2), (self.pushAcc[-1], self.pos)) != None:
                    print("Intersection detected!")
                    if v1[0] == v2[0]: self.pos[0] = v1[0]
                    elif v1[1] == v2[1]: self.pos[1] = v1[1]
                    else: raise ValueError 
                    self.pushAcc.append((round(self.pos[0]), round(self.pos[1])))
                    
                    print("acc: ", self.pushAcc)

                    for sparx in sparxs:
                        if sparx.direction == 1:
                            sparx.prevVertexPreMerge = f.vertices[sparx.prevVertexIndex]
                        else: sparx.prevVertexPreMerge = f.vertices[(sparx.prevVertexIndex + 1) % len(f.vertices)]
                    merge(self.prevVertexIndex, i, self.pushAcc)
                    self.prevVertexIndex = f.vertices.index(self.pushAcc[-1])
                    for sparx in sparxs:
                        try:
                            getDir(self.pushAcc[0], sparx.prevVertexPreMerge)
                            tVertex = self.pushAcc[0]
                            print("efefe")
                        except:
                            tVertex = self.pushAcc[-1]
                        if sparx.prevVertexPreMerge in f.vertices:
                            if sparx.direction == 1:
                                sparx.prevVertexIndex = f.vertices.index(sparx.prevVertexPreMerge)
                            else: sparx.prevVertexIndex = f.vertices.index(sparx.prevVertexPreMerge) - 1
                        else: sparx.prevVertexIndex = f.vertices.index(tVertex)
                        #else: sparx.prevVertexIndex = f.vertices.index(self.pushAcc[-1])
                    self.pushDirection = ""
                    self.newPushDirection = ""
                    self.pushAcc = []
                    break
            
            for i in range(len(self.pushAcc)-1):
                v1 = self.pushAcc[i-1]
                v2 = self.pushAcc[i]
                if line_intersection((v1, v2), (self.pushAcc[-1], self.pos)) != None:
                    self.cancelPush()
                    break
    
    def cancelPush(self):
        self.pushDirection = ""
        self.newPushDirection = ""
        self.pos = list(self.pushAcc[0])
        self.pushAcc = []

def line_intersection(line1, line2):
    x1, y1 = line1[0]
    x2, y2 = line1[1]
    x3, y3 = line2[0]
    x4, y4 = line2[1]

    # Calculate the slopes of the lines
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    
    # If the lines are parallel or coincident, return None (no intersection)
    if denom == 0:
        return None
    
    # Calculate the intersection point coordinates
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom
    
    if (round(px), round(py)) == (x3, y3):
        return None

    # Check if the intersection point lies within both line segments
    if (min(x1, x2) <= px <= max(x1, x2) and min(y1, y2) <= py <= max(y1, y2) and
        min(x3, x4) <= px <= max(x3, x4) and min(y3, y4) <= py <= max(y3, y4)):
        
        return px, py
    else:
        return None


def isClockwise(vertices):
    n = len(vertices)
    if n < 3:
        # A polygon with less than 3 vertices is not valid
        return False

    area = 0
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        area += (x2 - x1) * (y2 + y1)

    return area < 0

def merge(edge1, edge2, tail):
    op1 = []
    op2 = []
    vert1 = []
    vert2 = []
    if edge1 == edge2:
        op1 = tail[:]
        if isClockwise(tail):
            tail = tail[::-1]
        op2 = loopList(f.vertices, edge1+1, edge2+1) + tail
    else:
        vert1 = loopList(f.vertices, edge1+1, edge2+1)
        vert2 = loopList(f.vertices, edge2+1, edge1+1)
        op1 = tail[:] + vert2
        op2 = tail[::-1] + vert1
    
    if not isClockwise(op1):
        op1 = op1[::-1]
    if not isClockwise(op2):
        op2 = op2[::-1]
    
    if isInsidePolygon(qix.pos, op1):
        f.vertices = op1[:]
    else:
        f.vertices = op2[:]

    
    print("L: ", f.vertices)
    f.updateArea()



def isInsidePolygon(pos, L):
    # Ray casting algorithm to check if a point is inside a polygon
    count = 0
    x = pos[0]
    y = pos[1]
    for i in range(len(L)):
        v1 = L[i]
        v2 = L[(i + 1) % len(L)]
        if ((v1[1] <= y) != (v2[1] <= y)) and (x < (v2[0] - v1[0]) * (y - v1[1]) / (v2[1] - v1[1]) + v1[0]):
            count += 1
    return count % 2 == 1

# Initialize Pygame
pygame.init()

# Set up font
pygame.font.init()

# Set up display
ScreenDimensions = (800, 600)
screen = pygame.display.set_mode(ScreenDimensions)

# Create instances
f = Field([(100, 100), (400, 100), (400, 400), (100, 400)])
player = Player(0)
qix = Qix((300, 300))
sparxs = [Sparx(3), Sparx(2)] 

# List of textObjects
areaText = textObject("Area: " + str(round(f.percentArea, 2)) + "%", (500, 200))
textObjects = [areaText]
textObjects.append(textObject("Use A and D to move clockwise", (450, 100)))
textObjects.append(textObject("and counter-clockwise", (450, 120)))
textObjects.append(textObject("Use Arrow keys to capture territory", (450, 160)))



def handleEvents():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # will break main loop
            return False
        elif event.type == pygame.KEYDOWN:
            if player.pushDirection == "":
                if event.key == pygame.K_d:
                    player.moving_clockwise = True
                elif event.key == pygame.K_a:
                    player.moving_counterclockwise = True
                elif event.key == pygame.K_UP:
                    player.pushDirection = player.isItValidPushDirection('U')
                    player.newPushDirection = 'U'
                elif event.key == pygame.K_DOWN:
                    player.pushDirection = player.isItValidPushDirection('D')
                    player.newPushDirection = 'D'
                elif event.key == pygame.K_LEFT:
                    player.pushDirection = player.isItValidPushDirection('L')
                    player.newPushDirection = 'L'
                elif event.key == pygame.K_RIGHT:
                    player.pushDirection = player.isItValidPushDirection('R')
                    player.newPushDirection = 'R'
            else:
                if event.key == pygame.K_UP and player.pushDirection != 'D':
                    player.newPushDirection = 'U'
                elif event.key == pygame.K_DOWN and player.pushDirection != 'U':
                    player.newPushDirection = 'D'
                elif event.key == pygame.K_LEFT and player.pushDirection != 'R':
                    player.newPushDirection = 'L'
                elif event.key == pygame.K_RIGHT and player.pushDirection != 'L':
                    player.newPushDirection = 'R'
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                player.moving_clockwise = False
            elif event.key == pygame.K_a:
                player.moving_counterclockwise = False
            if event.key == pygame.K_UP and player.newPushDirection == 'U':
                player.newPushDirection = ""
            elif event.key == pygame.K_DOWN and player.newPushDirection == 'D':
                player.newPushDirection = ""
            elif event.key == pygame.K_LEFT and player.newPushDirection == 'L':
                player.newPushDirection = ""
            elif event.key == pygame.K_RIGHT and player.newPushDirection == 'R':
                player.newPushDirection = ""
    return True


# Main loop
while True:
    if not(handleEvents()): break

    # Fill the screen with white
    screen.fill(WHITE)

    # Draw the filled polygon
    pygame.draw.polygon(screen, BLACK, f.vertices)

    # Move the player along the edge
    player.move()
    for sparx in sparxs:
        sparx.move()

    # Draw the player
    player.draw(screen)
    # Draw the Qix
    pygame.draw.circle(screen, WHITE, (qix.pos[0], qix.pos[1]), 10)
    #Draw the sparx
    for sparx in sparxs:
        sparx.draw(screen)

    # Update Area Text
    areaText.updateText("Area: " + str(round(f.percentArea, 2)) + "%") 
    
    for textObject in textObjects:
        screen.blit(textObject.surface, textObject.position)


    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
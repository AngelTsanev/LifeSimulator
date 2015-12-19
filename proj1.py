import time
from random import randint as rand
from rgbmatrix import RGBMatrix
from rgbmatrix import graphics

N = 64
M = 32


Matrix = RGBMatrix(32, 2, 1)
Matrix.pwmBits = 11
Matrix.brightness = 100

R = rand(0,20)

# generate board and food
class BF:
        """This is a Board Field"""
        def __init__ (self, food, Ids):
                self.food = food
                self.Ids = Ids

        def colorize(self, x, y):
                if self.food == 0 and (not self.Ids):
                        Matrix.SetPixel(x, y, 0, 0, 0)

                elif self.food > 0 and (not self.Ids):
                        Matrix.SetPixel(x, y, 100, 255, 100)

                elif len(self.Ids) > 1:
                        Matrix.SetPixel(x, y, 255, 255, 0)

                elif self.Ids[0].sex == 0:
                        Matrix.SetPixel(x, y, 255, 100, 100)

                else:
                        Matrix.SetPixel(x, y, 100, 100, 255)

B = []

for i in range(N):
        B.append([])
        for j in range(M):
                B[i].append(BF(0,[]))

for i in range(10):
        x = rand(0,N-1)
        y = rand(0,M-1)
        B[x][y].food = 50

class Id:
        def __init__ (self, sex, race, age, fitness, health, x, y):
                self.sex = sex
                self.race = race
                self.age = age
                self.fitness = fitness
                self.health = health
                self.x = x
                self.y = y

        def Step(self):
                x = self.x
                y = self.y
                
                Temp = []
                if (x + 1 < N): Temp.append((x+1,y))
                if (x - 1 >= 0): Temp.append((x-1,y))
                if (y + 1 < M): Temp.append((x,y+1))
                if (y - 1 >= 0): Temp.append((x,y-1))

                next = Temp[rand(0,len(Temp) - 1)]

                B[x][y].Ids.remove(self)
                B[next[0]][next[1]].Ids.append(self)
                if B[next[0]][next[1]].food > 0:
                        B[next[0]][next[1]].food -= 1
                        self.health = min(100, self.health + 10)

                B[x][y].colorize(x,y)
                B[next[0]][next[1]].colorize(next[0],next[1])

                self.x = next[0]
                self.y = next[1]

#generate id-s  
IDs = []
P = 100

for i in range(P):
        x = rand(0,N-1)
        y = rand(0,M-1)

        IDs.append(Id(rand(0,1), R, 1, rand(0,100), rand(0,100), x, y))
        B[x][y].Ids.append(IDs[-1])


def print_board(k):
        f = open('step' + str(k) + '.txt','w+')

        for i in range(N):
                for j in range(M):
                        if not B[i][j].Ids:
                                f.write(str(B[i][j].food))
                        else:
                                f.write('F' if B[i][j].Ids[0].sex == 0 else 'M')
                        f.write('\t')
                f.write('\n')

for i in range(1000):
        #print_board(i)

        for j in range(P):
                IDs[j].Step()
        time.sleep(0.5)

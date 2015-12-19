import time
from rgbmatrix import RGBMatrix
from rgbmatrix import graphics
from random import randint as rand

N = 64
M = 32

Matrix = RGBMatrix(32, 2, 1)
Matrix.pwmBits = 11
Matrix.brightness = 100

R = rand(0,20)

# generate board and food
B = []

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

for i in range(N):
        B.append([])
        for j in range(M):
                B[i].append(BF(0,[]))

for i in range(10):
        x = rand(0,N-1)
        y = rand(0,M-1)
        B[x][y].food = 50

# generate population
IDs = []
P = 100

class Id:
        def __init__ (self, sex, race, age, fitness, health, x, y, status, last2):
            self.sex = sex
            self.race = race
            self.age = age
            self.fitness = fitness
            self.health = health
            self.x = x
            self.y = y
            self.status = status
            self.last2 = last2

        def Step(self):
            x = self.x
            y = self.y
            
            # find next field and remove from current field
            Temp = []
            if (x + 1 < N and (x+1,y) not in self.last2): Temp.append((x+1,y))
            if (x - 1 >= 0 and (x-1,y) not in self.last2): Temp.append((x-1,y))
            if (y + 1 < M and (x,y+1) not in self.last2): Temp.append((x,y+1))
            if (y - 1 >= 0 and (x,y-1) not in self.last2): Temp.append((x,y-1))
            
            next = Temp[rand(0,len(Temp) - 1)]
            
            self.last2.append(next)
            if len(self.last2) > 2: self.last2.pop(0)
            
            nx = next[0]
            ny = next[1]
            
            B[x][y].Ids.remove(self)
            
            # search for partner
            if self.age > 10:
                for it in B[nx][ny].Ids:
                    if it.sex == 1 - self.sex and it.fitness >= self.fitness//2: break
                else: it = None
            
                if it:
                    IDs.append(Id(rand(0,1), R, 1, (it.fitness + self.fitness)//2, rand(0,100), nx, ny, 1, []))
                    B[nx][ny].Ids.append(IDs[-1])
            
            # check for food
            if B[nx][ny].food > 0:
                B[nx][ny].food -= 1
                self.health = min(100, self.health + 11)
            
            # update self
            self.x = nx
            self.y = ny
            
            self.age += 1
            self.health -= 1
            
            B[nx][ny].Ids.append(self)
            
            if (self.age > 100 or self.health < 1): self.status = -1
            
            # colorize the fields
            B[x][y].colorize(x,y)
            B[nx][ny].colorize(nx,ny)
            
for i in range(P):
        x = rand(0,N-1)
        y = rand(0,M-1)

        IDs.append(Id(rand(0,1), R, 1, rand(0,100), rand(0,100), x, y, 1, []))
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

for i in range(20):
        #print_board(i)
        
        j = 0
        while j < len(IDs):
            IDs[j].Step()
            if (IDs[j].status == -1): IDs.pop(j)
            else: j += 1
            
        time.sleep(0.2)

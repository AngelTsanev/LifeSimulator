import time, socket, json
from rgbmatrix import RGBMatrix
from rgbmatrix import graphics
from random import randint as rand
from config import *

N = 64
M = 32

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('192.168.1.6', 7878)
sock.setblocking(False)
sock.bind(server_address)

sock.listen(1)

Matrix = RGBMatrix(32, 2, 1)
Matrix.pwmBits = 11
Matrix.brightness = 100

R = rand(0,20)

MR = rand(50, 150)
MG = rand(50, 150)
MB = rand(50, 150)

FR = MR + 100
FG = MG + 100
FB = MB + 100

def sendData(data):
        sock.sendall(json.dumps(data.to_JSON()))

def recieveData():
        recieved_data = ''
        try:
            conn, addr = sock.accept()
            #if(conn): return
            #while True:
            data = conn.recv(1024000)
            #        if data:
            #print data
            recieved_data += data
        #        else: break
        except:
            pass
        #finally:
        #    conn.close()
        print recieved_data
        return recieved_data

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
                Matrix.SetPixel(x, y, FR, FG, FB)
            else: Matrix.SetPixel(x, y, MR, MG, MB)

        def to_dict(self):
            return self.__dict__

for i in range(N):
        B.append([])
        for j in range(M):
                B[i].append(BF(0,[]))

for i in range(10):
        x = rand(0,N-1)
        y = rand(0,M-1)
        B[x][y].food = INIT_FOOD
        B[x][y].colorize(x,y)

# generate population
IDs = []

class Id:
        def __init__ (self, sex, race, age, fitness, health, x, y, status, mate_stat, last2):
            self.sex = sex
            self.race = race
            self.age = age
            self.fitness = fitness
            self.health = health
            self.x = x
            self.y = y
            self.status = status
            self.mate_stat = mate_stat
            self.last2 = last2

        def to_dict(self):
            return self.__dict__

        def to_JSON(self):
            return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

            
        def Step(self):
            x = self.x
            y = self.y
            
            # find next field and remove from current field
            Temp = []
            if (x + 1 < N and (x+1,y) not in self.last2): Temp.append((x+1,y))
            if (x - 1 >= 0 and (x-1,y) not in self.last2):
                Temp.append((x-1,y))
            elif(x - 1 < 0):
                Temp.append((x-1,y))
            if (y + 1 < M and (x,y+1) not in self.last2): Temp.append((x,y+1))
            if (y - 1 >= 0 and (x,y-1) not in self.last2): Temp.append((x,y-1))
            
            next = Temp[rand(0,len(Temp) - 1)]
            
            self.last2.append(next)
            if len(self.last2) > 2: self.last2.pop(0)
            
            nx = next[0]
            ny = next[1]
	    
            B[x][y].Ids.remove(self)
            # search for partner
            if self.age > MATE_AGE and self.mate_stat > MATE_STAT:
                for it in B[nx][ny].Ids:
                    if it.age > MATE_AGE and it.mate_stat > MATE_STAT and it.sex == 1 - self.sex and it.fitness >= self.fitness//2: break
                else: it = None
            
                if it:
                    self.mate_stat = 0
                    it.mate_stat = 0
                    IDs.append(Id(rand(0,1), R, 1, (it.fitness + self.fitness)//2, rand(0,100), nx, ny, 1, 0, []))
                    B[nx][ny].Ids.append(IDs[-1])
     
            # check for food
            if B[nx][ny].food > 0:
                B[nx][ny].food -= 1
                self.health = min(100, self.health + 11)
            
            # update self and new field
            self.x = nx
            self.y = ny
            
            self.age += 1
            self.health -= 1
            self.mate_stat += 1
            
            if (self.age > MAX_AGE or self.health < 1): self.status = -1
            else: B[nx][ny].Ids.append(self)
            
            B[nx][ny].colorize(nx,ny)
            # colorize the fields
            B[x][y].colorize(x,y)
            
for i in range(POPULATION):
        x = rand(0,N-1)
        y = rand(0,M-1)

        IDs.append(Id(rand(0,1), R, 1, rand(0,100), rand(0,100), x, y, 1, 0, []))
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
        t = []
        for j in range(len(IDs)):
            data = recieveData()
            if(data != ''):
                object = json.loads(json.loads(data))
                t.append(Id(object["sex"], object["race"], object["age"], object["fitness"], object["health"], object["x"], object["y"], object["status"], object["mate_stat"], object["last2"]))
                B[t[-1].x][t[-1].y].Ids.append(t[-1])
            IDs[j].Step()
        for j in range(len(t)):
            t[j].Step()
            IDs.append(t[j])
        
        IDs = filter(lambda x: x.status != -1, IDs)
        
        time.sleep(0.2)


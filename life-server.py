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
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(server_address)

sock.listen(1)

#try:
#	conn, addr = sock.accept()
#except socket.error, e:
#        print time.clock(), e


Matrix = RGBMatrix(32, 2, 1)
Matrix.pwmBits = 11
Matrix.brightness = 100



R = rand(0,2)

def parse(data):
	data = data.split(',')
	data = map(lambda x: int(x), data)
	return Id(data[0], data[1], data[2], data[3], data[4], data[5], data[6], 0, data[7], [])

def sendData(data):
        sock.sendall(json.dumps(data.to_JSON()))

def recieveData():
        recieved_data = ''
	#conn, addr = sock.accept()
        try:
	    #global conn
            conn, addr = sock.accept()
#	    conn.setblocking(False)
            print addr
	    #if(conn): return
            #while True:
#	    conn.setblocking(0.4)
            data = conn.recv(1024)
            #        if data:
            print data
            recieved_data += data
       	    conn.close()
 	    #else: break
	    #conn.send("alive")
        except socket.error, e:
            #pass
	    #conn.close()
	    print time.clock(), e
        #else:
	    #print data
	    #recieved_data += data
	#finally:
        #    conn.close()
        #print recieved_data
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
                Matrix.SetPixel(x, y, 0, 155, 00)
            elif len(self.Ids) > 1:
                Matrix.SetPixel(x, y, 255, 255, 0)
            else:
                Matrix.SetPixel(x, y, RaceColors[self.Ids[0].race][self.Ids[0].sex][0], RaceColors[self.Ids[0].race][self.Ids[0].sex][1], RaceColors[self.Ids[0].race][self.Ids[0].sex][2])

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
                    IDs.append(Id(rand(0,1), R, 1, (it.fitness + self.fitness)//2, rand(100, 200), nx, ny, 1, 0, []))
                    B[nx][ny].Ids.append(IDs[-1])
     
            # check for food
            if B[nx][ny].food > 0:
                B[nx][ny].food -= 1
                self.health = min(200, self.health + 11)

	    # FIGHT
	    for other in B[nx][ny].Ids:
    		if self.race != other.race:
        	    if self.fitness >= other.fitness:
           		other.status = -1
           		self.health = self.health // 2
            		self.fitness += 2
        	    else:
            	   	self.status = -1
            	    	other.health = other.health // 2
            	    	other.fitness += 2
		    break
            
            # update self and new field
            self.x = nx
            self.y = ny
            
            self.age += 1
            self.health -= 1
            self.mate_stat += 1
            
            if (self.age > MAX_AGE or self.health < 1): self.status = -1
            if (self.status != -1): B[nx][ny].Ids.append(self)
            
            B[nx][ny].colorize(nx,ny)
            # colorize the fields
            B[x][y].colorize(x,y)
            
for i in range(POPULATION):
        x = rand(0,N-1)
        y = rand(0,M-1)

        IDs.append(Id(rand(0,1), R, 1, rand(0,100), rand(100, 200), x, y, 1, 0, []))
        B[x][y].Ids.append(IDs[-1])


while True:
#	sock.send("alive")
#for i in range(1000):
        #print_board(i)
        t = []
	data = recieveData()
        if(data != ''):
            #object = json.loads(json.loads(data))
            #t.append(Id(object["sex"], object["race"], object["age"], object["fitness"], object["health"], object["x"], object["y"], object["status"], object["mate_stat"], object["last2"]))
	    t.append(parse(data))        
	    B[t[-1].x][t[-1].y].Ids.append(t[-1])
        for j in range(len(IDs)):
        #    data = recieveData()
        #    if(data != ''):
        #        object = json.loads(json.loads(data))
        #        t.append(Id(object["sex"], object["race"], object["age"], object["fitness"], object["health"], object["x"], object["y"], object["status"], object["mate_stat"], object["last2"]))
        #        B[t[-1].x][t[-1].y].Ids.append(t[-1])
            IDs[j].Step()
        for j in range(len(t)):
            t[j].Step()
            IDs.append(t[j])
        
        IDs = filter(lambda x: x.status != -1, IDs)
        
        time.sleep(0.4)
#	sock.send("alive")

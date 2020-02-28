import random
import math
time=0
txt=open('C:\Users\luca\Downloads\processing-3.5.4-windows64\log.txt','w')
class Virus:
    
        def __init__(self,spread,mort,giorni, contagCoeff=1):
            self.spread=spread
            self.mort=mort
            self.giorni=giorni
            self.contagCoeff=contagCoeff
        def __repr__(self):
            return str([self.spread,self.mort])

class Person:
    def __init__(self,Life, Pos, V, isSick, reckless,virus=None,isImmune=False, giorno=0):
        self.Life=Life #la vita massima
        self.giorno=giorno #quando si è ammalato
        self.isImmune=isImmune #se è immune
        self.V=V #la velocità iniziale
        self.Health=Life #la vita  nel momento attuale
        self.Pos=Pos #la posizione
        self.isSick=isSick #Bool per capire se è malato
        self.reckless=reckless #quanto è spericolato
        self.virus=virus #il virus che lo ha infettato
    def Act(self,NearPeople,giorno):
        ''' fa compiere un movimento alla persona:
            - se non è malata, cerca di allontanarsi dai malati se sono vicini
              guardando il livello di vita di chi le sta vicino (p.Health/p.Life) 
              e agendo secondo il proprio livello di spericolatezza (reckless)
              se non vi sono malati vicini compie una mossa casuale
            - se è malata invece  ha una probabilità di infettare chi le sta accanto
              proporzionale al coefficiente di diffusione del virus (virus.spread)

        '''
        
        vx,vy=0,0
        if NearPeople and not self.isImmune:

            if(not (self.isSick and self.virus)):
                F=filter(lambda x: x.isSick and x.Health/float(x.Life)<self.reckless, NearPeople)
                if F:
                    for p in F:
                        if math.sqrt((self.Pos[0]-p.Pos[0])**2+(self.Pos[1]-p.Pos[1])**2)<15:
                            a=self.Gradient(p)
                            vx-=a[0]
                            vy-=a[1]
                else:
                    vx=random.uniform(-1,1)
                    vy=random.uniform(-1,1)
               

            else:

                for p in list(filter(lambda x: not x.isSick and not x.isImmune,NearPeople)):
                    if math.sqrt((self.Pos[0]-p.Pos[0])**2+(self.Pos[1]-p.Pos[1])**2)<10:
                        if(random.uniform(0,1)<self.virus.spread and self.Health/self.Life<=self.virus.contagCoeff):
                            p.isSick=True
                            p.giorno=giorno
                    if p.Health/float(p.Life)<self.reckless:
                        a=self.Gradient(p)
                        vx-=a[0]
                        vy-=a[1]
                    else:
                        vx=random.uniform(-1,1)
                        vy=random.uniform(-1,1)


                
        else:
            
            vx=random.uniform(-1,1)
            vy=random.uniform(-1,1)
        
        vx=vx*0.2
        vy=vy*0.2
        self.V[0]+=vx
        self.V[1]+=vy
        self.V[0]=self.V[0]/math.sqrt(self.V[0]**2+self.V[1]**2)
        self.V[1]=self.V[1]/math.sqrt(self.V[0]**2+self.V[1]**2)
        self.V[0]*=self.Health/float(self.Life)
        self.V[1]*=self.Health/float(self.Life)
        self.Pos[0]+=self.V[0]*0.3
        self.Pos[1]+=self.V[1]*0.3
    
    def Gradient(self,other):
        ''' steepest descent, pesata in modo tale che in caso di punti sella continui
            scenda comunque
            Determina la direzione e la velocità dell'individuo a seconda dei malati vicini
            a cui è associato una funzione 1/d^2 con d distanza tra individuo e infetto
        '''
        x=self.Pos[0]
        y=self.Pos[1]
        p=other.Pos
        vx=0
        vy=0
        vx+=-4*((x-p[0])/50.0)/(1+((x-p[0])/50.0)**2+((y-p[1])/50.0)**2)**2
        #vx+=-10*((10+x-p[0])/50.0)/(0.01+((10+x-p[0])/50.0)**2+((y-p[1])/50.0)**2)**2
        vx=vx/2
        vy+=-4*((y-p[1])/50.0)/(1+((x-p[0])/50.0)**2+((y-p[1])/50.0)**2)**2
        #vy+=-10*((10+y-p[1])/50.0)/(0.01+((x-p[0])/50.0)**2+((10+y-p[1])/50.0)**2)**2
        vy=vy/2
        return vx,vy
    def pr(self):
        ''' Disegna un individuo con colore che dipende dalla salute
        '''
        N=map(self.Health/float(self.Life),0,1,0,255)
        fill(255-N,N,0)
        if(self.isSick):
            stroke(0,0,0)
        elif(self.isImmune):
            fill(0,0,0)
        else:
            noStroke()
        ellipse(self.Pos[0],self.Pos[1],6,6)
        
    def NearPeople(self, people):
        '''seleziona le persone vicine'''
        D=[]
        for i in range(-1,2):
            for j in range(-1,2):
                D.extend(people[(int(self.Pos[0]/20) +i)%32][(int(self.Pos[1]/20)+j)%32])
        return D
    def __repr__(self):
        return str([self.Health, self.Life,self.isSick, self.reckless,self.virus])

class City:
    ''' una città con un certo numero di individui '''
    def __init__(self,NPeople,avLife,avReckless, virus, response):
        self.grid=[[[] for j in range(32)] for i in range(32)]
        self.virus=virus
        self.response=response
        self.avLife=avLife
        self.avReckless=1-avReckless
        self.People=[]
        for i in range(NPeople):
            a=abs(random.gauss(avLife,30))
            b=abs(random.gauss(avReckless,0.1))
            self.People.append(Person(a,[random.uniform(0,640),random.uniform(0,640)],[random.uniform(-1,1),random.uniform(-1,1)],False,b))
        self.alive=len(self.People)
        self.death=0
        self.sick=0
        self.immune=0
    def updateGrid(self):
        I=[[[] for j in range(32)] for i in range(32)]
        for i in self.People:
            I[int(i.Pos[0]/20)][int(i.Pos[1]/20)].append(i)
        self.grid=I
    
    def Repos(self):
        for p in self.People:
            p.Pos[0]=p.Pos[0]%640
            p.Pos[1]=p.Pos[1]%640
            
        
    def checkSick(self):
        '''aggiorna il numero di malati'''
        N=0
        G=0
        for p in self.People:
            #if p.isSick:
                #print(str(p.Health))
            if p.isImmune:
                G+=1
            if p.isSick:
                N+=1
                if p.isSick and not p.virus:
                    
                    p.virus=Virus(abs(random.gauss(self.virus.spread,0.1)),abs(random.gauss(self.virus.mort, 0.01)),self.virus.giorni,self.virus.contagCoeff)
               # print([p.virus.spread,p.virus.mort])
        self.sick=N
        self.immune=G
    def checkPeople(self):
        ''' aggiorna il numero di persone morte e vive '''
        NewP=[]
        for p in self.People:
            if not p.Health<=0:
                NewP.append(p)

        self.People=NewP
        alive=len(self.People)
        self.death+=self.alive-alive
        self.alive=alive
    
    def Act(self,giorno):
        ''' fa compiere un movimento alle singole persone della città'''
  
        for p in self.People:
            p.Act(p.NearPeople(self.grid),giorno)
        self.checkPeople()
        self.checkSick()
        self.Repos()
        self.updateGrid()
        self.pr()
    
        
    def pr(self):
        ''' disegna tutti gli indivdui'''
        for p in self.People:
            p.pr()
    def AddSick(self):
        ''' aggiunge un malato alla popolazione'''
        a=abs(random.gauss(self.avLife,20))
        b=abs(random.gauss(self.avReckless,0.1))
        self.People.append(Person(a,[random.uniform(0,640),random.uniform(0,640)],[random.uniform(-1,1),random.uniform(-1,1)],True,b,self.virus))
        self.sick+=1
        self.alive+=1
class World:
    def __init__(self,cities,virus):
        global time
        self.cities=cities
        self.virus=virus
        self.giorno=time/60
    
    def checkGiorno(self):
        global time
        if time/60>self.giorno:
            self.giorno+=1
        if time%60==0:
            return True
        else:
            return False
            
    def Act(self):
        for c in self.cities:
            c.Act(self.giorno)
        if self.checkGiorno():
            print(self.cities[0].immune/float(self.cities[0].death+self.cities[0].immune+1))
            if(self.cities[0].sick==0):
                txt.close()
            else:
                txt.write(str(time)+' '+str(self.cities[0].immune)+' '+str(self.cities[0].death)+' '+str(self.cities[0].sick)+'\n')
            for c in self.cities:
                A=list(filter(lambda x: x.isSick, c.People))
                for p in A:
                    if(self.giorno-p.giorno<=p.virus.giorni):
                        
                        if random.uniform(0,1)<p.virus.mort**(1.0/self.virus.giorni):
                            p.Health-=p.Life/(p.virus.giorni)+0.001
                    else:
                        p.isImmune=True
                        p.Health=p.Life
                        p.isSick=False
                    
        
    

            
            

            
                    
            
Covid=Virus(0.3,0.05,14,0.7)
citta=City(1000,100,0.6,Covid,0.5)
W=World([citta],Covid)

def setup():
    size(640,640,P2D)
    background(255,255,255)
    citta.AddSick()



def draw():
    global time

    time+=1

    background(255,255,255)
    
    W.Act()



def mouseClicked():
        for p in citta.People:
            if math.sqrt((mouseX-p.Pos[0])**2+(mouseY-p.Pos[1])**2)<10:
                print(p)

from manimlib.imports import *
from random import randrange
from math import atan
from math import sqrt
VIT=FRAME_WIDTH/20
CD_P=30 #change directory proba = 20%

dt=0.1
height_vs_scale=0.5

class Vect():
    def rot():
        '''
        Elle calcule le rotationel de la vitesse,
        puis il donne une valeur comprise entre [0,2*pi]
        en utilisant la fonction logistic (d'euler)
        cette valeur représente l'angle de wings
        '''

class Bird():
    def __init__(self, position=np.array([0,0,0])):
        self.generatre_bird(position)

    def generatre_bird(self,position,speed,rot):
        '''
        completer la forme de bird
        '''

        shift=position.copy()
        self.position=position.copy()
        shift[2]=0
        self.bird_objects=[Circle()]
        scale=height_vs_scale**(-self.position[2])
        self.bird_objects[0].shift(shift)
        self.bird_objects[0].scale(scale)

    def move_to(self,position,speed):
        def generate_para(position,speed):
            shift=position-self.position
            shift_len=sqrt(shift[0]**2+shift[1]**2+shift[2]**2)
            direction=shift/shift_len
            dOM=speed*dt*direction
            dOM_len=sqrt(dOM[0]**2+dOM[1]**2+dOM[2]**2)
            nbr_pts=int(shift_len/dOM_len)

            return dOM,nbr_pts

        dOM,nbr_pts=generate_para(position,speed)

        Objects=[]
        progress=np.array([0.0,0.0,0.0])
        for i in range(nbr_pts):
            progress+=dOM
            self.generatre_bird(progress)
            ins=[]
            for o in self.bird_objects:
                ins+=[o.copy()]
            Objects+=[ins]

        self.generatre_bird(position)
        last=[]
        for o in self.bird_objects:
                last+=[o.copy()] 
        return Objects+[last]

class Test(Scene):

    def play_move_bird_to(self,bird,position,speed):
        Objs=bird.move_to(position,speed)
        ob=None
        for Obj in Objs:
            ob=Obj
            for o in Obj:
                self.add(o)
            self.wait(dt)
            for o in Obj:
                self.remove(o)
        for o in ob:
            self.add(o)

    def construct(self):
        b=Bird()
        self.wait(2)
        self.play_move_bird_to(b,RIGHT+IN,1)
        self.wait(2)

class Main(Scene):
    Daban=[]
    Prev_shift=[]
    def rand_shift(self,prev_slop):
        dom=int(VIT*1000)
        x=randrange(-dom,dom)/1000
        y=randrange(-dom,dom)/1000
        if x==0:
            x=0.1
        if prev_slop!=None:
            if abs(atan(y/x)-atan(prev_slop))>20:
                return self.rand_shift(prev_slop)

        return x*RIGHT+y*UP

    def generator(self,nbr):
        for i in range(nbr):
            d=Dot(radius=0.05)
            pos=self.rand_shift(None)
            d.shift(pos)
            Main.Daban+=[d]
            Main.Prev_shift+=[pos]
            self.add(d)

    def zann(self):
        global CD_P
        Anim=[]
        l=len(Main.Daban)
        if l==1:
            CD_P=80
        for i in range(l):
            d=Main.Daban[i]
            shift=Main.Prev_shift[i]
            if randrange(0,100)<CD_P:
                shift=self.rand_shift(Main.Prev_shift[i][1]/Main.Prev_shift[i][0])
            pos=d.get_arc_center()+shift
            if pos[0]>FRAME_WIDTH/2 or pos[0]<-FRAME_WIDTH/2:
                shift[0]*=(-1)
            if pos[1]>FRAME_HEIGHT/2 or pos[1]<-FRAME_HEIGHT/2:
                shift[1]*=(-1)
            Anim+=[ApplyMethod(d.shift,shift,rate_func=linear)]
            Main.Prev_shift[i]=shift
        self.play(*Anim)
    
    @staticmethod
    def run_for_your_life():
        Anim=[]
        Remain=[]
        for i in range(1,len(Main.Daban)):
            d=Main.Daban[i]
            shift=25*Main.Prev_shift[i]
            pos=d.get_arc_center()+shift
            Anim+=[ApplyMethod(d.shift,shift)]
            if pos[0]<FRAME_WIDTH/2 and pos[0]>-FRAME_WIDTH/2 and pos[1]>-FRAME_HEIGHT/2 and pos[1]<FRAME_HEIGHT/2:
                Remain+=[d]
        Main.Daban=Remain
        return Anim


    def construct(self):
        self.generator(65)
        for i in range(10):
            self.zann()
        #logo=ImageMobject("logo_a.png")
        #logo.scale(0.1)
        #self.play(ApplyMethod(logo.scale,20),*Main.run_for_your_life())
        #for i in range(10):
            #self.zann()

        #self.wait(2)
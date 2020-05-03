from manimlib.imports import *
from random import randrange
from math import atan
VIT=FRAME_WIDTH/20
CD_P=30#change directory proba = 20%
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
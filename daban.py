from manimlib.imports import *
from random import randrange
from math import atan
from math import sqrt
VIT=FRAME_WIDTH/20
CD_P=30 #change directory proba = 20%

dt=0.1
height_vs_scale=0.5

class Vect():
    def __init__(self,x,y,z):
        self.array=np.array([x,y,z])

    def screen_projection(self):
        return Vect(self.array[0],self.array[1],0)

    def norme(self):
        return math.sqrt(
            self.array[0]**2+
            self.array[1]**2+
            self.array[2]**2
        )

    def rotation(self,angle,axe):
        pass

    def coordinte_in(self,base_out,base_in):
            pass

    def copy(self):
        return Vect(self.array[0],self.array[1],self.array[2])

    @staticmethod
    def prod_scalaire(u,v):
        return u.array[0]*v.array[0]+u.array[1]*v.array[1]+u.array[2]*v.array[2]

    @staticmethod
    def prod_vect(u,v):
        return Vect(
            u.array[1]*v.array[2]-u.array[2]*v.array[1],
            u.array[2]*v.array[0]-u.array[0]*v.array[2],
            u.array[0]*v.array[1]-u.array[1]*v.array[0])

    @staticmethod
    def angle_entre(u,v):
        u_c=u.copy()
        v_c=v.copy()
        p_s=Vect.prod_scalaire(u_c,v_c)
        n_p=u_c.norme()*v_c.norme()
        if n_p==0:
            return 0

        p_s/=n_p
        tetha=math.acos(p_s)
        u_vec_v=Vect.prod_vect(u_c,v_c)
        if Vect.prod_scalaire(u_vec_v,Vect(0,0,1))<0:
            return -tetha
        return tetha

class Bird():
    def __init__(self, position=np.array([0,0,0]),color=WHITE):
        self.color=color
        self.generatre_bird(position,position,position)

    def generatre_bird(self,position,pre_position,post_position,new_color=None):
        if new_color!=None:
            self.color=new_color

        def wings_base(position,pre_position,post_position):
            direction=Vect(position[0]-pre_position[0],position[1]-pre_position[1],position[2]-pre_position[2])
            n=direction.norme()
            if n==0:
                return 0
            direction/=n

            next_direction=Vect(post_position[0]-position[0],post_position[1]-position[1],post_position[2]-position[2])
            n=next_direction.norme()
            if n==0:
                return 0
            next_direction/=n

            angle_de_divation=Vect.angle_entre(direction,next_direction)

            x,z=0
            if next_direction.array[0]!=0:
                x=-next_direction.array[2]/next_direction.array[0]
                z=1
            elif next_direction.array[2]!=0:
                z=-next_direction.array[0]/next_direction.array[1]
                x=1
            else:
                x,z=1,0
            wings_dir=Vect(x,0,z)
            wings_dir.array/=wings_dir.norme()
            wings_dir.rotation(angle_de_divation,next_direction)

            return [wings_dir,next_direction,Vect.prod_vect(wings_dir,next_direction)]

        def wings_pts(position,pre_position,post_position):
            bird_base=wings_base(position,pre_position,post_position)
            screen_base=[Vect(1,0,0),Vect(0,1,0),Vect(0,0,1)]
            Ref_pts=None #les_pts_des_wings_dans_la_base_de_bird : bird_base. à completer !!
            Wings_pts=[] #les_pts_des_wings_dans_la_base_de_screen
            for p in Ref_pts:
                Wings_pts+=[p.coordinte_in(screen_base,bird_base)]
            return Wings_pts

        def body_pts(post_position,position):
            pass

        scale=0.01
        #l=l_factor(post_position,position)
        #b=b_factor(position,pre_position,post_position)

        ################################################
        b=1
        l=1
        ################################################

        ########### Create the pts using body_pts and wings_pts :
        head=Circle(
            radius=20*scale,
            color=self.color,fill_color=self.color,fill_opacity=1)

        body=Polygon(
            20*LEFT*scale,20*RIGHT*scale,l*100*DOWN*scale,
            color=self.color,fill_color=self.color,fill_opacity=1)
        tail=Polygon(
            (10*LEFT+100*DOWN)*scale,(10*RIGHT+100*DOWN)*scale,80*l*DOWN*scale,
            color=self.color,fill_color=self.color,fill_opacity=1)
        wing_l=Polygon(
            0*LEFT,75*b*LEFT*scale,(100*b*LEFT+20*l*DOWN)*scale,
            (100*b*LEFT+50*l*DOWN)*scale,(75*b*LEFT+30*l*DOWN)*scale,
            30*l*scale*DOWN,
            color=self.color,fill_color=self.color,fill_opacity=1)
        wing_r=Polygon(
            0*RIGHT,75*b*RIGHT*scale,(100*b*RIGHT+20*l*DOWN)*scale,
            (100*b*RIGHT+50*l*DOWN)*scale,(75*b*RIGHT+30*l*DOWN)*scale,
            30*l*scale*DOWN,
            color=self.color,fill_color=self.color,fill_opacity=1)
        ###########

        self.bird_objects=[head,body,tail,wing_l,wing_r]

        ######################### scale _ rotion _ shift
        #shift=position.copy()
        #shift[2]=0
        #scale=height_vs_scale**(-self.position[2])
        #self.bird_objects[0].shift(shift)
        #self.bird_objects[0].scale(scale)

        self.position=position.copy()

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
        b.generatre_bird(1*LEFT+1*UP,0*UP,2*LEFT+2*UP+5*IN,new_color=None)
        self.add(*b.bird_objects)
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
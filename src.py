from manimlib.imports import *
from random import randrange
import math

#dt=0.017 #60 fps
dt=0.1 #test

#============================= Manim Test class =================================================
class Test(Scene):

    def construct(self):
        b=Bird()
        #positions=[
        #    [2.0*LEFT,2.0*RIGHT,0.5*IN+0.5*RIGHT,0.5*IN+0.5*RIGHT],
            #[2.0*RIGHT,3.0*RIGHT+3.0*UP,0.5*IN+0.5*RIGHT,0.1*UP],
            #[3.0*RIGHT,1.0*LEFT+2.0*DOWN,0.5*DOWN+0.5*LEFT,0.5*UP+0.5*LEFT],
            #[2*DOWN+LEFT,2*UP+IN,0.5*UP+IN+RIGHT,0.5*UP+0.5*LEFT+OUT]
        #
        P,A=b.aleatoire_path(Vect(0.0,0.0,0.0),Vect(1.0,0.0,0.0))

        for i in range(1,len(P)-1):
            obj=b.generatre_bird(P[i],P[i-1],P[i+1],A[i])
            self.add(*obj)
            self.wait(dt)
            self.remove(*obj)
        self.wait(2)

#============================= Bird class =================================================

class Bird():
    def __init__(self, position=np.array([0,0,0]),color=WHITE):
        self.color=color
        self.position=position
        #self.wings=self.generatre_bird(position,position,position)

    def generatre_bird(self,position,pre_position,post_position,diviation_angle,new_color=None):

        def z_axis_to_scale(z):
            return 0.25**(-z)

        def wings_objects(position,pre_position,post_position):

            def wings_base(position,pre_position,post_position):
                screen_base=[Vect(1,0,0),Vect(0,1,0),Vect(0,0,1)]
                direction=Vect(position[0]-pre_position[0],position[1]-pre_position[1],position[2]-pre_position[2])
                n=direction.norme()
                if n==0:
                    return screen_base
                direction.scalaire_mult(1/n)

                next_direction=Vect(post_position[0]-position[0],post_position[1]-position[1],post_position[2]-position[2])
                n=next_direction.norme()
                if n==0:
                    return screen_base
                next_direction.scalaire_mult(1/n)

                x,z=0.0,0.0
                if next_direction.array[0]!=0:
                    x=-next_direction.array[2]/next_direction.array[0]
                    z=1.0
                elif next_direction.array[2]!=0:
                    z=-next_direction.array[0]/next_direction.array[2]
                    x=1.0
                else:
                    x,z=1.0,0.0
                wings_dir=Vect(x,0,z)
                wings_dir.array/=wings_dir.norme()
                third_vect=Vect.prod_vect(wings_dir,next_direction)
                base_bird=[wings_dir.copy(),next_direction.copy(),third_vect.copy()]

                wings_dir.rotation_arround_direction(diviation_angle,base_bird)
                third_vect.rotation_arround_direction(diviation_angle,base_bird)

                base_bird=[wings_dir.copy(),next_direction.copy(),third_vect.copy()]
                return base_bird

            def wings_pts(position,pre_position,post_position):
                bird_base=wings_base(position,pre_position,post_position)
                Ref_pts=[
                    Vect (-20,-10,0),
                    Vect(-60,0,0),
                    Vect (-100,0,0),
                    Vect(-110,-20,0),
                    Vect(-70,-32,0),
                    Vect(-20,-40,0),
                    Vect(20,-40,0),
                    Vect(70,-32,0),
                    Vect(110,-20,0),
                    Vect(100,0,0),
                    Vect(60,0,0),
                    Vect(20,-10,0)
                ] #les_pts_des_wings_dans_la_base_de_bird : bird_base.
                Wings_pts=[] #les_pts_des_wings_dans_la_base_de_screen

                for p in Ref_pts:
                    Wings_pts+=[p.coordinte_in_screen_base(bird_base)]
                return Wings_pts

            def pts_3D_to2D(pts):
                pts_np_arr=[]
                for p in pts:
                    pts_np_arr+=[np.array([p.array[0],p.array[1],0])]
                return pts_np_arr

            pts_2D=pts_3D_to2D(wings_pts(position,pre_position,post_position))
            wings=Polygon(
                *pts_2D,
                color=self.color,fill_color=self.color,fill_opacity=1,stroke_width=5,stroke_color=self.color
            )
            return [wings]

        def body_objects(post_position,position):
            l=1
            direction=Vect(
                post_position[0]-position[0],
                post_position[1]-position[1],
                post_position[2]-position[2]
            )
            n=direction.norme()
            if n!=0:
                direction.array/=n
            l=Vect.prod_scalaire(direction,direction.screen_projection())

            head=Circle(
                radius=20,
                color=self.color,fill_color=self.color,fill_opacity=1
            )
            body=Polygon(
                20*LEFT,20*RIGHT,l*100*DOWN,
                color=self.color,fill_color=self.color,fill_opacity=1
            )
            tail=Polygon(
                10*LEFT+100*l*DOWN,10*RIGHT+100*l*DOWN,80*l*DOWN,
                color=self.color,fill_color=self.color,fill_opacity=1
            )
            angle=Vect.angle_entre(Vect(0.0,1.0,0.0),direction,[Vect(1.0,0.0,0.0),Vect(0.0,1.0,0.0),Vect(0.0,0.0,1.0)])
            head.rotate(angle,about_point=position)
            body.rotate(angle,about_point=position)
            tail.rotate(angle,about_point=position)
            return [head,body,tail]

        if new_color!=None:
            self.color=new_color
        self.position=position.copy()

        scale=0.01*z_axis_to_scale(position[2])
        bird_objects=body_objects(post_position,position)+wings_objects(position,pre_position,post_position)
        for obj in bird_objects:
            obj.scale(scale,about_point=position)
        return bird_objects

    def position_interpolation(self,p_d,p_a,v_d,v_a):
        '''
        This function works in those conditions:
            * p_d != p_a
            * v_d and v_a must have a component following the main direction and it must be positive
        '''

        def verify_conditions_and_generate_vect(p_d,p_a,v_d,v_a):
            if p_d[0]==p_a[0] and p_d[1]==p_a[1] and p_d[2]==p_a[2]:
                raise ValueError("La position de depart c'est la position d'arrive")
            P_d=Vect(p_d[0],p_d[1],p_d[2])
            P_a=Vect(p_a[0],p_a[1],p_a[2])
            main_direc=Vect.soustraction(P_a,P_d)
            l=main_direc.norme()
            main_direc.array/=l

            V_d=Vect(v_d[0],v_d[1],v_d[2])
            V_a=Vect(v_a[0],v_a[1],v_a[2])

            v_d_prj=Vect.prod_scalaire(V_d,main_direc)
            v_a_prj=Vect.prod_scalaire(V_a,main_direc)
            if v_d_prj<=0:
                raise ValueError("La vitesse de départ ne suit pas la direction principale")
            if v_a_prj<=0:
                raise ValueError("La vitesse d'arrive ne suit pas la direction principale")

            n=int(2*l/(dt*(v_d_prj+v_a_prj)))
            return P_d,P_a,V_d,V_a,l,main_direc,n

        def choose_mvt_base(main_direc,V_d,V_a):
            v_init=None
            f=open("mvt_base.verf",'a')
            if Vect.is_equal(Vect.prod_vect(V_d,main_direc),Vect(0,0,0)):
                if Vect.is_equal(Vect.prod_vect(V_a,main_direc),Vect(0,0,0)):
                    raise Exception("main_direc,V_d,V_a sont colinéaires")
                v_init=V_a.copy()
            else:
                v_init=V_d.copy()
            
            vec_n=Vect.prod_vect(main_direc,v_init)

            vec=Vect.prod_vect(main_direc,vec_n)
            return [main_direc.copy(),vec,Vect.prod_vect(main_direc,vec)]

        def vitesse_main_direction(V_d,V_a,l,n,base_mvt):
            v_1=Vect.prod_scalaire(V_d,base_mvt[0])
            v_2=Vect.prod_scalaire(V_a,base_mvt[0])
            a=(v_2-v_1)/(n*dt)
            
            V=[v_1]
            for i in range(1,n):
                V+=[v_1+a*i*dt]

            return V

        def vitesse_first_rad(V_d,V_a,l,n,base_mvt):
            v1=Vect.prod_scalaire(V_d,base_mvt[1])
            v2=Vect.prod_scalaire(V_a,base_mvt[1])
            d=l/n
            if v1*v2<=0:
                x=abs(v2)/(abs(v2)+abs(v1))*l
                V_rad_1_scal=[v1]
                dis=0
                if x!=0:
                    a=-v1/x
                    while dis<x:
                        dis+=d
                        V_rad_1_scal+=[v1+a*dis]

                if x!=l:
                    a=v2/(l-x)
                    while dis<l:
                        dis+=d
                        V_rad_1_scal+=[a*(dis-x)]
                return V_rad_1_scal

            else:
                x1=abs(v2)/(abs(v1)+3*abs(v2))*l
                x2,x3=2*x1,3*x1
                v3=(abs(v1)+abs(v2))/2
                if v1>0:
                    v3*=-1
                V_rad_1_scal=[v1]
                dis=0
                a=-v1/x1
                while dis<x1:
                    dis+=d
                    V_rad_1_scal+=[v1+a*dis]

                a=v3/x1
                while dis<x2:
                    dis+=d
                    V_rad_1_scal+=[a*(dis-x1)]

                a*=-1
                while dis<x3:
                    dis+=d
                    V_rad_1_scal+=[v3+a*(dis-x2)]
                
                a=v2/(l-x3)
                while dis<l:
                    dis+=d
                    V_rad_1_scal+=[a*(dis-x3)]
                
                return V_rad_1_scal
        
        def vitesse_second_rad(V_d,V_a,l,n,base_mvt):
            v_init=Vect.prod_scalaire(V_a,base_mvt[2])
            d=l/n
            x1=l/3
            dis=0
            if v_init==0:
                v_init=Vect.prod_scalaire(V_d,base_mvt[2])
                if v_init==0:
                    return [0]*n
                
                v_=v_init/2
                V=[v_init]

                a=-v_init/x1
                while dis < x1:
                    dis+=d
                    V+=[v_init+a*dis]

                a=v_/x1
                while dis < 2*x1:
                    dis+=d
                    V+=[a*(dis-x1)]
                
                a*=-1
                while dis < l:
                    dis+=d
                    V+=[v_+a*(dis-2*x1)]
                
                return V

            else :
                V=[v_init]
                v_=v_init/2

                a=-v_/x1
                while dis < x1:
                    dis+=d
                    V+=[a*dis]

                a*=-1
                while dis < 2*x1:
                    dis+=d
                    V+=[v_+a*(dis-x1)]

                a=v_init/x1
                while dis < l:
                    dis+=d
                    V+=[a*(dis-2*x1)]
                
                return V

        def diviation_angle(dir,V_d,V_a,n,base_mvt):
            def behavior(dir,V_d,V_a,n,base_mvt):
                if Vect.prod_scalaire(dir,Vect(0,1,0))>=0:
                    return False #for flapping
                return True #for gliding

            def flapping(dir,V_d,V_a,n,base_mvt):
                pass
            
            def gliding(dir,V_d,V_a,n,base_mvt):
                Angles=[]
                moy_ang=Vect.angle_entre(V_d,V_a,base_mvt)
                if Vect.angle_entre(V_d,base_mvt[0],base_mvt)*Vect.angle_entre(V_a,base_mvt[0],base_mvt)>0:
                    moy_ang+=math.pi
                n_2=int(n/2)
                if n_2!=0:
                    a=moy_ang/n_2
                    for i in range(n_2):
                        Angles+=[i*a]
                a=-moy_ang/(n-n_2)
                for i in range(n-n_2):
                    Angles+=[moy_ang+i*a]

                return Angles+[0]

            return gliding(dir,V_d,V_a,n,base_mvt)


        P_d,P_a,V_d,V_a,l,main_direc,n=verify_conditions_and_generate_vect(p_d,p_a,v_d,v_a)
        if n==0:
            return [],[]
        # Traiter le cas ou main_direc,V_d,V_a sont colinéaires
        base_mvt=choose_mvt_base(main_direc,V_d,V_a)

        Vn=vitesse_main_direction(V_d,V_a,l,n,base_mvt)
        Vr1=vitesse_first_rad(V_d,V_a,l,n,base_mvt)
        Vr2=vitesse_second_rad(V_d,V_a,l,n,base_mvt)

        Positions=[P_d]
        for i in range(n):
            vn_vec=base_mvt[0].copy()
            vn_vec.scalaire_mult(Vn[i])
            vr1_vec=base_mvt[1].copy()
            vr1_vec.scalaire_mult(Vr1[i])
            vr2_vec=base_mvt[2].copy()
            vr2_vec.scalaire_mult(Vr2[i])

            Vr=Vect.somme(vr1_vec,vr2_vec)
            V=Vect.somme(vn_vec,Vr)

            V.scalaire_mult(dt)
            Positions+=[Vect.somme(Positions[i],V)]

        positions=[]
        for p in Positions:
            positions+=[p.array]
        return positions,diviation_angle(dir,V_d,V_a,n,base_mvt)

    def aleatoire_path(self,P_0,V_0,duration=20):
        def next_direction_and_next_pts(P_0,V_0):
            def out_of_screen(P_0,next_dir):

                def t_max_possible(P_0,a,b,c):
                    T_max_possible=[]

                    if a>0:
                        T_max_possible+=[((0.5*FRAME_WIDTH-P_0.array[0])/a,0)]
                    if a<0:
                        T_max_possible+=[((-0.5*FRAME_WIDTH-P_0.array[0])/a,0)]

                    if b>0:
                        T_max_possible+=[((0.5*FRAME_HEIGHT-P_0.array[1])/b,1)]
                    if b<0:
                        T_max_possible+=[((-0.5*FRAME_HEIGHT-P_0.array[1])/b,1)]

                    if c>0:
                        T_max_possible+=[((-FRAME_WIDTH-P_0.array[2])/c,2)]
                    if c<0:
                        T_max_possible+=[(-P_0.array[2]/c,2)]

                    return T_max_possible

                def is_it_t_max(t,a,b,c,P_0):
                    x=a*t[0]+P_0.array[0]
                    y=b*t[0]+P_0.array[1]
                    z=c*t[0]+P_0.array[2]

                    err=0.000001

                    if t[1]!=0 and (x+err>0.5*FRAME_WIDTH or x-err<-0.5*FRAME_WIDTH):
                        return False
                    if t[1]!=1 and (y+err>0.5*FRAME_HEIGHT or y-err<-0.5*FRAME_HEIGHT):
                        return False
                    if t[1]!=2 and (z+err>0 or z-err<-FRAME_WIDTH):
                        return False

                    return True

                a,b,c = next_dir.array[0],next_dir.array[1],next_dir.array[2]
                T_max_possible=t_max_possible(P_0,a,b,c)
                for t in T_max_possible:
                    if is_it_t_max(t,a,b,c,P_0):
                        return Vect(
                            a*t[0]+P_0.array[0],
                            b*t[0]+P_0.array[1],
                            c*t[0]+P_0.array[2]
                        )
                raise Exception("Can't find P_MAX")

            base=V_0.BaseOrthoNormer()#[--,V0,--]
            base1=[base[2].copy(),base[0].copy(),base[1].copy()]
            base2=[base[1].copy(),base[2].copy(),base[0].copy()]
            m=int(math.pi/2*1000)
            ang1=randrange(-m,m)/1000
            ang2=randrange(-m,m)/1000
            vec1=V_0.copy()
            vec2=V_0.copy()
            vec1.rotation_arround_direction(ang1,base1)
            vec2.rotation_arround_direction(ang2,base2)

            next_dir=Vect.somme(vec1,vec2)
            next_dir.array/=next_dir.norme()
            P_MAX=out_of_screen(P_0,next_dir)
            l_max_vec=Vect.soustraction(P_MAX,P_0)
            l_max=l_max_vec.norme()*0.8
            l=randrange(1,int(l_max*1000)+1)/1000
            l_vec=next_dir.copy()
            l_vec.scalaire_mult(l)
            P_next=Vect.somme(P_0,l_vec)
            return next_dir,P_next

        def next_vitesse(direction,P_1):
            def la_plus_proche(X_MAX,Y_MAX,px,py,pz):
                d=[]
                if px>X_MAX*0.8:
                    d+=[(X_MAX-px,0)]
                if px<-X_MAX*0.8:
                    d+=[(px-X_MAX,1)]
                if py>Y_MAX*0.8:
                    d+=[(Y_MAX-py,2)]
                if px<-Y_MAX*0.8:
                    d+=[(py-Y_MAX,3)]
                if pz>FRAME_WIDTH*0.8:
                    d+=[(FRAME_WIDTH-pz,4)]
                if pz<FRAME_WIDTH*0.2:
                    d+=[(pz,5)]
                
                d_min=FRAME_WIDTH+10
                i_min=None
                for l in d:
                    if l[0]<d_min:
                        d_min=l[0]
                        i_min=l[1]
                if i_min==None:
                    i_min=randrange(0,6)
                return i_min

            def calcule_vitesse(i_choice,a,b,c,V_max):
                vx,vy,vz=None,None,None
                if i_choice==0 or i_choice==1:
                    vx=randrange(0,V_max*1000)/1000
                    if vx==0:
                        vx=0.1
                    if i_choice==1:
                        vx*=-1
                    if b!=0:
                        vz=0
                        vy=-a/b*vx
                        if b>0:
                            vy+=randrange(0,V_max*1000)/1000
                        else:
                            vy-=randrange(0,V_max*1000)/1000
                    elif c!=0:
                        vy=0
                        vz=-a/c*vx
                        if c>0:
                            vz+=randrange(0,V_max*1000)/1000
                        else:
                            vz-=randrange(0,V_max*1000)/1000
                    else:
                        vy=0
                        vz=0
                
                if i_choice==2 or i_choice==3:
                    vy=randrange(0,V_max*1000)/1000
                    if vy==0:
                        vy=0.1
                    if i_choice==3:
                        vy*=-1
                    if a!=0:
                        vz=0
                        vx=-b/a*vy
                        if a>0:
                            vx+=randrange(0,V_max*1000)/1000
                        else:
                            vx-=randrange(0,V_max*1000)/1000
                    elif c!=0:
                        vx=0
                        vz=-b/c*vy
                        if c>0:
                            vz+=randrange(0,V_max*1000)/1000
                        else:
                            vz-=randrange(0,V_max*1000)/1000
                    else:
                        vx=0
                        vz=0

                if i_choice==4 or i_choice==5:
                    vz=randrange(0,V_max*1000)/1000
                    if vz==0:
                        vz=0.1
                    if i_choice==5:
                        vz*=-1
                    if b!=0:
                        vx=0
                        vy=-c/b*vz
                        if b>0:
                            vy+=randrange(0,V_max*1000)/1000
                        else:
                            vy-=randrange(0,V_max*1000)/1000
                    elif a!=0:
                        vy=0
                        vx=-c/a*vz
                        if a>0:
                            vx+=randrange(0,V_max*1000)/1000
                        else:
                            vx-=randrange(0,V_max*1000)/1000
                    else:
                        vx=0
                        vy=0

                return Vect(vx,vy,vz)

            V_max=0.5
            a,b,c=direction.array[0],direction.array[1],direction.array[2]
            px,py,pz=P_1.array[0],P_1.array[1],P_1.array[2]
            X_MAX=FRAME_WIDTH/2
            Y_MAX=FRAME_HEIGHT/2
            return calcule_vitesse(la_plus_proche(X_MAX,Y_MAX,px,py,pz),a,b,c,V_max)

        P=[]
        A=[]
        Pd=P_0
        Vd=V_0
        n=int(duration/dt)
        while(len(P)<n):
            next_dir,Pa=next_direction_and_next_pts(Pd,Vd)
            Va=next_vitesse(next_dir,Pd)
            PA=self.position_interpolation(Pd.array,Pa.array,Vd.array,Va.array)
            P+=PA[0]
            A+=PA[1]
            Pd,Vd=Pa,Va

        return P[:n],A[:n]

#============================= Vect class =================================================

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
    
    def scalaire_mult(self,a):
        self.array*=a

    def coordinte_in_bird_base(self,base_bird):
        passage=np.array([base_bird[0].array,base_bird[1].array,base_bird[2].array])
        V=np.dot(passage,self.array)
        return Vect(V[0],V[1],V[2])

    def coordinte_in_screen_base(self,base_bird):
        passage=np.array([base_bird[0].array,base_bird[1].array,base_bird[2].array])
        V=np.dot(np.linalg.inv(passage),self.array)
        return Vect(V[0],V[1],V[2])

    def rotation_arround_direction(self,angle,base_bird):#arround base_bird[1]
        Mat_Rot=np.array([
            np.array([np.cos(angle),0,np.sin(angle)]),
            np.array([0,1,0]),
            np.array([-np.sin(angle),0,np.cos(angle)])
        ])
        vec_in_bird_base=self.coordinte_in_bird_base(base_bird)
        rotated_vec_in_bird_base_array=np.dot(Mat_Rot,vec_in_bird_base.array)
        rotated_vec_in_bird_base=Vect(
            rotated_vec_in_bird_base_array[0],
            rotated_vec_in_bird_base_array[1],
            rotated_vec_in_bird_base_array[2]
        )
        rotated_vec_in_screen_base=rotated_vec_in_bird_base.coordinte_in_screen_base(base_bird)
        self.array=rotated_vec_in_screen_base.array

    def BaseOrthoNormer(self):#self is the seconde vect
        a,b,c=self.array[0],self.array[1],self.array[2]
        x,y,z=None,None,None
        
        if a!=0:
            z=0
            y=1
            x=-b/a

        elif b!=0:
            x=0
            z=1
            y=-c/b
        
        elif c!=0:
            x=0
            y=1
            z=-b/c
        
        per=Vect(x,y,z)
        per.array/=per.norme()
        slef=self.copy()
        slef.array/=slef.norme()

        return [per,slef,Vect.prod_vect(per,slef)]

    def copy(self):
        return Vect(self.array[0],self.array[1],self.array[2])

    def str(self):
        return '('+str(self.array[0])+','+str(self.array[1])+','+str(self.array[2])+')'

    @staticmethod
    def is_equal(u,v):
        if u.array[0]==v.array[0] and u.array[1]==v.array[1] and u.array[2]==v.array[2]:
            return True
        return False

    @staticmethod
    def somme(u,v):
        return Vect(u.array[0]+v.array[0],u.array[1]+v.array[1],u.array[2]+v.array[2])

    @staticmethod
    def soustraction(u,v):
        return Vect(u.array[0]-v.array[0],u.array[1]-v.array[1],u.array[2]-v.array[2])

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
    def angle_entre(u,v,base):
        u_c=u.copy()
        v_c=v.copy()
        v_extra=base[2].copy()
        v_extra.scalaire_mult(Vect.prod_scalaire(v_c,base[2]))
        v_c=Vect.soustraction(v_c,v_extra)
        p_s=Vect.prod_scalaire(u_c,v_c)
        n_p=u_c.norme()*v_c.norme()
        if n_p==0:
            return 0

        p_s/=n_p
        
        # A cause de l'erreur de calcule décimale.
        if p_s>1 :
            p_s=1

        if p_s<-1 :
            p_s=-1

        tetha=math.acos(p_s)
        u_vec_v=Vect.prod_vect(u_c,v_c)
        if Vect.prod_scalaire(u_vec_v,base[2])<0:
            return -tetha
        return tetha
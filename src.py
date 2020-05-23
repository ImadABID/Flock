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
        #P,A=b.aleatoire_path(Vect(0.0,0.0,0.0),Vect(0.1,0.1,-0.1))
        P,A=b.position_interpolation(0.0*IN,14.0*IN,LEFT+IN,RIGHT+IN)

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
            return 0.5**(-z)

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

    def position_interpolation(self,p_d,p_a,v_d,v_a,duration=60):
        def choose_mvt_base(main_direc,V_d,V_a):
            v_init=None
            if Vect.is_equal(Vect.prod_vect(V_d,main_direc),Vect(0,0,0)):
                if Vect.is_equal(Vect.prod_vect(V_a,main_direc),Vect(0,0,0)):
                    raise Exception("main_direc,V_d,V_a sont colinéaires")
                v_init=V_a.copy()
            else:
                v_init=V_d.copy()
            
            vec_n=Vect.prod_vect(main_direc,v_init)

            vec=Vect.prod_vect(main_direc,vec_n)
            return [main_direc.copy(),vec,Vect.prod_vect(main_direc,vec)]

        def easy_interpolation(P_d,V_d,P_a,V_a):
            '''
            This function works in those conditions:
                * p_d != p_a
                * v_d and v_a must have a component following the main direction and it must be positive
            '''
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

            main_direc=Vect.soustraction(P_a,P_d)
            l=main_direc.norme()
            main_direc.array/=l

            n=int(2*l/(dt*(Vect.prod_scalaire(V_d,main_direc)+Vect.prod_scalaire(V_a,main_direc))))

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

        def pt_aleatoir(BIRD_LIVING_SPACE):
            pass

        def pt_v_inter(P_d,V_d,P_a,V_a,main_direc):
            pass

        def somme_deux_P_A_format(P1,A1,P2,A2):#P1,A1+P2,A2
            pass

        BIRD_LIVING_SPACE=[-FRAME_WIDTH/2,FRAME_WIDTH/2,-FRAME_HEIGHT/2,FRAME_HEIGHT/2,-FRAME_WIDTH/2,0.0]
        
        if p_d[0]==p_a[0] and p_d[1]==p_a[1] and p_d[2]==p_a[2]:
            pt_inter=pt_aleatoir(BIRD_LIVING_SPACE).array
            P1,A1=self.position_interpolation(p_d,pt_inter,RIGHT,LEFT)
            P2,A2=self.position_interpolation(pt_inter,p_d,LEFT,RIGHT)
            return somme_deux_P_A_format(P1,A1,P2,A2)
        
        P_d=Vect(p_d[0],p_d[1],p_d[2])
        P_a=Vect(p_a[0],p_a[1],p_a[2])
        main_direc=Vect.soustraction(P_a,P_d)
        main_direc.array/=main_direc.norme()

        V_d=Vect(v_d[0],v_d[1],v_d[2])
        V_a=Vect(v_a[0],v_a[1],v_a[2])

        v_d_prj=Vect.prod_scalaire(V_d,main_direc)
        v_a_prj=Vect.prod_scalaire(V_a,main_direc)
        if v_d_prj<=0 or v_a_prj<=0 :
            P,V=pt_v_inter(P_d,V_d,P_a,V_a,main_direc)
            P1,A1=easy_interpolation(P_d,V_d,P,V)
            P2,A2=easy_interpolation(P,V,P_a,V_a)
            return somme_deux_P_A_format(P1,A1,P2,A2)

        return easy_interpolation(P_d,V_d,P_a,V_a)

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
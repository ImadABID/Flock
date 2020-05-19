from manimlib.imports import *
from random import randrange
import math

#dt=0.017 #60 fps
dt=0.1 #test

#============================= Manim Test class =================================================
class Test(Scene):

    def construct(self):
        b=Bird()
        P=[]
        #P+=b.position_interpolation(2.0*LEFT,2.0*RIGHT,0.5*IN+0.5*RIGHT,0.5*IN+0.5*RIGHT)
        P+=b.position_interpolation(2.0*RIGHT,3.0*RIGHT+3.0*UP,0.5*IN+0.5*RIGHT,0.1*UP)
        #P+=b.position_interpolation(3.0*RIGHT,1.0*LEFT+2.0*DOWN,0.5*DOWN+0.5*LEFT,0.5*UP+0.5*LEFT)
        #P+=b.position_interpolation(2*DOWN+LEFT,2*UP+IN,0.5*UP+IN+RIGHT,0.5*UP+0.5*LEFT+OUT)
        for i in range(1,len(P)-1):
            obj=b.generatre_bird(P[i],P[i-1],P[i+1])
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

    def generatre_bird(self,position,pre_position,post_position,new_color=None):

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

                angle_coff=-1
                if dt==0.1:
                    angle_coff=-30
                if dt==0.017:
                    angle_coff=-100

                angle_de_divation=Vect.angle_entre(direction,next_direction,base_bird)*angle_coff

                wings_dir.rotation_arround_direction(angle_de_divation,base_bird)
                third_vect.rotation_arround_direction(angle_de_divation,base_bird)

                base_bird=[wings_dir.copy(),next_direction.copy(),third_vect.copy()]
                return base_bird

            def wings_pts(position,pre_position,post_position):
                bird_base=wings_base(position,pre_position,post_position)
                Ref_pts=[
                    Vect(75,0,0),
                    Vect(-75,0,0),
                    Vect(-100,-20,0),
                    Vect(-100,-50,0),
                    Vect(-75,-30,0),
                    Vect(75,-30,0),
                    Vect(100,-50,0),
                    Vect(100,-20,0),
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
                raise ValueError("Le vitesse de départ ne suit pas la direction principale")
            if v_a_prj<=0:
                raise ValueError("Le vitesse d'arrive ne suit pas la direction principale")

            n=int(2*l/(dt*(v_d_prj+v_a_prj)))

            return P_d,P_a,V_d,V_a,l,main_direc,n

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

        def choose_mvt_base(main_direc,V_d,V_a):
            v_init=None
            if Vect.is_equal(Vect.prod_vect(V_d,main_direc),Vect(0,0,0)):
                v_init=V_a.copy()
            else:
                v_init=V_d.copy()
            
            x_d,y_d,z_d=main_direc.array[0],main_direc.array[1],main_direc.array[2]
            x_v,y_v,z_v=v_init.array[0],v_init.array[1],v_init.array[2]
            x_n,y_n,z_n=y_d*z_v-z_d*y_v,z_d*x_v-x_d*z_v,x_d*y_v-y_d*x_v

            x,y,z=None,None,None
            nbr_zero_dirc_eq=0
            if x_d==0:
                nbr_zero_dirc_eq+=1
            if y_d==0:
                nbr_zero_dirc_eq+=1
            if z_d==0:
                nbr_zero_dirc_eq+=1

            if nbr_zero_dirc_eq==2:
                if x_d!=0:
                    x=0.0
                    if y_n!=0:
                        z=1.0
                        y=-z_n/y_n
                    else :
                        y=1.0
                        z=0.0

                elif y_d!=0:
                    y=0.0
                    if x_n!=0:
                        z=1.0
                        x=-z_n/x_n
                    else :
                        x=1.0
                        z=0.0

                else:
                    z=0.0
                    if x_n!=0:
                        y=1.0
                        x=-y_n/x_n
                    else :
                        x=1.0
                        y=0.0

            elif nbr_zero_dirc_eq==1:
                if x_d==0:
                    z=1.0
                    y=-z_d/y_d
                    x=-(y_n*y+z_n*z)/x_n

                if y_d==0:
                    z=1.0
                    x=-z_d/x_d
                    y=-(x_n*x+z_n*z)/y_n

                if z_d==0:
                    y=1.0
                    x=-y_d/x_d
                    z=-(x_n*x+y_n*y)/z_n
            else :
                z=1.0
                y=(x_d*z_n-x_n*z_d)/(x_n*y_d-x_d*y_n)
                x=-(x_d*y_n*y+x_d*z_n)/(x_d*x_n)

            vec=Vect(x,y,z)
            vec.array/=vec.norme()
            return [main_direc,vec,Vect.prod_vect(main_direc,vec)]

        P_d,P_a,V_d,V_a,l,main_direc,n=verify_conditions_and_generate_vect(p_d,p_a,v_d,v_a)
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
        return positions

#============================= Vect class =================================================

class Vect():
    def __init__(self,x,y,z):
        self.array=np.array([x,y,z])

    def screen_projection(self):
        return Vect(self.array[0],self.array[1],0)

    def norme(self):
        f=open("error.tracker",'w')
        f.write(self.str())
        f.close()
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

    def rotation_arround_direction(self,angle,base_bird):
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
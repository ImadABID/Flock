from manimlib.imports import *
from random import randrange
import math

#============================= Manim Test class =================================================
class Test(Scene):

    def construct(self):
        b=Bird()
        self.add(*b.generatre_bird(0*RIGHT,DOWN,RIGHT+4*UP))
        self.wait(2)

#============================= Bird class =================================================
height_vs_scale=0.5
class Bird():
    def __init__(self, position=np.array([0,0,0]),color=WHITE):
        self.color=color
        self.position=position
        #self.wings=self.generatre_bird(position,position,position)

    def generatre_bird(self,position,pre_position,post_position,new_color=None):

        def z_axis_to_scale(z):
            return height_vs_scale**(-z)

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

                angle_de_divation=Vect.angle_entre(direction,next_direction)

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
                color=self.color,fill_color=self.color,fill_opacity=1,stroke_width=10
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
                10*LEFT+100*DOWN,10*RIGHT+100*DOWN,80*l*DOWN,
                color=self.color,fill_color=self.color,fill_opacity=1
            )
            angle=Vect.angle_entre(Vect(0,1,0),direction)
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
        
        # A cause de l'erreur de calcule décimale.
        if p_s>1 :
            p_s=1

        if p_s<-1 :
            p_s=-1

        tetha=math.acos(p_s)
        u_vec_v=Vect.prod_vect(u_c,v_c)
        if Vect.prod_scalaire(u_vec_v,Vect(0,0,1))<0:
            return -tetha
        return tetha
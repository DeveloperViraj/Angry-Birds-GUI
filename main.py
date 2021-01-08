"""
Angry Birds by Viraj
"""
__author__ = "Viraj"
__date__ = "2020/11/9"

import os
import math
import arcade
import pymunk
import timeit
from PIL import Image
 

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Angry Birds"

class PhysicsSprite(arcade.Sprite):
    def __init__(self, pymunk_shape, filename):
        super().__init__(filename, center_x=pymunk_shape.body.position.x, center_y=pymunk_shape.body.position.y)
        self.pymunk_shape = pymunk_shape


class CircleSprite(PhysicsSprite):
    def __init__(self, pymunk_shape, filename):
        super().__init__(pymunk_shape, filename)
        self.width = pymunk_shape.radius * 2
        self.height = pymunk_shape.radius * 2


class BoxSprite(PhysicsSprite):
    def __init__(self, pymunk_shape, filename, width, height):
        super().__init__(pymunk_shape, filename)
        self.width = width
        self.height = height

 
def make_sprite(mass,image,position,space):      
    """生成一个受重力的角色"""
    width,height = Image.open(image).size  # 获取图像的宽度和高度
    mass = mass
    moment = pymunk.moment_for_box(mass, (width,height))
    body = pymunk.Body(mass, moment)
    body.position = pymunk.Vec2d(position)
    shape = pymunk.Poly.create_box(body, (width, height))
    shape.friction = 0.3
    space.add(body, shape)
    sprite = BoxSprite(shape, image, width=width, height=height)
    return sprite       


class MyGame(arcade.Window):
    """ 最顶层的游戏类，继承自窗口 """

    def __init__(self, width, height,title):
        super().__init__(width, height,title)
        
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.parabolic_points = []        # 保存抛物线点
        self.dx = self.dy = 0
 
        # -- Pymunk的重力空间
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)

        # 所有角色列表
        self.background = arcade.Sprite("images/background.png")
        self.background.left = self.background.bottom = 0
        self.sprite_list = arcade.SpriteList()
        self.static_lines = []

        # 用鼠标拖曳的角色相关变量
        self.shape_being_dragged = None
        self.last_mouse_position = 0, 0

        self.draw_time = 0
        self.processing_time = 0

        # 创建地板
        floor_height = 80
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        shape = pymunk.Segment(body, [0, floor_height], [SCREEN_WIDTH, floor_height], 0.0)
        shape.friction = 10
        self.space.add(shape)
        self.static_lines.append(shape)

        # 开始叠箱子--请用for循环优化下面的代码
        box = make_sprite(43,"images/boxCrate_double.png",(1000,  130),self.space)
        self.sprite_list.append(box) 
        box = make_sprite(43,"images/boxCrate_double.png",(1000,  230),self.space)
        self.sprite_list.append(box) 
        box = make_sprite(43,"images/boxCrate_double.png",(1000,  330),self.space)
        self.sprite_list.append(box) 
        box = make_sprite(43,"images/boxCrate_double.png",(1000,  430),self.space)
        self.sprite_list.append(box) 
        box = make_sprite(43,"images/boxCrate_double.png",(1000,  530),self.space)
        self.sprite_list.append(box)          
  

        # 创建猪               
        sprite = make_sprite(33,"images/pig.png",(1000, 620),self.space)
        self.sprite_list.append(sprite)        

        # 创建小鸟的平台        
        sprite = make_sprite(33,"images/platform.png",(160, 160),self.space)
        self.sprite_list.append(sprite)        

        # 创建物理小鸟
        self.shoot_position = pymunk.Vec2d(160 , 290)             
        self.physic_bird = make_sprite(33,"images/bird.png",self.shoot_position,self.space)
        self.sprite_list.append(self.physic_bird)        
        
        # 创建virtual小鸟，它是用来被拖曳的，它并不加入到所有角色列表，需要单独渲染       
        self.virtual_bird = arcade.Sprite("images/bird.png")#  被拖曳的小鸟
        self.virtual_bird.center_x = self.shoot_position[0]
        self.virtual_bird.center_y = self.shoot_position[1]  

        self.reset_shoot = True
        
    def reset_shoot_bird(self):
        """重新发射"""
        self.virtual_bird.center_x = self.shoot_position[0]
        self.virtual_bird.center_y = self.shoot_position[1]
        self.physic_bird.pymunk_shape.body.velocity = (0,0)
        self.physic_bird.pymunk_shape.body.position = self.shoot_position
        self.physic_bird.pymunk_shape.body.angle = 0 
        
        self.reset_shoot = True
        self.shape_being_dragged = None
        
    def on_key_press(self, key, modifiers):
        """
        当按键时调用此方法
        """
        if key == arcade.key.SPACE:
           self.reset_shoot_bird()       
        
         
    def on_draw(self):
        """
        渲染屏幕
        """

        # 开始渲染屏幕
        arcade.start_render()

        # 开始计时
        draw_start_time = timeit.default_timer()

        # 画背景图片
        self.background.draw()

        # 画所有的角色
        self.sprite_list.draw()

        # 画静止的线条
        for line in self.static_lines:
            body = line.body
            pv1 = body.position + line.a.rotated(body.angle)
            pv2 = body.position + line.b.rotated(body.angle)
            arcade.draw_line(pv1.x, pv1.y, pv2.x, pv2.y, arcade.color.WHITE, 2)

        if self.reset_shoot :  self.virtual_bird.draw()

        # 画皮筋
        x1,y1 = self.shoot_position
        x2,y2 = self.virtual_bird.position
        dd = (x1-x2)*(x1-x2) + (y1-y2)*(y1-y2)
         
        if dd>2 and self.reset_shoot:
          arcade.draw_line(x1, y1, x2, y2, arcade.color.ORANGE, 4)


        # 画抛物线
        print(len(self.parabolic_points),self.reset_shoot,self.dx,self.dy)
        if self.reset_shoot :          
           for point in self.parabolic_points:
               arcade.draw_circle_outline(point[0],point[1], 5, arcade.color.WISTERIA, 3)          
        

        # 画时间
        output = f"处理时间: {self.processing_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 20, arcade.color.WHITE, 12,font_name='simhei')

        output = f"绘画时间: {self.draw_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 40, arcade.color.WHITE, 12,font_name='simhei')

        self.draw_time = timeit.default_timer() - draw_start_time

    def on_mouse_press(self, x, y, button, modifiers): 
        
        if button == arcade.MOUSE_BUTTON_LEFT :  
            self.shape_being_dragged = self.virtual_bird 

    def on_mouse_release(self, x, y, button, modifiers):
        
        physic_bird_position = self.physic_bird.pymunk_shape.body.position 
        distance = (physic_bird_position.get_distance(self.shoot_position)) 
        if distance > 1 :return
        
        if button == arcade.MOUSE_BUTTON_LEFT:
            # 松开
            self.shape_being_dragged = None              
            self.dx = x - self.shoot_position[0]
            self.dy = y - self.shoot_position[1]
            print("发射",self.dx,self.dy)
            self.physic_bird.pymunk_shape.body.force = -self.dx*20000, -self.dy*20000
            self.reset_shoot = False
            self.dx = 0
            self.dy = 0
            self.parabolic_points = []

    def on_mouse_motion(self, x, y, dx, dy):
        if self.shape_being_dragged is not None:
            # 抓住了某个物体，让它跟随鼠标指针            
            
            self.virtual_bird.center_x = x
            self.virtual_bird.center_y = y
            self.dx = x - self.shoot_position[0]
            self.dy = y - self.shoot_position[1]

            # 计算抛物线点
            print("self.dx,self.dy",self.dx,self.dy)
            gx,gy = self.space.gravity
            gy = -gy/100
            self.parabolic_points = []
            x , y = self.shoot_position
        
            for i in range(20):                   # 画的点的个数
                x = x - self.dx
                y = y - self.dy
                self.dy = self.dy + gy            # 垂直速度不断变小                 
                self.parabolic_points.append((x,y))             
            

    def update(self, delta_time):
         
        start_time = timeit.default_timer()        
        self.virtual_bird.update()
        
        # 检测每一个角色，移除y坐标小于0的
        for sprite in self.sprite_list:
            if self.physic_bird == sprite:continue         # 排除物理小鸟
            if sprite.pymunk_shape.body.position.y < 0:
                # 从重力空间中移除
                self.space.remove(sprite.pymunk_shape, sprite.pymunk_shape.body)
                # 从列表中删除 
                sprite.kill()

        self.space.step(1 / 60.0)
 
        # 把角色统统移到它的物理坐标
        for sprite in self.sprite_list:
            sprite.center_x = sprite.pymunk_shape.body.position.x
            sprite.center_y = sprite.pymunk_shape.body.position.y
            sprite.angle = math.degrees(sprite.pymunk_shape.body.angle)

        # 保存时间
        self.processing_time = timeit.default_timer() - start_time

          

def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT,SCREEN_TITLE)

    arcade.run()


if __name__ == "__main__":
    main()

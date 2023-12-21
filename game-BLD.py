#main.py
#Felix 
#Culminating
#Jan 20th 2023
# A first person shooter game using Ursina engine.

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
from direct.actor.Actor import Actor
import random

app = Ursina(title ="cool game :)",fullscreen = False)

Entity.default_shader = lit_with_shadows_shader 

ground = Entity(model='plane', collider='box', scale=100, texture='test_tileset', origin_y=0, texture_scale=(4,4))

player = FirstPersonController(model='cube', z=-10, color=color.blue, speed=6,enabled = False) # allows for first person control, like moving the camera and moving around the enviroment

gun = Entity(model='none', parent=camera , world_position = (-0.05,0.4,-10.1), color=color.black, on_cooldown=True, ammo = 30) 

# The gun model is made up of 3 seperate parts. This is due to Ursina not supporting static models with animations.
model = Actor("model.glb")
mag = Actor("mag.glb")
spare = Actor("spare.glb")

gun_parts = [model,mag,spare]

for i in gun_parts: #sets up the animated models
    i.setColor(0)
    i.reparent_to(gun)
    i.pose("reload",170)
     
gun.reticle = Entity(parent=camera,position=(1,0.1,-2), world_scale=0.3, model='quad', z=2,color=color.rgba(255,153,51,180),enabled=False)#square that pops up when scoping in
crosshair = Animation(name = 'crosshair', parent = camera.ui, scale = 0.05)
ammo_count = Text("", origin=(-6,4), scale=4) # ammo counter

shootables_parent = Entity()  #Any object is shootable
mouse.traverse_target = shootables_parent # Mouse can collide with every object.

def toggle_attributes(**kwargs): #takes in a object and attribute and sets the attribute to the opposite of its value
    for obj, attr in kwargs.items():
        try:
            i = globals()[obj]
            setattr(i, attr, not getattr(i, attr))
        except:
            pass
            
    
def enable_player(): # enables player controls
    toggle_attributes(player = "enabled", gun = "on_cooldown")
    menu.make_visible() 
    
def credits(): # activates credits
    menu.credit_text.visible = not menu.credit_text.visible
    menu.credit_text_2.visible = not menu.credit_text_2.visible
    menu.make_visible()
       
class Menu(Entity): #defines the main menu
    title = Text("Cool FPS Game :))))",origin = (-0.03,-2),visible = False, color = color.green , scale = 6)
    credit_text = Text("made by felix",origin = (-0.03,-2),visible = False, color = color.green , scale = 5)
    credit_text_2 = Text("press tab to go back",origin = (-0.03,4),visible = False, color = color.orange , scale = 3)
    buttons = [Button(parent = camera.ui,text='hi', radius=.1, scale = (0.2,0.1,0.2),visible = False, y = (i*0.25)-0.4) for i in range(3)]
    buttons[0].text = "credits"
    buttons[1].text = "quit"
    buttons[2].text = "play"
    
    buttons[1].on_click = quit
    buttons[2].on_click = enable_player
    buttons[0].on_click = credits
    
    def make_visible(cls): # makes the title and buttons visible or not visible
        
        cls.title.visible= not cls.title.visible
       
        for i in cls.buttons:
            i.visible = not i.visible
   
              
class Enemy(Entity): #defines an enemy with attributes health, and a head
    def __init__(self, **kwargs): #self refers to the instance, while kwargs refers to multiple of the same class
        super().__init__(parent=shootables_parent, model='cube', scale_y=1.8, origin_y=-.5, color=color.light_gray, collider='box', **kwargs)
        self.head = Entity(name = "head",parent=self, y=1.1, collider='box',model='cube', color=color.orange, world_scale=(0.7,0.8,0.7)) #headshots are not functional
        self.health_bar = Entity(parent=self, y=1.4, model='cube', color=color.red, world_scale=(1.5,.1,.1))
        self.max_hp = 100
        self.hp = self.max_hp
       
    @property # gets hp
    def hp(self):
        return self._hp
        
    @hp.setter #from our shoot function, it subtracts its health by 10 until the enemy is dead. Then it disposes itself.
    def hp(self, value):
        self._hp = value
        if value <= 0:
            enemies.pop()
            destroy(self)
            return
        
        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5 #health bar
        self.health_bar.alpha = 1
   
menu = Menu() # initalizes menu
menu.make_visible()

enemies = [Enemy(x=random.uniform(-12,12), z=random.uniform(-8,8)) for i in range(8)] #spawn initial enemies

def input(key): #when a key is pressed, this function is called
   
    if key == 'escape':
        quit()
        
    if key == 'tab' and not player.enabled:
      credits()
    
    elif key == 'tab':
       enable_player()
      
    if key == 'right mouse down':
        zoom()
        
    if key =='r': #reload
        model.play("reload")
        mag.play("reload_Armature.001")
        spare.play("Action")
      
        invoke(setattr,gun,'ammo', gun.ammo + (30-gun.ammo), delay = 5.8) #sets ammo to 30 after reload
    if key == 'y': #inspect
         model.play("inspect.002")
         mag.play("inspect")
         spare.pose("Action",200)
         
      
def update(): #called every frame
    
    if len(enemies) < 8: # if an enemy dies spawn a new one
        enemies.insert(1,Enemy(x=random.uniform(-12,12), z=random.uniform(-8,8)))
        
    ammo_count.text = gun.ammo #updates ammo text
    gun.reticle.x = gun.x +0.15 # reticle (yellow square) goes along with gun
    
    if held_keys['left mouse']: # shoots if not reloading
        if gun.ammo > 0 or not menu.credit_text.visible:
            try:
                if not (150 > model.get_current_frame() > 1): #can't fire while reloading
                    shoot()
                   
            except:
                shoot()
          
        
    if held_keys['right mouse']: #scope in
         if gun.reticle.enabled == True and gun.position.x >= -0.15:
           invoke(setattr, gun, 'x', gun.position.x-.01, delay=.0001) # invoke calls a function with a delay
         elif gun.reticle.enabled  == False and gun.position.x <= 0.08:
           invoke(setattr, gun, 'x', gun.position.x+.01, delay=.0001)
        
         
from ursina.prefabs.ursfx import ursfx
def shoot(): # subtracts health from target, plays sound, put gun on cool down.
    if not gun.on_cooldown:
        gun.on_cooldown = True
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.1, wave='noise', pitch=random.uniform(-13,-12), pitch_change=-12, speed=3.0)
        invoke(setattr,gun,'rotation_x', gun.rotation_x - 5,delay=0) #firing animation
        invoke(setattr,gun,'rotation_x', gun.rotation_x + 5,delay=0.1)#firing animation
        invoke(setattr, gun, 'ammo', gun.ammo-1, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'): # If object is vaild and has hp, then subtract it's health.
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)    
            
def zoom():  
    gun.reticle.enabled = not gun.reticle.enabled
    

sun = DirectionalLight()
sun.look_at(Vec3(1,-1,1))
Sky()

app.run()

# Leap OS 1.2

import os
add_library('minim')
player = Minim(this)
add_library('sound')

# Import the processing module
from processing import *
import random
# Constants
resolution = (600,900)
Gravity = 3
highscore = 0
Jump_vel = 40 #jump velicty when ninja lands on platforms


class main_app():
    def __init__(self, w, h):
        self.Game = game(w, h)
        self.pause = False
        self.Game.over = True
        self.start = False
        self.start_image = loadImage(os.getcwd() + "/images/StartImage.png")
        self.menuMusic = player.loadFile(os.getcwd()+"/sounds/Menu.mp3")
        self.bgMusic = player.loadFile(os.getcwd()+"/sounds/Gameplay.mp3")
        self.bgMusic.loop()
        
    def update(self):
        if self.pause:
            pass
        else:
            self.Game.update()
        if self.Game.over:
            pass
                
    def display(self):
        if not self.start:
            # displays prologue to the game
            img = loadImage(os.getcwd()+"/images/StartScreen.png")
            image(self.start_image, 0, 0)
            self.menuMusic.play()
        else:
            # begins game once player moves past the prologue
            self.menuMusic.pause()    
            self.Game.display()
                
class game():
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.ninja = ninja(150,350,63,77)
        self.platforms = []
        self.browns = []
        # initial platforms
        self.platforms.append(Green_p(350,800))
        self.platforms.append(Blue_p(50,750))
        self.platforms.append(Green_p(150,700))
        self.platforms.append(Green_p(500,550))
        self.platforms.append(Green_p(100,600))
        self.platforms.append(Green_p(400,350))
        self.platforms.append(Green_p(250,200))
        self.platforms.append(Green_p(150,100))
        self.distance = 0
        self.score = 0
        self.g_o_h = self.h + 50 # y-coordinate of 'game over' height
        self.scoreY = 20
        self.P_options = ["Green", "Blue", "Yellow", "Purple"]
        self.P_weights = [0.7,0.3,0,0]
        self.highscore = highscore
        self.over = False
        self.overmessage = "Game Over!"
        self.dojo= loadImage(os.getcwd()+"/images/Background/Dojo.png")
        self.dojo.resize(resolution[0], resolution[1])
        self.dojoY = 0
        self.morning = loadImage(os.getcwd()+"/images/Background/Morning.png")
        self.morning.resize(resolution[0], resolution[1])
        self.morningY = -self.h # y-coordinate of morning background
        self.night = loadImage(os.getcwd()+"/images/Background/Night.png")
        self.night.resize(resolution[0], resolution[1])
        self.nightY = -self.h # y-coordinate of night background
        self.night2 = loadImage(os.getcwd()+"/images/Background/Space1.jpeg")
        self.night2.resize(resolution[0], resolution[1])
        self.night2Y = -self.h
        self.night3 = loadImage(os.getcwd()+"/images/Background/Space2.jpeg")
        self.night3.resize(resolution[0], resolution[1])
        self.night3Y = -self.h
        self.fade_alpha = 255
        self.obstacles = []
        self.obstacle_spawn_timer = 0
        self.min_spawn_interval = 90 
        self.max_spawn_interval = 300
        self.collided = False
          
        
    def display(self):
        image(self.morning, 0, self.morningY)
        image(self.night, 0, self.nightY)
        image(self.night3, 0, self.night2Y)
        tint(255, self.fade_alpha)
        image(self.night2, 0, self.night2Y)
        noTint()
        image(self.dojo, 0, self.dojoY)
        
        for p in self.platforms:
            p.display()
        for b in self.browns:
            b.display()
            
        for obstacle in self.obstacles:
            obstacle.display()
        
        self.ninja.display()
        #print(self.ninja.x, self.platforms[0].x + self.platforms[0].w)
        fill(255,255,255)
        textSize(16)
        text("Score:" + str(self.score/10), 320, self.scoreY)
        textSize(30)
        textAlign(CENTER)
        text(self.overmessage, self.w/2, self.g_o_h)
        if self.highscore < self.score//10:
            self.highscore = self.score//10
        text("Your Score: "+ str(self.score//10), self.w/2, self.g_o_h + 50)
        text("High Score: "+ str(self.highscore), self.w/2, self.g_o_h + 100)
        textSize(20)
        fill(0,0,0)
        text("-CLICK SCREEN TO PLAY AGAIN-", self.w/2, self.g_o_h + 450)
        
    def update(self):
        if self.over!=True:  
            self.obstacle_create()      
            for obstacle in self.obstacles:
                if obstacle.check_collision(self.ninja)==True or self.collided:
                    if obstacle.type=='Monster':
                        # Handling collision with monster/assassin
                        indices=[]
                        for i in range(len(self.platforms)):
                            if self.platforms[i].y > self.ninja.y:
                               indices.append(i)
                        for i in indices:
                            del self.platforms[i]
                        obstacle.apply_effect(self.ninja)
                    elif obstacle.type=='BlackHole':
                        #Handling collision with black hole
                        self.ninja.y = self.h + 50  #moves ninja to the bottom of the screen
                        obstacle.apply_effect(self.ninja)  
                    self.collided = True
                    self.ninja.vy = 20
                
        self.ninja.update()
        
        # checks collision with platforms
        for p in self.platforms:
            if p.check_collision() and not self.over:
                if p.y == self.ninja.y + self.ninja.h:
                    if p == "Purple":
                        self.ninja.xy = -30*p.side
                    self.ninja.vy = -Jump_vel        # jump
                elif not self.collided:
                    self.ninja.y = p.y - self.ninja.h
                    self.ninja.vy = 0
                self.shift()
        
        # checks collision with brown (decoy) platforms                
        for b in self.browns:
            b.check_collision()

        for obstacle in self.obstacles:
            obstacle.update()
        
        
        # checks if distance is greater than a=score and updates score accordingly    
        self.score = max(self.score, -self.distance)
        if self.ninja.x > self.w:
            self.ninja.x = 0
        if self.ninja.x < 0:
            self.ninja.x = self.w
            
    # randomly returns a type of platform       
    def get_type(self):
        sum = 0.0
        for x in self.P_weights:
            sum += x
        rand_num = random.randint(0,int(sum*100))
        rand_num = float(rand_num)/100
        #print(sum, rand_num)
        if rand_num < self.P_weights[0]:
                    return "Green"
        elif rand_num < self.P_weights[0]+self.P_weights[1]:
                    return "Blue"
        elif rand_num < self.P_weights[0]+self.P_weights[1]+self.P_weights[2]:
                    return "Yellow"
        elif rand_num < self.P_weights[0]+self.P_weights[1]+self.P_weights[2]+self.P_weights[3]:
                    return "Purple"
        else:
                    return "Empty"
    
    # shifts all elements in the game             
    def shift(self):
        if self.ninja.excalibur != None:
            indices=[]
            for i in range(len(self.platforms)):
                if self.platforms[i].y > self.ninja.y:
                    indices.append(i)
            for i in indices:
                    del self.platforms[i]
            if self.dojoY > 0:
                self.dojoY -= self.ninja.vy
            if self.g_o_h > self.h/2 - 100:
                self.g_o_h -= self.ninja.vy
            self.scoreY -= self.ninja.vy
            self.over = True
            self.overmessage = "Congratulations Ninja!"
            self.ninja.y -= self.ninja.vy
            
        elif (self.ninja.y <= self.h/2 and self.ninja.vy < 0):
            self.ninja.y -= self.ninja.vy
            #print(self.ninja.vy)
            self.distance += self.ninja.vy
            
            #deleting old platforms
            for i in range(len(self.browns)-1):
                self.browns[i].y -= self.ninja.vy
                if self.h < self.browns[i].y:
                    del self.browns[i]
                    break 
                
            for i in range(len(self.platforms)-1):
                self.platforms[i].y -= self.ninja.vy
                if self.h < self.platforms[i].y:
                    if (self.platforms[i].powerup != None and 
                        (self.platforms[i].powerup.type == "Ninja Thrusters" or self.platforms[i].powerup.type == "Shurkin") 
                            and self.platforms[i].powerup.activated):
                        pass
                    else:
                        del self.platforms[i]
                        break 
                    
            #deleting old obstacles    
            for i in range(len(self.obstacles)):
                self.obstacles[i].y -= self.ninja.vy
                if self.h < self.obstacles[i].y-self.obstacles[i].h:
                    del self.obstacles[i]
                    break
            
            #creating new platforms
            if self.distance < self.platforms[len(self.platforms)-1].y - 100:
                type = self.get_type()
                self.plat_create(type)
                self.P_weights[0] += 0.01
                self.P_weights[2] += 0.02
                self.P_weights[3] += 0.02
                
            # shifting background images
            if self.distance < -9999 and self.dojoY < self.h:
                self.dojoY -= self.ninja.vy/4
                self.morningY -= self.ninja.vy/4
            if self.distance < -19999 and self.nightY < 0:
                self.nightY -= self.ninja.vy/4
            if self.distance < -29999 and self.night2Y < 0:
                self.night2Y -= self.ninja.vy/4
                self.night3Y -= self.ninja.vy/4
            if self.distance < -39999:
                if self.fade_alpha > 0:
                    self.fade_alpha -= 2
            if self.distance < -99999 and self.overmessage == "Game Over!":
                self.platforms.append(Green_p(random.randint(10,self.w-80), -1000, "Excalibur"))
                self.overmessage = "You almost had it! Better luck next time..."
                
        # shifts all elements up when ninja falls below the screen        
        elif (self.ninja.y >= self.h) or self.over:
            if self.dojoY > 0:
                self.dojoY -= self.ninja.vy
            if self.g_o_h > self.h/2 - 100:
                self.ninja.y -= self.ninja.vy
                self.ninja.y -= 3
                self.g_o_h -= self.ninja.vy
            self.scoreY -= self.ninja.vy
            for i in range(len(self.platforms)):
                self.platforms[i].y -= self.ninja.vy
            for i in range(len(self.browns)):
                self.browns[i].y -= self.ninja.vy
            for i in range(len(self.obstacles)):
                self.obstacles[i].y -= self.ninja.vy
            self.over = True

            
    def get_powerup(self):
        rand_num = random.randint(0,100)
        rand_num = float(rand_num)/100
        #print(rand_num)
        if rand_num < 0.05:
                    return "Ninja Thrusters"
        elif rand_num < 0.1:
                    return "Trampoline"
        elif rand_num < 0.2:
                    return "Shurkin"
        elif rand_num < 0.4:
                    return "Spring"
        else:
                    return None
                
    def plat_create(self, type, powerup = None):
        if powerup == None:
            powerup = self.get_powerup()
        if type == "Green":
            self.platforms.append(Green_p(random.randint(10,self.w-80), self.distance, powerup))
        elif type == "Blue":
            self.platforms.append(Blue_p(random.randint(10,self.w-80), self.distance, powerup))
        elif type == "Yellow":
            if (powerup == "Ninja Thrusters" or powerup == "Shurkin"):
                powerup = None
            self.platforms.append(Yellow_p(random.randint(10,self.w-80), self.distance, powerup))
        elif type == "Purple":
            self.platforms.append(Purple_p(random.randint(10,self.w-80), self.distance, powerup))
        
        # generates brown platforms
        C = random.randint(1,100)
        if C > 40 and self.distance > -20000:
            self.browns.append(Brown_p(random.randint(10,self.w-80), self.distance))

    def obstacle_create(self):
        l=['BlackHole','Monster']
        rand_index=random.randint(0,1)
        type=l[rand_index]
        if self.score // 10 >= 3000:
            if type == 'BlackHole' and random.random() < 0.02 and self.obstacle_spawn_timer <= 0 and len(self.obstacles)<1:
                self.obstacles.append(BlackHole(random.randint(10, self.w - 150), 100, 150))
                self.obstacle_spawn_timer = random.randint(self.min_spawn_interval, self.max_spawn_interval)
                
            elif type == 'Monster' and random.random() < 0.02 and self.obstacle_spawn_timer <= 0 and len(self.obstacles)<1:
                self.obstacles.append(Monster(random.randint(10, self.w - 10 - 30), 100, 90, 5))
                self.obstacle_spawn_timer = random.randint(self.min_spawn_interval, self.max_spawn_interval)
            
            if self.obstacle_spawn_timer > 0 and len(self.obstacles)==0:
                self.obstacle_spawn_timer -= 1
            
        elif self.score // 10 >= 1000:
            if type == 'Monster' and random.random() < 0.02 and self.obstacle_spawn_timer <= 0 and len(self.obstacles)<1:
                self.obstacles.append(Monster(random.randint(10, self.w - 10 - 30), 150, 90, 5))
                self.obstacle_spawn_timer = random.randint(self.min_spawn_interval, self.max_spawn_interval)
                
            if self.obstacle_spawn_timer > 0 and len(self.obstacles)==0:
                self.obstacle_spawn_timer -= 1
                
            
class ninja():
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.vx = 0
        self.vy = 0
        self.terminal_vel = 20
        self.cnt = 0
        self.images = []
        for i in range(1,8):
            img1 = "/images/Ninja_sprites/Pos{}_scarf1.PNG".format(i)
            img2 = "/images/Ninja_sprites/Pos{}_scarf2.PNG".format(i)
            self.images.append(loadImage(os.getcwd() + img1))
            self.images.append(loadImage(os.getcwd() + img2))
        self.excalibur = None
        self.shurkin = None
        self.jetpack = None
    
    def update(self):
        self.move()
        Window.Game.shift()
        self.gravity()
        
    def move(self):
        self.x += self.vx
        self.y += self.vy
        
    def gravity(self):
        if self.vy < self.terminal_vel:
            self.vy += Gravity
            
    def display(self):
        if self.excalibur == None and self.shurkin == None:
            if self.vx == 0:
                image(self.images[random.choice([7,6])], self.x, self.y, self.w, self.h)
            elif self.vx > 0:
                image(self.images[int(self.cnt)+7], self.x, self.y, self.w, self.h)
            elif self.vx < 0:
                image(self.images[int(self.cnt)], self.x, self.y, self.w, self.h)
            self.cnt += 0.01
            if self.cnt > 7:
                self.cnt = 0
        elif self.shurkin == None:
            image(self.excalibur, self.x, self.y, 111, 132)
        else:
            image(self.shurkin, self.x, self.y, self.w, self.h)


# Platform class
class Platform():
    def __init__(self, x, y, powerup = None):
        self.x = x
        self.y = y
        self.w = 80
        self.h = 20
        self.a = 0
        self.put_power_up(powerup)
    def update(self):
        if self.powerup != None:
            if self.powerup.type == "Spring":
                if not self.powerup.activated:
                    self.powerup.x = self.x + 50
                    self.powerup.y = self.y - 20
                else:
                    self.powerup.x = self.x + 50
                    self.powerup.y = self.y - 40
            elif self.powerup.type == "Shurkin":
                self.powerup.x = self.x + 40
                self.powerup.y = self.y - 30
            elif self.powerup.type == "Trampoline":
                self.powerup.x = self.x + 30
                self.powerup.y = self.y - 20
            elif self.powerup.type == "Ninja Thrusters":
                self.powerup.x = self.x + 30
                self.powerup.y = self.y - 50
            elif self.powerup.type == "Excalibur":
                self.powerup.x = self.x
                self.powerup.y = self.y - 90
                
    def display(self):
        fill(0, 200, 0)
        quad(self.x, self.y, self.x + self.w, self.y,  self.x + self.w, self.y + self.h, self.x, self.y + self.h)
    def __repr__ (self):
        return "Default"
    def put_power_up(self, powerup):
        if powerup == "Spring":
            self.powerup = spring(self)
        elif powerup == "Shurkin":
            self.powerup = shurkin(self)
        elif powerup == "Ninja Thrusters":
            self.powerup = jetPack(self)
        elif powerup == "Trampoline":
            self.powerup = trampoline(self)
        elif powerup == "Excalibur":
            self.powerup = excalibur(self)
        else:
            self.powerup = None
            
    def check_collision(self):
        return ((not Window.Game.ninja.vy < 0) and 
                ( self.x - 10 <= Window.Game.ninja.x < self.x + self.w*1.2 
                  and Window.Game.ninja.y <= self.y <= Window.Game.ninja.y + Window.Game.ninja.h))

class Green_p(Platform):
    def __init__(self, x, y, powerup = None):
        Platform.__init__(self,x,y, powerup)
        self.img = loadImage(os.getcwd() + "/images/Platforms/Green_Platform.png")
    def display(self):
        self.update()
        image(self.img, self.x, self.y, self.w, self.h)
        if self.powerup != None:
            self.powerup.display()
    def __repr__ (self):
        return "Green " + str(self.y)
            
class Brown_p(Platform):
    def __init__(self, x, y):
        powerup = None
        Platform.__init__(self,x,y, powerup)
        self.img1 = loadImage(os.getcwd() + "/images/Platforms/Brown_Platform.PNG")
        self.img2 = loadImage(os.getcwd() + "/images/Platforms/Brown_Platform2.PNG")
        self.img3 = loadImage(os.getcwd() + "/images/Platforms/Brown_Platform3.PNG")
        self.count = 0
        self.jumped = False
    def __repr__ (self):
        return "Brown " + str(self.y)
    def display(self):
        if self.jumped:
            self.count += 1
            if self.count < 10:
                image(self.img2, self.x, self.y, self.w + 10, self.h + 10)
            elif self.count < 40:
                image(self.img3, self.x, self.y, self.w + 30, self.h + 30)
                self.y += 2
        elif self.count == 0:
            image(self.img1, self.x, self.y, self.w, self.h)

    def check_collision(self):
        if (    (not Window.Game.ninja.vy < 0) and 
                ( self.x - 10 <= Window.Game.ninja.x < self.x + self.w*1.2 ) and 
                (Window.Game.ninja.y <= self.y <= Window.Game.ninja.y + Window.Game.ninja.h)  ):
            self.jumped = True
            return False
            
class Blue_p(Platform):
    def __init__(self, x, y, powerup = None):
        Platform.__init__(self,x,y, powerup)
        self.img = loadImage(os.getcwd() + "/images/Platforms/Blue_Platform.png")
        self.vx = 3
        self.w_lim = range(self.x - 100, self.x + 100)
    def move(self):
        self.x += self.vx
        if self.x not in self.w_lim:
            self.vx = -self.vx
    def __repr__ (self):
        return "Blue " + str(self.y)
    def display(self):
        image(self.img, self.x, self.y, self.w, self.h)
        self.move()
        self.update()
        if self.powerup != None:
            self.powerup.display()

class Yellow_p(Platform):
    def __init__(self, x, y, powerup = None):
        Platform.__init__(self,x,y, powerup)
        self.img = loadImage(os.getcwd() + "/images/Platforms/Yellow_Platform.png")
        self.afterImg = loadImage(os.getcwd() + "/images/Platforms/Red_Platform.png")
        self.count = 0
        self.jumped = False
    def __repr__ (self):
        return "Yellow " + str(self.y)
    def display(self):
        self.update()
        if self.jumped and self.count < 10:
            self.count += 1
            image(self.afterImg, self.x, self.y, self.w, self.h)
        elif self.count == 0:
            image(self.img, self.x, self.y, self.w, self.h)
        else:
            self.powerup = None
            self.h = 1
            self.w = 1
        if self.powerup != None:
            self.powerup.display()
    def check_collision(self):
        if (  self.x -10 <= Window.Game.ninja.x < self.x + self.w*1.2 and Window.Game.ninja.y <= self.y <= Window.Game.ninja.y + Window.Game.ninja.h):
            self.jumped = True
            return True
        
class Purple_p(Platform):
    def __init__(self, x, y, powerup = None):
        Platform.__init__(self,x,y, powerup)
        self.img = loadImage(os.getcwd() + "/images/Platforms/Purple_Platform.png")
        self.side = random.choice([-1,1])
        self.h = self.h*2
    def __repr__ (self):
        return "Purple " + str(self.y)
    def display(self):
        self.update()
        if self.side == 1:
            image(self.img, self.x, self.y, self.w, self.h, 0, 0, 661, 405)
        else:
            image(self.img, self.x, self.y, self.w, self.h, 661, 0, 0, 405)
    def check_collision(self):
        return (  self.x - 10 <= Window.Game.ninja.x < self.x + self.w and Window.Game.ninja.y <= self.y <= Window.Game.ninja.y + Window.Game.ninja.h)
    
class power_up():
    def __init__(self, platform):
        self.platform = platform
        self.x = platform.x + 50
        self.y = platform.y - 20
        self.activated = False
        self.show = True
        
    def update(self):
        #print(self.x, Game.ninja.x, self.x + self.w )
        if self.check_collision():
            self.activated = True
            return True
    
    def check_collision(self):
        if (  self.x - self.w <= Window.Game.ninja.x < self.x + self.w and Window.Game.ninja.y - Window.Game.ninja.h + 15 <= self.y <= Window.Game.ninja.y + Window.Game.ninja.h - 15):
            return True

class spring(power_up):
    def __init__(self, platform):
        power_up.__init__(self, platform)
        self.w = 20
        self.h = 20
        self.img = loadImage(os.getcwd() + "/images/Powerups/Spring_1.PNG")
        self.type = "Spring"
        self.sound=SoundFile(this, os.getcwd() + '/sounds/Spring.mp3')
        self.sound.amp(1.0)
        self.sound_played=False
        
    def display(self):
        if self.update():
                Window.Game.ninja.vy = -70
                self.y -= 20
                self.h += 20
                self.img = loadImage(os.getcwd() + "/images/Powerups/Spring_2.PNG")
        if self.show:
            self.img.resize(self.w,self.h)
            if self.activated and not self.sound_played:
                self.sound.play()
                self.sound_played=True
            image(self.img, self.x, self.y)

class shurkin(power_up):
    def __init__(self, platform):
        power_up.__init__(self, platform)
        self.w = 50
        self.h = 60
        self.y -= 10
        self.img = loadImage(os.getcwd() + "/images/Powerups/Shurkin_spinner.png")
        self.img.resize(self.w,self.h)
        self.type = "Shurkin"
        self.sound=SoundFile(this, os.getcwd() + "/sounds/Shurkin.mp3")
        self.sound.amp(1.0)
        self.sound_played=False
        self.Nin_img1 = loadImage(os.getcwd() + "/images/Ninja_sprites/Shurkin_spinner1.PNG")
        self.Nin_img2 = loadImage(os.getcwd() + "/images/Ninja_sprites/Shurkin_spinner2.PNG")
        self.activated = False
        self.cnt = 0
    def display(self):
        if self.activated and self.cnt < 30:
            if self.cnt == 1:
                if Window.Game.ninja.shurkin == None:
                    Window.Game.ninja.w = 84*1.1
                    Window.Game.ninja.h = 96*1.1
            else: 
                if self.cnt % 2 == 0:
                    Window.Game.ninja.shurkin = self.Nin_img1
                else:
                    Window.Game.ninja.shurkin = self.Nin_img2
            Window.Game.ninja.vy = -50
            self.cnt += 1 
        elif self.activated == False:
            if self.cnt == 30:
                Window.Game.ninja.shurkin = None
            elif self.update():
                self.h = 60
                self.cnt = 1
            image(self.img, self.x, self.y)
        else:
            Window.Game.ninja.shurkin = None
            Window.Game.ninja.w = 63
            Window.Game.ninja.h = 77
        if self.activated and not self.sound_played:
            self.sound.play()
            self.sound_played=True
                

class trampoline(power_up):
    def __init__(self, platform):
        power_up.__init__(self, platform)
        self.w = 40
        self.h = 20
        self.x -= 20
        self.y += 10
        self.img1 = loadImage(os.getcwd() + "/images/Powerups/Trampoline_1.png")
        self.img1.resize(self.w,self.h)
        self.img2 = loadImage(os.getcwd() + "/images/Powerups/Trampoline_2.png") 
        self.img2.resize(self.w,self.h)
        self.img3 = loadImage(os.getcwd() + "/images/Powerups/Trampoline_3.png")
        self.img3.resize(self.w,self.h)
        self.main_img = self.img1
        self.cnt = 0
        self.type = "Trampoline"
        self.sound=SoundFile(this, os.getcwd() + "/sounds/Trampoline.mp3")
        self.sound.amp(1.0)
        self.sound_played=False
        
    def display(self):
        if self.activated:
            if self.cnt < 5:
                Window.Game.ninja.vy = -70
                self.cnt += 1 
                self.main_img = self.img2 
            elif self.cnt == 10: 
                Window.Game.ninja.vy = -70 
                self.cnt += 1 
                self.main_img = self.img3 
            elif self.cnt < 15: 
                Window.Game.ninja.vy = -70 
                self.cnt += 1 
            else:
                self.main_img = self.img1
        else:
            if self.update():
                Window.Game.ninja.vy = -70
        if self.activated and not self.sound_played:
                self.sound.play()
                self.sound_played=True
        image(self.main_img, self.x, self.y)


class jetPack(power_up):
    def __init__(self, platform):
        power_up.__init__(self, platform)
        self.w = 50
        self.h = 50
        self.img1 = loadImage(os.getcwd() + "/images/Powerups/jetpack1.PNG")
        self.img1.resize(self.w,self.h)
        self.img2 = loadImage(os.getcwd() + "/images/Powerups/jetpack2.PNG")
        self.img2.resize(self.w,self.h)
        self.img3 = loadImage(os.getcwd() + "/images/Powerups/jetpack3.PNG")
        self.img3.resize(self.w,self.h)
        self.img4 = loadImage(os.getcwd() + "/images/Powerups/jetpack4.PNG")
        self.img4.resize(self.w,self.h)
        self.main_img = self.img1
        self.type = "Ninja Thrusters"
        self.cnt = 0
        self.sound=SoundFile(this, os.getcwd() + "/sounds/JetPack.mp3")
        self.sound.amp(1.0)
        self.sound_played=False
        
    def display(self):
        if self.activated:
            Window.Game.ninja.jetpack = "Something"
        else:
            Window.Game.ninja.jetpack = None
        if self.activated and self.cnt < 100:
            if self.cnt < 5:
                self.main_img = self.img2
            else:
                if self.cnt%2 == 0:
                    self.main_img = self.img3
                else:
                    self.main_img = self.img4
            Window.Game.ninja.vy = -50
            self.cnt += 1 
            self.x = Window.Game.ninja.x - 4
            self.y = Window.Game.ninja.y
        else:
            self.main_img = self.img1
            self.activated = False
            if self.update():
                cnt = 1
        if self.activated and not self.sound_played:
                self.sound.play()
                self.sound_played=True
        image(self.main_img, self.x, self.y)

class excalibur(power_up):
    def __init__(self, platform):
        power_up.__init__(self, platform)
        self.w = 70
        self.h = 90
        print("Excalibur at", self.x, self.y)
        self.img1 = loadImage(os.getcwd() + "/images/Rooted_excalibur.PNG")
        self.img1.resize(self.w,self.h)
        self.img2 = loadImage(os.getcwd() + "/images/unrooted_excalibur.PNG")
        self.img2.resize(self.w,self.h + 20)
        self.Nin_img1 = loadImage(os.getcwd() + "/images/Ninja_sprites/Ninja_excalibur.PNG")
        self.Nin_img2 = loadImage(os.getcwd() + "/images/Ninja_sprites/Ninja_excalibur2.PNG")
        self.main_img = self.img1
        self.type = "Excalibur"
        self.cnt = 0
        self.sound=SoundFile(this, os.getcwd() + "/sounds/Win.mp3")
        self.sound.amp(1.0)
        self.sound_played=False
        
    def display(self):
        if self.activated:
            if self.cnt < 5:
                self.main_img = self.img2
                image(self.main_img, self.x, self.y - 20)
                self.cnt += 1 
            elif self.cnt == 5:
                if self.activated and not self.sound_played:
                    self.sound.play()
                    self.sound_played=True
                Window.Game.ninja.w = (self.w + 8)*1.3
                Window.Game.ninja.h = (self.h + 5)*1.3
                
                self.cnt += 1 
            elif self.cnt < 10:
                Window.Game.ninja.excalibur = self.Nin_img2
                self.cnt += 1 
            else:
                Window.Game.ninja.excalibur = self.Nin_img2
        else:
            self.main_img = self.img1
            self.activated = False
            if self.update():
                self.h = 60
                cnt = 1
            image(self.main_img, self.x, self.y)

class Obstacle:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

    def check_collision(self, ninja):
        # Check collision with the ninja
        distance = ((self.x-ninja.x)**2 + (self.y-ninja.y)**2)**0.5
        return distance < (self.size + min(ninja.w, ninja.h)) / 2
    
    
class BlackHole(Obstacle):
    def __init__(self, x, y, size):
        Obstacle.__init__(self, x, y, size)
        self.type = "BlackHole"
        #self.r = size
        self.w=size
        self.h= size
        self.disappear_timer = 60
        self.img=loadImage(os.getcwd()+"/images/Obstacles/BlackHole.PNG")
        self.sound=SoundFile(this, os.getcwd() + '/sounds/BlackHole.mp3')
        self.sound.amp(1.0)
        self.sound_played=False

    def apply_effect(self, ninja):
        if not self.sound_played:
                self.sound.play()

        Window.Game.over = True
        ninja.vy = 0  # Stop moving downwards
        for i in range(0,max(ninja.w,ninja.h),2):
            ninja.w = max(ninja.w - 2, 0) 
            ninja.h = max(ninja.h - 2, 0)     
            if ninja.w==0 or ninja.h==0:
                ninja.y=Window.Game.h+100
                break
                
    def update(self):
        if self.check_collision(Window.Game.ninja):
            # Updating the disappear timer
            self.disappear_timer -= 1

            if self.disappear_timer == 0:
                # Resetting the black hole position and timer when it disappears
                self.reset_position()

    def display(self):
        image(self.img, self.x, self.y, self.w, self.h)
        

    def reset_position(self):
        self.x, self.y = self.get_random_position()
        self.disappear_timer = 60  # Resetting the timer
        
    def get_random_position(self):
        x, y = 0, 0  
        valid_position = None
    
        while not valid_position:
            x = random.randint(10, Window.Game.w - 10 - self.w)
            y = random.randint(10, Window.Game.h - 10 - self.h)
            
            for p in Window.Game.platforms:
                if p.check_collision()==True:
                    valid_position = False
                    break
    
            for o in Window.Game.obstacles:
                if o.check_collision(Window.Game.ninja)==True:
                    valid_position = False
                    break
                
            if valid_position!=False:
                valid_position=True
            else:
                valid_position=None

        return x, y

        
class Monster(Obstacle):
    def __init__(self, x, y, size, speed):
        Obstacle.__init__(self,x, y, size)
        self.type='Monster'
        self.speed = speed
        self.direction = 1  # 1 for right, -1 for left
        self.w = size
        self.h = size
        self.img1 = loadImage(os.getcwd() + "/images/Obstacles/Assasin_1.PNG")
        self.img2 = loadImage(os.getcwd() + "/images/Obstacles/Assasin_slash1.PNG")
        self.current_img = self.img1
        self.killsound=SoundFile(this, os.getcwd() + '/sounds/MonsterKill.mp3')
        self.killsound.amp(1.0)
        self.killsound_played=False

    def move(self):
        self.x += self.speed * self.direction

        # Reversing direction when the monster reaches the screen edges
        if self.x <= 0 or self.x >= Window.Game.w - self.size:
            self.direction *= -1

    def apply_effect(self, ninja):
        if self.check_collision(ninja):
            self.current_img = self.img2
            if not self.killsound_played:
                    self.killsound.play()
                    self.killsound_played=True  
            ninja.vy = min(ninja.vy + 5, ninja.terminal_vel)
    
            ninja.y += ninja.vy

            Window.Game.g_o_h = min(Window.Game.g_o_h + ninja.vy, Window.Game.h / 2 - 100)
            # Move the platforms up
            for p in Window.Game.platforms:
                p.y -= ninja.vy
            Window.Game.over = True

    def display(self):
        if self.direction > 0:
            image(self.current_img, self.x - self.w / 2, self.y - self.h / 2, self.w, self.h)
        elif self.direction < 0:
            image(self.current_img, self.x + self.w / 2, self.y - self.h / 2, -self.w, self.h)
       
    def update(self):
        self.move()
        self.display()
        

Window = main_app(resolution[0], resolution[1])
FPS = 30
H_speed = 20
def setup():
    global FPS
    size(resolution[0], resolution[1])
    smooth()
    frameRate(FPS)

def draw():
    if Window.pause==False:
        global FPS, H_speed
        frameRate(FPS)
        background(255)
        Window.Game.update()
        Window.display()
        
    
def keyPressed():
    global H_speed
    # Up and Down are cheatcodes
    # if keyCode == UP:
    #     Window.Game.ninja.vy = -80
    #if keyCode == DOWN:
     #   Window.Game.ninja.vy = 20
    if keyCode == LEFT:
        Window.Game.ninja.vx = -H_speed
    if keyCode == RIGHT:
        Window.Game.ninja.vx = H_speed
        
def keyReleased(): 
    if keyCode == LEFT or keyCode == RIGHT:
        Window.Game.ninja.vx = 0
        
def mouseClicked():
    global Game, highscore, FPS, H_speed
    Window.start = True
    
    if Window.Game.over:
        highscore = Window.Game.highscore
        Window.Game = game(resolution[0], resolution[1])
    
    #pauses game
    elif Window.pause == False:
        Window.pause = True
        Window.bgMu
        sic.pause()
    #resumes game
    elif Window.pause == True:
        Window.pause = False
        Window.bgMusic.play()
        

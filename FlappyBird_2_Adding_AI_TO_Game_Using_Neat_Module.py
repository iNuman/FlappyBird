#!/usr/bin/env python
# coding: utf-8

# ## Flappy Bird Using Neural Networks

# In[1]:


# %run Sudoku_Game_CLI.ipynb import valid, solve
import pygame
import neat
import time
import os
import random
pygame.font.init()

gen = 0


# In[2]:


WIN_WIDTH = 300
WIN_HEIGHT = 500

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")


# ### Getting Images

# In[3]:


# BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
# PIPE_IMGS = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
# BASE_IMGS = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
# BG_IMGS = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

PIPE_IMGS = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha())
BG_IMGS = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (300, 550))
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
BASE_IMGS = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha())


# ## Fonts for Score

# In[4]:


STAT_FONT = pygame.font.SysFont("comicsans", 30)


# ###  Creating Bird Class

# In[5]:


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25 #'''Tilting upward and downward the birds face'''
    ROT_VEL = 20       #''' Velocity of rotation'''
    ANIMATION_TIME = 5 
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0 #''' initially the bird will be in straight no tilting'''
        self.tick_count = 0
        self.vel = 0 #''' initially the bird is not moving'''
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0] #''' IMGS REFER BIRD IMAGES'''
        
    
    def jump(self):
        self.vel = -10.5 
        ''' When then birds goes up the velocity will be -ve and moving down will be +ve 
        moving right will be +ve and moving left will be -ve'''
        self.tick_count = 0 
        ''' this is gona keep track of when we last  jump'''
        self.height = self.y
        
        
    def move(self):
        self.tick_count += 1 
        ''' this will keep the track how many times we moved since the last jump
        
         We'll doing something with displacement means how many pixels we're moving up and down this frame'''
        d = self.vel*self.tick_count + 1.5*self.tick_count**2
        ''' Formula: -10.5*1 = -10.5, 1.5*1 power 2 = 1.5=====> -10.5 + 1.5 = -9 so the bird will move -9pixels upward'''
        
        if d >= 16: 
            ''' if the bird is moving down let it set to be 16pixels so that
            we'll move down to fast we reach point where we don't accelerate anymore'''
            d = 16
            
        if d < 0:#''' if the bird is moving up let the bird moing up a bit more'''
            d -= 2
            
        self.y = self.y + d #''' we added the calculated d to y to move slowly up or slowly down'''
        
        ''' Now we'll work with tilting up and tilting down and we'll do this inside move becaue we'll figure out
        whether we're tilting up or down base onthe bird moves up or down'''
        
        if d < 0 or self.y < self.height + 50:
            '''if we are going upward even if we are coming downward till that mid point oujr birds face 
            should be slight up
           
           if we're going downward bird face shoul be completely 90 degrees downwards likes nose diving to the ground
        with faster and faster velocity we're not using max rotation here becaue we want completely down when moving down
        and we used max rotation above because we don't want to completely rotate up but slight upward of bird face'''
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL 
                
                
    def draw(self, win): #'''win means window where our image will be shown'''
        self.img_count += 1
        
        #''' If the image count is less then animation time we'll set the first image'''
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1] #'''WE'LL show the second image'''
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
            ''' this way we set the wings flapping up and down
            
             last thing is when the bird going down the images should not change instead it should just dive with 
            leveling it's wings'''
        if self.tilt <= -80:
            self.img = self.IMGS[1]
           # '''and during going downward when bird again moving upward it should again change images'''
            self.img_count = self.ANIMATION_TIME * 2
            
        #''' Now to rotate the image in center of pygame window'''
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        #''' we'll define the top left of our image self.x and self.y'''
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)
            
    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    
    
class Pipe():
    """
    represents a pipe object
    """
    GAP = 150 # gap between pipes
    VEL = 5

    def __init__(self, x):
        """
        initialize pipe object
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(PIPE_IMGS, False, True)
        self.PIPE_BOTTOM = PIPE_IMGS

        self.passed = False

        self.set_height()

    def set_height(self):
        """
        set the height of the pipe, from the top of the screen
        :return: None
        """
        self.height = random.randrange(50, 450) # pipes height will be in between these random
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
        move pipe based on vel
        :return: None
        """
        self.x -= self.VEL

    def draw(self, win):
        """
        draw both the top and bottom of the pipe
        :param win: pygame window/surface
        :return: None
        """
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird):
        """
        returns if a point is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False
        
       
        
        
class Base:
    VEL = 5
    WIDTH = BASE_IMGS.get_width()
    IMGS = BASE_IMGS
    
    def __init__(self, y):
        self.y = y
        self.x1 = 0 # one image with o and 2nd behind the first one 
        self.x2 = self.WIDTH
        
    def move(self):
        # we're moving them with the same velocity
        self.x1 -= self.VEL # base image will be move to left
        self.x2 -= self.VEL # 2nd image will be move to the left with the same speed as of base image 1
     
        # here concept is when one image is completely move off of the screen then it'll recycled to the end time 6:27:22 
        # below if statement is doing this work and this ways the base looks it's moving continously
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
            
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
            
    def draw(self, win):
        win.blit(self.IMGS, (self.x1, self.y))
        win.blit(self.IMGS, (self.x2, self.y))
    
        
        
def draw_win(win, birds, pipes, base, score, gen):
    win.blit(BG_IMGS, (0, 0)) # blit means draw we're drawing BG IMAGE AND 0, 0 OR TOP LEFT CORNER
    
    for pipe in pipes:
        pipe.draw(win)
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10)) #no matter how much big the score is it'll be always show up screen
   
    text = STAT_FONT.render("Gen: " + str(gen), 1, (255,255,255))
    win.blit(text, (10, 10))
   
    base.draw(win)
    
    for bird in birds:
        bird.draw(win)
        
    pygame.display.update()
    
    

def main(genomes, config):
    global gen
    gen += 1
    nets = []
    ge = []
    birds = []
    # Now i need to keep track of neural network that controls each bird
    # because the genomes that are coming are reallly a bunch of neural networks
    # that gona control each of our birds so, I need to keep track of bird that neural network is controlling
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config) # setted Neural network for our genome
        nets.append(net) # append it to the list 
        birds.append(Bird(20, 200)) # append bird object to the list
        g.fitness = 0 # setted initial fitness to zero
        ge.append(g)
    
    base = Base(530) # height of 530 because it'll be at the bottom of the screen
    pipes = [Pipe(500)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score  = 0 
    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()


        pipe_ind = 0 # pipe index
        if len(birds) > 0:
            # it means if we pass through the pipe then change the to 2nd index we're looking at
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else: # if there's no bird left we're gona quit the game
            run = False
            break
            
                
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness = 0.1
            
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            
            if output[0] > 0.5: # because output is a list in our cas there's only one output
                bird.jump()
                
                 
        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird): # we checked if every pipe collide with every bird
                    # if the bird collide i don't want to keep it anymore i wana remove it 
                    ge[x].fitness -= 1
                    birds.pop(x) # remove the bird
                    nets.pop(x) # remove the neural network associated with it
                    ge.pop(x) # remove the genome also
                    
                if not pipe.passed and pipe.x < bird.x: # we also checked if the bird has passed by pipe
                    pipe.passed = True
                    add_pipe = True
                    
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
                
            pipe.move()
            
        if add_pipe: # add a pipe
            score += 1
            for g in ge:
                g.fitness += 5  # if the birds pass through the pipe i will give them a fair fitness score
            pipes.append(Pipe(WIN_WIDTH))
        # to remove the pipes  of window
        for r in rem:
            pipes.remove(r)
            
            # same as bird collide with pipe if the bird hit the ground i will remove that bird and network associated with it
        for x, bird in enumerate(birds):
             if bird.y + bird.img.get_height() >= 530 or bird.y < 0:
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
            
        base.move()
        draw_win(win, birds, pipes, base, score, gen)


# ## Loading Configuration File

# In[ ]:


def run(config_path):
    # loaded configuration file
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)
    
    
    # Now to generate a population / setted a population
    p = neat.Population(config)
    
    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)


    winner = p.run(main,50) # here 50 are generations and main will be our fitness function because it determine how far 
    # our bird will go
    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)


"""
The classic game of flappy bird. Make with python
and pygame. Features pixel perfect collision using masks
"""

import os
import random
import time

import neat
import pygame

pygame.font.init() # init font

WIN_WIDTH = 500
WIN_HEIGHT = 800

# Generations
GEN = 0

# Getting the images of the birds in a list, with their size doubled
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

# Getting the image of the pipe
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))

# Getting the image of the base
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))

# Getting the image of the background
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)


class Bird:
    """
    Bird class representing the flappy bird
    """
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25  #How much the bird is gonna tilt
    ROTATION_VELOCITY = 20
    ANIMATION_TIME = 5


    def __init__(self, x, y):
        # X -> starting x position
        # Y -> starting y position
        self.x = x
        self.y = y
        self.tilt = 0 # degrees to tilt
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0] #Bird1.png


    def jump(self):
        """
        Make the bird jump
        """
        self.velocity = -10.5
        self.tick_count = 0 #When we last jumped
        self.height = self.y


    def move(self):
        """
        Make the bird move
        """
        self.tick_count += 1

        # Calculating the displacement
        # Tells how much we're moving up or down
        d = self.velocity * self.tick_count + 1.5 * self.tick_count**2

        if d >= 16:
            d = 16

        if d < 0:
            d -= 2

        # Changing the replacement
        self.y = self.y + d

        # Making the bird tilt
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else: # tilt down
            if self.tilt > -90:
                self.tilt -= self.ROTATION_VELOCITY


    def draw(self, win):
        """
        Draw the bird
        """
        self.img_count += 1

        # Check what image we should show based on the current image count
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0] #First bird
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1] #Second bird
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2] #Last bird
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0 #Reset the counter

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        # Rotate the image
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    
    def get_mask(self):
        """
        Gets the mask for the current image of the bird
        """
        return pygame.mask.from_surface(self.img)


class Pipe:
    """
    Represents a pipe object
    """
    GAP = 200
    VELOCITY = 5


    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        # If the bird passed the pipe
        self.passed = False
        self.set_height()


    def set_height(self):
        """
        Set the height of the pipe, from the top of the screen
        """
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP


    def move(self):
        """
        Move the pipe based on velocity
        """
        self.x -= self.VELOCITY
    

    def draw(self, win):
        """
        Draw both the top and bottom of the pipe
        :param win: pygame window/surface
        """
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird):
        """
        Returns if a point is colliding with the pipe
        """
        bird_mask = bird.get_mask()
        top_mask =  pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask =  pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True #We're colliding
        
        return False


class Base:
    """
    Represents the moving floor of the game
    """
    VELOCITY = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG


    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH


    def move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH


    def draw(self, win):
        """
        Draw the floor. This is two images that move together.
        :param win: the pygame surface/window
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score, gen):
    """
    Draws the windows for the main game loop
    :param win: pygame window surface
    :param bird: a Bird object
    :param pipes: List of pipes
    :param score: score of the game (int)
    :param gen: current generation
    :param pipe_ind: index of closest pipe
    """
    win.blit(BG_IMG, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    # 'Score' text
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    # 'Generations' Text
    text = STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
    win.blit(text, (10,10))

    base.draw(win)

    for bird in birds:
        bird.draw(win)
        
    pygame.display.update()


# Fitness Function
def eval_genomes(genomes, config):
    """
    Runs the simulation of the current population of
    birds and sets their fitness based on the distance they
    reach in the game.
    """
    global GEN
    GEN += 1

    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # bird object that uses that network to play
    
    nets = []
    ge = []
    birds = []

    # Set up a neural network for the genes
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        
        # Input to neural network
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1  

            # Output of the neural network
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()

        # Pipes generation
        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                # if the birds collided
                if pipe.collide(bird):
                    # remove 1 from his fitness score
                    ge[x].fitness -= 1
                    # get rid of him
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                # Check if the bird passed the pipe
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            # If the pipe is off the screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()
        
        if add_pipe:
            score += 1
            # Increase the fitness of the bird who gets through the pipe
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            # If the bird hit the floor or moved up too far
            if bird.y + bird.img.get_height() > 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        # Base moving
        base.move()

        draw_window(win, birds, pipes, base, score, GEN) 


def run(config_path):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    """
    # Load the configuration
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Population
    population = neat.Population(config)

    # Set the output
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Run for up to 50 generations
    winner = population.run(eval_genomes,50)

if __name__ == "__main__":
    # Determine path to configuration file
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedfoward.txt")
    run(config_path)
    

""" NEAT AI
Take the best bird from 1 generation, clone him and repeat.
INPUTS -> y position of the bird, top pipe, bottom pipe
OUTPUTS -> jump or don't jump
ACTIVATION FUNCTION -> TanH
POPULATION SIZE -> 100 birds
FITNESS FUNCTION -> distance the bird walks
MAX GENERATIONS -> 30
"""











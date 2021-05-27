import os
import sys

import pygame
from random import randrange
import neat
from pygame import mixer
from time import sleep

AI_Playing = True
gen = 0

mixer.init()
mixer.music.load('pass_pipe.wav')

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 600

BIRD = [pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
        pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
        pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
        ]

PIPE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))

BASE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))

BACKGROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))

pygame.font.init()
SCORE_FONT = pygame.font.SysFont('arial', 50)


class Bird:
    IMGS = BIRD
    max_rotation = 25
    vel_rotation = 20
    time_animation = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ang = 0
        self.vel = 0
        self.height = self.y
        self.time = 0
        self.cont_image = 0
        self.image = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.time = 0
        self.height = self.y

    def move(self):
        self.time += 1
        d = 1.5 * (self.time ** 2) + self.vel * self.time

        if d > 16:
            d = 16
        elif d < 0:
            d -= 2

        self.y += d

        if d < 0 or self.y < (self.height + 50):
            if self.ang < self.max_rotation:
                self.ang = self.max_rotation
        else:
            if self.ang > -90:
                self.ang -= self.vel_rotation

    def draw(self, window):
        self.cont_image += 1

        if self.cont_image < self.time:
            self.image = self.IMGS[0]
        elif self.cont_image < self.time * 2:
            self.image = self.IMGS[1]
        elif self.cont_image < self.time * 3:
            self.image = self.IMGS[2]
        elif self.cont_image < self.time * 4:
            self.image = self.IMGS[1]
        elif self.cont_image >= self.time * 4 + 1:
            self.image = self.IMGS[0]
            self.cont_image = 0

        if self.ang <= -80:
            self.image = self.IMGS[1]
            self.cont_image = self.time * 2

        rotation_image = pygame.transform.rotate(self.image, self.ang)
        center = self.image.get_rect(topleft=(self.x, self.y)).center
        rectangle = rotation_image.get_rect(center=center)
        window.blit(rotation_image, rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe:
    DISTANCE = 200
    VELOCITY = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.pos_top = 0
        self.pos_base = 0
        self.TOP_PIPE = pygame.transform.flip(PIPE, False, True)
        self.BASE_PIPE = PIPE
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = randrange(50, 450)
        self.pos_top = self.height - self.TOP_PIPE.get_height()
        self.pos_base = self.height + self.DISTANCE

    def move(self):
        self.x -= self.VELOCITY

    def draw(self, window):
        window.blit(self.TOP_PIPE, (self.x, self.pos_top))
        window.blit(self.BASE_PIPE, (self.x, self.pos_base))

    def colide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.TOP_PIPE)
        base_mask = pygame.mask.from_surface(self.BASE_PIPE)

        top_distance = (self.x - bird.x, self.pos_top - round(bird.y))
        base_distance = (self.x - bird.x, self.pos_base - round(bird.y))

        top_point = bird_mask.overlap(top_mask, top_distance)
        base_point = bird_mask.overlap(base_mask, base_distance)

        if base_point or top_point:
            return True
        else:
            return False


class Base:
    VELOCITY = 5
    WIDTH = BASE.get_width()
    IMAGE = BASE

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
        win.blit(self.IMAGE, (self.x1, self.y))
        win.blit(self.IMAGE, (self.x2, self.y))


def draw_window(window, birds, pipes, base, score):
    window.blit(BACKGROUND_IMAGE, (0, 0))
    for bird in birds:
        bird.draw(window)

    for pipe in pipes:
        pipe.draw(window)

    text = SCORE_FONT.render(f'Score: {score}', True, (255, 255, 255))
    window.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 10))

    if AI_Playing:
        text = SCORE_FONT.render(f'Gen: {gen}', True, (255, 255, 255))
        window.blit(text, (10, 10))

    base.draw(window)
    pygame.display.update()


def main(genomes, config):
    global gen
    gen += 1

    if AI_Playing:
        neural_networks = []
        list_genomes = []
        birds = []
        for _, genome in genomes:
            network = neat.nn.FeedForwardNetwork.create(genome, config)
            neural_networks.append(network)
            genome.fitness = 0
            list_genomes.append(genome)
            birds.append(Bird(230, 350))
    else:
        birds = [Bird(230, 350)]

    floor = Base(730)
    pipes = [Pipe(700)]
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    score = 0
    clock = pygame.time.Clock()
    loop = True
    while loop:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop = False
                pygame.quit()

            if not AI_Playing:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        for bird in birds:
                            bird.jump()
        index_pipe = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > (pipes[0].x + pipes[0].TOP_PIPE.get_width()):
                index_pipe = 1

        else:
            if not AI_Playing:
                mixer.init()
                mixer.music.load('fail.wav')
                mixer.music.play(fade_ms=3000)
                sleep(3)
            loop = False
            break
        for i, bird in enumerate(birds):
            bird.move()
            if AI_Playing:
                list_genomes[i].fitness += 0.1
                output = neural_networks[i].activate((bird.y,
                                                      abs(bird.y - pipes[index_pipe].height),
                                                      abs(bird.y - pipes[index_pipe].pos_base)))

                if output[0] > 0.5:
                    bird.jump()

        floor.move()

        add_pipe = False
        remove_pipes = []

        for pipe in pipes:
            for number, bird in enumerate(birds):
                if pipe.colide(bird):
                    birds.pop(number)
                    if AI_Playing:
                        list_genomes[number].fitness -= 1
                        list_genomes.pop(number)
                        neural_networks.pop(number)

                if not pipe.passed and bird.x > pipe.x:
                    pipe.passed = True
                    add_pipe = True
            pipe.move()
            if pipe.x + pipe.TOP_PIPE.get_width() < 0:
                remove_pipes.append(pipe)

        if add_pipe:
            score += 1
            mixer.music.play(fade_ms=1000)
            pipes.append(Pipe(600))
            if AI_Playing:
                for genome in list_genomes:
                    genome.fitness += 100
        for pipe in remove_pipes:
            pipes.remove(pipe)

        for number, bird in enumerate(birds):
            if (bird.y + bird.image.get_height()) > floor.y or bird.y < 0:
                birds.pop(number)
                if AI_Playing:
                    list_genomes.pop(number)
                    neural_networks.pop(number)

        draw_window(window, birds, pipes, floor, score)


def run(path):
    if AI_Playing:
        config = neat.config.Config(neat.DefaultGenome,
                                    neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet,
                                    neat.DefaultStagnation,
                                    path)

        population = neat.Population(config)
        population.add_reporter(neat.StdOutReporter(True))
        population.add_reporter(neat.StatisticsReporter())

        population.run(main)
    else:
        main(None, None)


if __name__ == '__main__':
    esc = int(input('Set a game mode: '
                    '\n1-A.I'
                    '\n2-Single Player'))
    options = [x+1 for x in range(2)]
    while esc not in options:
        esc = int(input('Please try again'))
    if esc == options[0]:
        AI_Playing = True
    if esc == options[1]:
        AI_Playing = False

    print('Loading', end='')
    for c in range(3):
        print('.', end='')
        sleep(0.6)
    print('Game Started!')
    sleep(0.3)
    path = os.path.join(os.path.dirname(__file__), 'config.txt')
    run(path)

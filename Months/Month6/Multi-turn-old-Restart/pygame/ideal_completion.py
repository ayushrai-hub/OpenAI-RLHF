import pygame
import random
import math

# Constants
WIDTH, HEIGHT = 800, 600
NUM_PARTICLES = 50
PARTICLE_RADIUS = 10
PARTICLE_MASS = 1
MASS = PARTICLE_MASS
VELOCITY_SCALE = 5
BACKGROUND_COLOR = (0, 0, 0)
PARTICLE_COLOR = (255, 255, 255)
FPS = 60

class Particle:
    def __init__(self, x, y, vx, vy, radius, mass):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.mass = mass

    def move(self):
        self.x += self.vx
        self.y += self.vy

    def wall_collision(self, width=WIDTH, height=HEIGHT):
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = abs(self.vx)
        elif self.x + self.radius > width:
            self.x = width - self.radius
            self.vx = -abs(self.vx)

        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy = abs(self.vy)
        elif self.y + self.radius > height:
            self.y = height - self.radius
            self.vy = -abs(self.vy)

    def draw(self, screen):
        pygame.draw.circle(screen, PARTICLE_COLOR, (int(self.x), int(self.y)), self.radius)

def handle_collisions(particles):
    for i in range(len(particles)):
        for j in range(i + 1, len(particles)):
            p1 = particles[i]
            p2 = particles[j]
            dx = p1.x - p2.x
            dy = p1.y - p2.y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance < p1.radius + p2.radius:  # Collision detected
                nx, ny = dx / distance, dy / distance
                p1_vn = p1.vx * nx + p1.vy * ny
                p2_vn = p2.vx * nx + p2.vy * ny
                p1_vt = p1.vx * -ny + p1.vy * nx
                p2_vt = p2.vx * -ny + p2.vy * nx

                p1_vn, p2_vn = p2_vn, p1_vn

                p1.vx = p1_vn * nx - p1_vt * ny
                p1.vy = p1_vn * ny + p1_vt * nx
                p2.vx = p2_vn * nx - p2_vt * ny
                p2.vy = p2_vn * ny + p2_vt * nx

                overlap = 0.5 * (p1.radius + p2.radius - distance + 1)
                p1.x += overlap * nx
                p1.y += overlap * ny
                p2.x -= overlap * nx
                p2.y -= overlap * ny

def create_particles(num_particles, width, height, radius, mass, velocity_scale):
    particles = []
    while len(particles) < num_particles:
        x = random.uniform(radius, width - radius)
        y = random.uniform(radius, height - radius)
        vx = random.uniform(-velocity_scale, velocity_scale)
        vy = random.uniform(-velocity_scale, velocity_scale)

        if all(math.sqrt((x - p.x) ** 2 + (y - p.y) ** 2) >= 2 * radius for p in particles):
            particles.append(Particle(x, y, vx, vy, radius, mass))
    return particles

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2D Ideal Gas Simulation")
    clock = pygame.time.Clock()

    particles = create_particles(NUM_PARTICLES, WIDTH, HEIGHT, PARTICLE_RADIUS, MASS, VELOCITY_SCALE)
    running = True

    while running:
        screen.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for particle in particles:
            particle.move()
            particle.wall_collision(WIDTH, HEIGHT)
        handle_collisions(particles)

        for particle in particles:
            particle.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()

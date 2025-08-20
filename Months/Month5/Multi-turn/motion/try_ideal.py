import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Ideal Gas Simulation")

# Simulation parameters
NUM_PARTICLES = 100
TEMPERATURE = 300
PARTICLE_RADIUS = 5
MASS = 1
BOLTZMANN_CONSTANT = 1
VELOCITY_SCALE = 0.05

# Compute the average speed from temperature
average_speed = math.sqrt(2 * BOLTZMANN_CONSTANT * TEMPERATURE / MASS)

# Particle class
class Particle:
    def __init__(self, x, y, vx, vy, radius, mass):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.mass = mass
        self.color = (0, 0, 255)

    def move(self):
        self.x += self.vx
        self.y += self.vy

    def wall_collision(self):
        # Collision with left or right wall
        if self.x - self.radius <= 0:
            self.vx *= -1
            self.x = self.radius
        elif self.x + self.radius >= WIDTH:
            self.vx *= -1
            self.x = WIDTH - self.radius
        # Collision with top or bottom wall
        if self.y - self.radius <= 0:
            self.vy *= -1
            self.y = self.radius
        elif self.y + self.radius >= HEIGHT:
            self.vy *= -1
            self.y = HEIGHT - self.radius

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# Collision handling function
def handle_collisions(particles):
    for i in range(len(particles)):
        p1 = particles[i]
        for j in range(i + 1, len(particles)):
            p2 = particles[j]
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            distance = math.hypot(dx, dy)
            min_distance = p1.radius + p2.radius
            if distance < min_distance:
                # Overlap amount
                overlap = 0.5 * (min_distance - distance)
                # Adjust positions
                p1.x -= overlap * (dx) / distance
                p1.y -= overlap * (dy) / distance
                p2.x += overlap * (dx) / distance
                p2.y += overlap * (dy) / distance

                # Elastic collision dynamics
                nx = dx / distance
                ny = dy / distance
                tx = -ny
                ty = nx

                # Tangential velocities
                dpTan1 = p1.vx * tx + p1.vy * ty
                dpTan2 = p2.vx * tx + p2.vy * ty

                # Normal velocities
                dpNorm1 = p1.vx * nx + p1.vy * ny
                dpNorm2 = p2.vx * nx + p2.vy * ny

                # Calculate new velocities
                m1 = (dpNorm1 * (p1.mass - p2.mass) + 2 * p2.mass * dpNorm2) / (p1.mass + p2.mass)
                m2 = (dpNorm2 * (p2.mass - p1.mass) + 2 * p1.mass * dpNorm1) / (p1.mass + p2.mass)

                p1.vx = tx * dpTan1 + nx * m1
                p1.vy = ty * dpTan1 + ny * m1
                p2.vx = tx * dpTan2 + nx * m2
                p2.vy = ty * dpTan2 + ny * m2

# Particle initialization ensuring no overlaps
def create_particles():
    particles = []
    for _ in range(NUM_PARTICLES):
        while True:
            x = random.uniform(PARTICLE_RADIUS, WIDTH - PARTICLE_RADIUS)
            y = random.uniform(PARTICLE_RADIUS, HEIGHT - PARTICLE_RADIUS)
            if not any(math.hypot(p.x - x, p.y - y) < p.radius + PARTICLE_RADIUS for p in particles):
                break
        angle = random.uniform(0, 2 * math.pi)
        speed = random.gauss(average_speed, average_speed * 0.1) * VELOCITY_SCALE
        vx = speed * math.cos(angle)
        vy = speed * math.sin(angle)
        particles.append(Particle(x, y, vx, vy, PARTICLE_RADIUS, MASS))
    return particles

def main():
    clock = pygame.time.Clock()
    particles = create_particles()
    running = True

    while running:
        screen.fill((0, 0, 0))  # Clear screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update particles
        for particle in particles:
            particle.move()
            particle.wall_collision()

        # Handle collisions
        handle_collisions(particles)

        # Draw particles
        for particle in particles:
            particle.draw(screen)

        pygame.display.flip()  # Update the display
        clock.tick(60)  # Limit to 60 frames per second

    pygame.quit()

if __name__ == "__main__":
    main()

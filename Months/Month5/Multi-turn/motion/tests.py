import unittest
from unittest.mock import patch
import random
import math
import pygame

import os

# Set this env var to "dummy", setting pygame for a headless test
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Import the necessary elements from the simulation code
from try_ideal import Particle, handle_collisions, WIDTH, HEIGHT, PARTICLE_RADIUS, MASS, main

class TestIdealGasSimulation(unittest.TestCase):

    def setUp(self):
        # Set up initial test particles for boundary and collision tests
        self.particle1 = Particle(x=100, y=100, vx=5, vy=0, radius=PARTICLE_RADIUS, mass=MASS)
        self.particle2 = Particle(x=150, y=100, vx=-5, vy=0, radius=PARTICLE_RADIUS, mass=MASS)

    def test_particle_initialization_no_overlap(self):
        particles = []
        for _ in range(100):
            while True:
                x = random.uniform(PARTICLE_RADIUS, WIDTH - PARTICLE_RADIUS)
                y = random.uniform(PARTICLE_RADIUS, HEIGHT - PARTICLE_RADIUS)
                if not any(math.hypot(p.x - x, p.y - y) < p.radius + PARTICLE_RADIUS for p in particles):
                    break
            particle = Particle(x, y, 0, 0, PARTICLE_RADIUS, MASS)
            particles.append(particle)

        for i, p1 in enumerate(particles):
            for j, p2 in enumerate(particles):
                if i != j:
                    self.assertGreaterEqual(
                        math.hypot(p1.x - p2.x, p1.y - p2.y),
                        p1.radius + p2.radius,
                        "Particles overlap during initialization."
                    )

    def test_wall_collision(self):
        self.particle1.x = PARTICLE_RADIUS
        self.particle1.vx = -5
        self.particle1.wall_collision()
        self.assertEqual(self.particle1.vx, 5, "Wall collision not reversing velocity correctly.")

        self.particle1.x = WIDTH - PARTICLE_RADIUS
        self.particle1.vx = 5
        self.particle1.wall_collision()
        self.assertEqual(self.particle1.vx, -5, "Wall collision not reversing velocity correctly.")

    def test_handle_collisions(self):
        self.particle1.x = 100
        self.particle1.y = 100
        self.particle2.x = 100 + 1.9 * PARTICLE_RADIUS
        self.particle2.y = 100

        self.particle1.vx = 5
        self.particle1.vy = 0
        self.particle2.vx = -5
        self.particle2.vy = 0

        initial_vx1 = self.particle1.vx
        initial_vx2 = self.particle2.vx

        particles = [self.particle1, self.particle2]
        handle_collisions(particles)

        self.assertNotEqual(particles[0].vx, initial_vx1, "Velocity of particle 1 did not change post-collision.")
        self.assertNotEqual(particles[1].vx, initial_vx2, "Velocity of particle 2 did not change post-collision.")

        total_momentum_initial = initial_vx1 * self.particle1.mass + initial_vx2 * self.particle2.mass
        total_momentum_final = particles[0].vx * particles[0].mass + particles[1].vx * particles[1].mass
        self.assertAlmostEqual(total_momentum_initial, total_momentum_final, places=2, msg="Momentum not conserved.")

        initial_kinetic_energy = 0.5 * self.particle1.mass * initial_vx1**2 + 0.5 * self.particle2.mass * initial_vx2**2
        final_kinetic_energy = 0.5 * particles[0].mass * particles[0].vx**2 + 0.5 * particles[1].mass * particles[1].vx**2
        self.assertAlmostEqual(initial_kinetic_energy, final_kinetic_energy, places=2, msg="Kinetic energy not conserved.")

    @patch('pygame.event.get', return_value=[pygame.event.Event(pygame.QUIT)])
    @patch('pygame.display.flip')
    def test_main_loop_runs_once(self, mock_display_flip, mock_pygame_event_get):
        """
        Test the main loop in ideal_completion to ensure it can run once and exit without hanging.
        """
        # Run the main function, which should immediately exit after one loop iteration due to the QUIT event
        main()

        # Check that pygame.display.flip() was called once during the single frame
        mock_display_flip.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)
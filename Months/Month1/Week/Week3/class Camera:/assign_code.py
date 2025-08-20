import pygame
from pygame.math import Vector3
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import noise

class Camera:
    def __init__(self):
        self.position = Vector3(0, 0, 0)
        self.yaw = 0
        self.pitch = 0

    def move(self, dx, dy, dz):
        forward = Vector3(math.sin(math.radians(self.yaw)), 0, math.cos(math.radians(self.yaw)))
        right = Vector3(forward.z, 0, -forward.x)
        self.position += forward * -dz + right * dx + Vector3(0, 1, 0) * dy

    def rotate(self, dyaw, dpitch):
        self.yaw += dyaw
        self.pitch += dpitch
        self.pitch = max(-89, min(89, self.pitch))

    def apply(self):
        glRotatef(-self.pitch, 1, 0, 0)
        glRotatef(-self.yaw, 0, 1, 0)
        glTranslatef(-self.position.x, -self.position.y, -self.position.z)

class Chunk:
    def __init__(self, position):
        self.position = position
        self.size = 16
        self.voxels = np.zeros((16, 16, 16), dtype=bool)

    def set_voxel(self, position, value):
        x, y, z = position
        if 0 <= x < self.size and 0 <= y < self.size and 0 <= z < self.size:
            self.voxels[x, y, z] = value

    def get_voxel(self, position):
        x, y, z = position
        if 0 <= x < self.size and 0 <= y < self.size and 0 <= z < self.size:
            return self.voxels[x, y, z]
        return False

class VoxelWorld:
    def __init__(self):
        self.chunks = {}
        self.render_distance = 2

    def get_chunk(self, chunk_position):
        if chunk_position not in self.chunks:
            self.chunks[chunk_position] = Chunk(chunk_position)
            self.generate_terrain(self.chunks[chunk_position])
        return self.chunks[chunk_position]

    def set_voxel(self, position, value):
        x, y, z = position
        chunk_position = (x // 16, y // 16, z // 16)
        local_position = (x % 16, y % 16, z % 16)
        chunk = self.get_chunk(chunk_position)
        chunk.set_voxel(local_position, value)

    def get_voxel(self, position):
        x, y, z = position
        chunk_position = (x // 16, y // 16, z // 16)
        local_position = (x % 16, y % 16, z % 16)
        chunk = self.get_chunk(chunk_position)
        return chunk.get_voxel(local_position)

    def generate_terrain(self, chunk):
        scale = 0.1
        for x in range(16):
            for z in range(16):
                world_x = x + chunk.position[0] * 16
                world_z = z + chunk.position[2] * 16
                height = int(noise.pnoise2(world_x * scale, world_z * scale, octaves=3) * 8 + 8)
                for y in range(16):
                    world_y = y + chunk.position[1] * 16
                    if world_y < height:
                        chunk.set_voxel((x, y, z), True)

    def render(self):
        glBegin(GL_QUADS)
        for chunk_position, chunk in self.chunks.items():
            cx, cy, cz = chunk_position
            for x in range(16):
                for y in range(16):
                    for z in range(16):
                        if chunk.get_voxel((x, y, z)):
                            wx, wy, wz = cx*16 + x, cy*16 + y, cz*16 + z
                            self.render_cube(wx, wy, wz)
        glEnd()

    def render_cube(self, x, y, z):
        glColor3f(0.5, 0.5, 0.5)
        # Front face
        glVertex3f(x, y, z+1)
        glVertex3f(x+1, y, z+1)
        glVertex3f(x+1, y+1, z+1)
        glVertex3f(x, y+1, z+1)
        # Back face
        glVertex3f(x, y, z)
        glVertex3f(x, y+1, z)
        glVertex3f(x+1, y+1, z)
        glVertex3f(x+1, y, z)
        # Top face
        glVertex3f(x, y+1, z)
        glVertex3f(x, y+1, z+1)
        glVertex3f(x+1, y+1, z+1)
        glVertex3f(x+1, y+1, z)
        # Bottom face
        glVertex3f(x, y, z)
        glVertex3f(x+1, y, z)
        glVertex3f(x+1, y, z+1)
        glVertex3f(x, y, z+1)
        # Right face
        glVertex3f(x+1, y, z)
        glVertex3f(x+1, y+1, z)
        glVertex3f(x+1, y+1, z+1)
        glVertex3f(x+1, y, z+1)
        # Left face
        glVertex3f(x, y, z)
        glVertex3f(x, y, z+1)
        glVertex3f(x, y+1, z+1)
        glVertex3f(x, y+1, z)

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0] / display[1]), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    world = VoxelWorld()
    camera = Camera()
    camera.position = Vector3(8, 16, 8)

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        mouse_dx, mouse_dy = pygame.mouse.get_rel()

        camera.rotate(-mouse_dx * 0.1, -mouse_dy * 0.1)

        movement_speed = 0.1
        if keys[pygame.K_w]:
            camera.move(0, 0, movement_speed)
        if keys[pygame.K_s]:
            camera.move(0, 0, -movement_speed)
        if keys[pygame.K_a]:
            camera.move(-movement_speed, 0, 0)
        if keys[pygame.K_d]:
            camera.move(movement_speed, 0, 0)
        if keys[pygame.K_SPACE]:
            camera.move(0, movement_speed, 0)
        if keys[pygame.K_LSHIFT]:
            camera.move(0, -movement_speed, 0)

        # Update visible chunks
        cx, cy, cz = int(camera.position.x) // 16, int(camera.position.y) // 16, int(camera.position.z) // 16
        for x in range(cx - world.render_distance, cx + world.render_distance + 1):
            for y in range(cy - world.render_distance, cy + world.render_distance + 1):
                for z in range(cz - world.render_distance, cz + world.render_distance + 1):
                    world.get_chunk((x, y, z))

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        camera.apply()
        world.render()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
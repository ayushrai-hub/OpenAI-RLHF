import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import noise
from concurrent.futures import ThreadPoolExecutor

class Camera:
    def __init__(self):
        self.position = np.array([64.0, 40.0, 64.0])
        self.yaw = 0
        self.pitch = 0

    def move(self, dx, dy, dz):
        forward = np.array([math.sin(math.radians(self.yaw)), 0, math.cos(math.radians(self.yaw))])
        right = np.array([forward[2], 0, -forward[0]])
        self.position += forward * -dz + right * dx + np.array([0, 1, 0]) * dy

    def rotate(self, dyaw, dpitch):
        self.yaw += dyaw
        self.pitch = max(-89, min(89, self.pitch + dpitch))

    def apply(self):
        glRotatef(-self.pitch, 1, 0, 0)
        glRotatef(-self.yaw, 0, 1, 0)
        glTranslatef(-self.position[0], -self.position[1], -self.position[2])

class Chunk:
    def __init__(self, position, world):
        self.position = position
        self.world = world
        self.voxels = np.zeros((64, 64, 64, 4), dtype=np.float32)
        self.mesh = None
        self.needs_remesh = True
        self.lod_meshes = {1: None, 2: None, 4: None}
        self.lod_needs_remesh = {1: True, 2: True, 4: True}
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

    def set_voxel(self, position, color):
        x, y, z = position
        self.voxels[x, y, z] = color + (1.0,)
        self.needs_remesh = True
        for lod in self.lod_needs_remesh:
            self.lod_needs_remesh[lod] = True

    def is_voxel_at(self, position):
        x, y, z = position
        return self.voxels[x, y, z, 3] > 0

    def generate_mesh(self, lod):
        vertices = []
        step = int(lod)

        for x in range(0, 64, step):
            for y in range(0, 64, step):
                for z in range(0, 64, step):
                    if self.is_voxel_at((x, y, z)):
                        color = self.voxels[x, y, z][:3]
                        faces = [
                            (x, y, z, -1, 0, 0),
                            (x + step, y, z, 1, 0, 0),
                            (x, y, z, 0, -1, 0),
                            (x, y + step, z, 0, 1, 0),
                            (x, y, z, 0, 0, -1),
                            (x, y, z + step, 0, 0, 1)
                        ]
                        for fx, fy, fz, nx, ny, nz in faces:
                            if not self.world.is_voxel_at_world_coords(fx, fy, fz):
                                vertices.extend([
                                    fx, fy, fz, *color, 1.0, nx, ny, nz,
                                    fx, fy + step, fz, *color, 1.0, nx, ny, nz,
                                    fx, fy + step, fz + step, *color, 1.0, nx, ny, nz,
                                    fx, fy, fz + step, *color, 1.0, nx, ny, nz,
                                ])

        self.lod_meshes[lod] = np.array(vertices, dtype=np.float32)
        self.lod_needs_remesh[lod] = False

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.lod_meshes[lod].nbytes, self.lod_meshes[lod], GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 40, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 40, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 40, ctypes.c_void_p(28))
        glEnableVertexAttribArray(2)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

class VoxelWorld:
    def __init__(self):
        self.chunks = {}
        self.render_distance = 256
        self.chunk_queue = set()
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.loaded_chunks = set()
        self.setup_shaders()
        self.lod_distances = {1: 128, 2: 256, 4: 512}

    def setup_shaders(self):
        vertex_shader = """
        #version 330 core
        layout (location = 0) in vec3 aPos;
        layout (location = 1) in vec4 aColor;
        layout (location = 2) in vec3 aNormal;

        out vec4 vColor;
        out vec3 vNormal;
        out vec3 vFragPos;

        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;

        void main()
        {
            gl_Position = projection * view * model * vec4(aPos, 1.0);
            vColor = aColor;
            vNormal = mat3(transpose(inverse(model))) * aNormal;
            vFragPos = vec3(model * vec4(aPos, 1.0));
        }
        """

        fragment_shader = """
        #version 330 core
        in vec4 vColor;
        in vec3 vNormal;
        in vec3 vFragPos;

        out vec4 FragColor;

        uniform vec3 lightPos;
        uniform vec3 viewPos;

        void main()
        {
            vec3 norm = normalize(vNormal);
            vec3 lightDir = normalize(lightPos - vFragPos);
            float diff = max(dot(norm, lightDir), 0.0);
            vec3 diffuse = diff * vec3(1.0, 1.0, 1.0);

            vec3 viewDir = normalize(viewPos - vFragPos);
            vec3 reflectDir = reflect(-lightDir, norm);
            float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
            vec3 specular = 0.5 * spec * vec3(1.0, 1.0, 1.0);

            vec3 ambient = 0.1 * vec3(1.0, 1.0, 1.0);

            vec3 result = (ambient + diffuse + specular) * vColor.rgb;
            FragColor = vec4(result, vColor.a);
        }
        """

   
    def is_voxel_at_world_coords(self, x, y, z):
        chunk_pos = (x // 64, y // 64, z // 64)
        if chunk_pos in self.chunks:
            chunk = self.chunks[chunk_pos]
            local_x, local_y, local_z = x % 64, y % 64, z % 64
            return chunk.is_voxel_at((local_x, local_y, local_z))
        return False

    def get_or_create_chunk(self, chunk_position):
        if chunk_position not in self.chunks:
            self.chunks[chunk_position] = Chunk(chunk_position, self)
        return self.chunks[chunk_position]

    def set_voxel(self, position, color):
        chunk_position = (position[0] // 64, position[1] // 64, position[2] // 64)
        local_position = (position[0] % 64, position[1] % 64, position[2] % 64)
        chunk = self.get_or_create_chunk(chunk_position)
        chunk.set_voxel(local_position, color)

    def update_chunks(self, camera_position):
        camera_chunk = (int(camera_position[0]) // 64, int(camera_position[1]) // 64, int(camera_position[2]) // 64)
        chunk_radius = math.ceil(self.render_distance / 64)

        for dx in range(-chunk_radius, chunk_radius + 1):
            for dy in range(-chunk_radius, chunk_radius + 1):
                for dz in range(-chunk_radius, chunk_radius + 1):
                    chunk_pos = (camera_chunk[0] + dx, camera_chunk[1] + dy, camera_chunk[2] + dz)
                    distance = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2) * 64

                    if distance <= self.render_distance:
                        if chunk_pos not in self.loaded_chunks and chunk_pos not in self.chunk_queue:
                            self.chunk_queue.add(chunk_pos)

        chunks_to_remove = [chunk_pos for chunk_pos in self.loaded_chunks
                            if math.sqrt((chunk_pos[0] - camera_chunk[0]) ** 2 +
                                         (chunk_pos[1] - camera_chunk[1]) ** 2 +
                                         (chunk_pos[2] - camera_chunk[2]) ** 2) * 64 > self.render_distance]

        for chunk_pos in chunks_to_remove:
            self.loaded_chunks.remove(chunk_pos)
            if chunk_pos in self.chunks:
                del self.chunks[chunk_pos]

    def process_chunk_queue(self):
        if self.chunk_queue:
            chunk_pos = self.chunk_queue.pop()
            if chunk_pos not in self.loaded_chunks:
                self.thread_pool.submit(self.generate_and_mesh_chunk, chunk_pos)
                self.loaded_chunks.add(chunk_pos)

    def generate_and_mesh_chunk(self, chunk_pos):
        chunk = self.get_or_create_chunk(chunk_pos)
        generate_chunk_terrain(chunk)
        for lod in [1, 2, 4]:
            chunk.generate_mesh(lod)

    def render(self, camera_position):
        glUseProgram(self.shader)

        model_loc = glGetUniformLocation(self.shader, "model")
        view_loc = glGetUniformLocation(self.shader, "view")
        proj_loc = glGetUniformLocation(self.shader, "projection")
        light_pos_loc = glGetUniformLocation(self.shader, "lightPos")
        view_pos_loc = glGetUniformLocation(self.shader, "viewPos")

        glUniformMatrix4fv(model_loc, 1, GL_FALSE, np.identity(4))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, glGetFloatv(GL_MODELVIEW_MATRIX))
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, glGetFloatv(GL_PROJECTION_MATRIX))
        glUniform3f(light_pos_loc, camera_position[0], camera_position[1] + 10, camera_position[2])
        glUniform3f(view_pos_loc, camera_position[0], camera_position[1], camera_position[2])

        for chunk_pos, chunk in self.chunks.items():
            distance = np.linalg.norm(np.array(chunk_pos) * 64 - camera_position)
            lod = next((l for l, d in sorted(self.lod_distances.items(), key=lambda x: -x[1]) if distance <= d), 4)

            if chunk.lod_needs_remesh[lod]:
                chunk.generate_mesh(lod)

            glBindVertexArray(chunk.vao)
            glDrawArrays(GL_QUADS, 0, len(chunk.lod_meshes[lod]) // 10)
            glBindVertexArray(0)

        glUseProgram(0)

def generate_chunk_terrain(chunk):
    scale = 0.05
    octaves = 4
    persistence = 0.5
    lacunarity = 2.0

    for x in range(64):
        for z in range(64):
            world_x = x + chunk.position[0] * 64
            world_z = z + chunk.position[2] * 64
            height = int(noise.pnoise2(world_x * scale, world_z * scale, octaves=octaves, persistence=persistence,
                                       lacunarity=lacunarity) * 32 + 32)
            for y in range(height):
                if y == height - 1:
                    color = (0.0, 0.7, 0.0)  # Green for top layer
                elif y > height - 4:
                    color = (0.5, 0.25, 0.0)  # Brown for dirt
                else:
                    color = (0.5, 0.5, 0.5)  # Gray for stone
                chunk.set_voxel((x, y, z), color)

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
    gluPerspective(45, (display[0] / display[1]), 0.1, 1000.0)
    glMatrixMode(GL_MODELVIEW)

    world = VoxelWorld()
    camera = Camera()

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

        speed = 0.1
        if keys[pygame.K_w]: camera.move(0, 0, speed)
        if keys[pygame.K_s]: camera.move(0, 0, -speed)
        if keys[pygame.K_a]: camera.move(speed, 0, 0)
        if keys[pygame.K_d]: camera.move(-speed, 0, 0)
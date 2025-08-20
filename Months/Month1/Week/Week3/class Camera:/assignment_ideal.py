import time

import pygame
from OpenGL.GL import shaders
from pygame.math import Vector3
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import numpy as np
import math
import noise
from concurrent.futures import ThreadPoolExecutor


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
    def __init__(self, position, world):
        self.position = position
        self.size = 64
        self.world = world  # Add this line
        self.voxels = np.zeros((64, 64, 64, 4), dtype=np.float32)
        self.mesh = None
        self.needs_remesh = True
        self.lod_meshes = {1: None, 1.5: None, 2: None, 3: None, 4: None}
        self.lod_needs_remesh = {1: True, 1.5: True, 2: True, 3: True, 4: True}
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

    def is_voxel_at_with_boundary_check(self, x, y, z):
        if 0 <= x < 64 and 0 <= y < 64 and 0 <= z < 64:
            return self.is_voxel_at((x, y, z))
        else:
            world_x = self.position[0] * 64 + x
            world_y = self.position[1] * 64 + y
            world_z = self.position[2] * 64 + z
            return self.world.is_voxel_at_world_coords(world_x, world_y, world_z)

    def set_voxel(self, position, color):
        x, y, z = position
        self.voxels[x, y, z] = color + (1.0,)
        self.needs_remesh = True
        for lod in self.lod_needs_remesh:
            self.lod_needs_remesh[lod] = True

    def is_voxel_at(self, position):
        x, y, z = position
        return self.voxels[x, y, z, 3] > 0  # Check the alpha value

    def generate_mesh(self, lod):
        vertices = []
        step = int(lod)  # Convert LOD to integer for stepping

        for x in range(0, 64, step):
            for y in range(0, 64, step):
                for z in range(0, 64, step):
                    if self.is_voxel_at((x, y, z)):
                        color = self.voxels[x, y, z][:3]  # Ensure we're only using RGB values

                        # Check each face and only add it if the adjacent voxel is empty
                        if not self.is_voxel_at_with_boundary_check(x - step, y, z):
                            vertices.extend(self.create_face(x, y, z, color, (-1, 0, 0), step))
                        if not self.is_voxel_at_with_boundary_check(x + step, y, z):
                            vertices.extend(self.create_face(x, y, z, color, (1, 0, 0), step))
                        if not self.is_voxel_at_with_boundary_check(x, y - step, z):
                            vertices.extend(self.create_face(x, y, z, color, (0, -1, 0), step))
                        if not self.is_voxel_at_with_boundary_check(x, y + step, z):
                            vertices.extend(self.create_face(x, y, z, color, (0, 1, 0), step))
                        if not self.is_voxel_at_with_boundary_check(x, y, z - step):
                            vertices.extend(self.create_face(x, y, z, color, (0, 0, -1), step))
                        if not self.is_voxel_at_with_boundary_check(x, y, z + step):
                            vertices.extend(self.create_face(x, y, z, color, (0, 0, 1), step))

        self.lod_meshes[lod] = np.array(vertices, dtype=np.float32)
        self.lod_needs_remesh[lod] = False

        #Update VBO and VAO
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.lod_meshes[lod].nbytes, self.lod_meshes[lod], GL_STATIC_DRAW)

        # Position attribute
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 40, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        # Color attribute
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 40, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)
        # Normal attribute
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 40, ctypes.c_void_p(28))
        glEnableVertexAttribArray(2)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def create_face(self, x, y, z, color, normal, step):
        r, g, b = color[:3]
        if normal == (-1, 0, 0):
            return [
                x, y, z, r, g, b, 1.0, *normal,
                x, y, z + step, r, g, b, 1.0, *normal,
                x, y + step, z + step, r, g, b, 1.0, *normal,
                x, y + step, z, r, g, b, 1.0, *normal,
            ]
        elif normal == (1, 0, 0):
            return [
                x + step, y, z, r, g, b, 1.0, *normal,
                x + step, y + step, z, r, g, b, 1.0, *normal,
                x + step, y + step, z + step, r, g, b, 1.0, *normal,
                x + step, y, z + step, r, g, b, 1.0, *normal,
            ]
        elif normal == (0, -1, 0):
            return [
                x, y, z, r, g, b, 1.0, *normal,
                x + step, y, z, r, g, b, 1.0, *normal,
                x + step, y, z + step, r, g, b, 1.0, *normal,
                x, y, z + step, r, g, b, 1.0, *normal,
            ]
        elif normal == (0, 1, 0):
            return [
                x, y + step, z, r, g, b, 1.0, *normal,
                x, y + step, z + step, r, g, b, 1.0, *normal,
                   x + step, y + step, z + step, r, g, b, 1.0, *normal,
                   x + step, y + step, z, r, g, b, 1.0, *normal,
            ]
        elif normal == (0, 0, -1):
            return [
                x, y, z, r, g, b, 1.0, *normal,
                x, y + step, z, r, g, b, 1.0, *normal,
                   x + step, y + step, z, r, g, b, 1.0, *normal,
                   x + step, y, z, r, g, b, 1.0, *normal,
            ]
        elif normal == (0, 0, 1):
            return [
                x, y, z + step, r, g, b, 1.0, *normal,
                      x + step, y, z + step, r, g, b, 1.0, *normal,
                      x + step, y + step, z + step, r, g, b, 1.0, *normal,
                x, y + step, z + step, r, g, b, 1.0, *normal,
            ]


class VoxelWorld:
    def __init__(self):
        self.chunks = {}
        self.render_distance = 4
        self.load_distance = 5
        self.chunk_queue = set()
        self.thread_pool = ThreadPoolExecutor(
            max_workers=16)  # or more, depending on your CPU
        self.loaded_chunks = set()
        self.mesh_vbos = {}
        self.instance_vbo = glGenBuffers(1)
        self.setup_shaders()
        self.setup_instance_data()
        self.render_radius = 256  # Adjust this value as needed
        self.lod_levels = [1, 2, 3, 4]
        self.lod_distances = {1: 128, 2: 256, 3: 384, 4: 512}
        self.lod_bias = 1.0  # Adjust this value to fine-tune LOD transitions

    def get_lod_for_distance(self, distance):
        adjusted_distance = distance * self.lod_bias
        for lod, max_distance in sorted(self.lod_distances.items()):
            if adjusted_distance < max_distance:
                return lod
        return max(self.lod_distances.keys())


    def setup_shaders(self):
        vertex_shader = """
        #version 120
        attribute vec3 aPos;
        attribute vec4 aColor;
        attribute vec3 aNormal;
        attribute vec3 aOffset;

        varying vec4 vColor;
        varying vec3 vNormal;
        varying vec3 vFragPos;

        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        uniform mat3 normalMatrix;

        void main()
        {
            vec3 fragPos = aPos + aOffset;
            gl_Position = projection * view * model * vec4(fragPos, 1.0);
            vColor = aColor;
            vNormal = normalMatrix * aNormal;
            vFragPos = vec3(model * vec4(fragPos, 1.0));
        }
        """

        fragment_shader = """
        #version 120
        varying vec4 vColor;
        varying vec3 vNormal;
        varying vec3 vFragPos;

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
            float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);
            vec3 specular = 0.5 * spec * vec3(1.0, 1.0, 1.0);

            vec3 ambient = 0.1 * vec3(1.0, 1.0, 1.0);

            vec3 result = (ambient + diffuse + specular) * vColor.rgb;
            gl_FragColor = vec4(result, vColor.a);
        }
        """

        self.shader = shaders.compileProgram(
            shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
        )

        # Store uniform locations
        self.model_loc = glGetUniformLocation(self.shader, "model")
        self.view_loc = glGetUniformLocation(self.shader, "view")
        self.proj_loc = glGetUniformLocation(self.shader, "projection")
        self.normal_matrix_loc = glGetUniformLocation(self.shader, "normalMatrix")
        self.light_pos_loc = glGetUniformLocation(self.shader, "lightPos")
        self.view_pos_loc = glGetUniformLocation(self.shader, "viewPos")


    def is_voxel_at_world_coords(self, x, y, z):
        chunk_pos = (x // 64, y // 64, z // 64)
        if chunk_pos in self.chunks:
            chunk = self.chunks[chunk_pos]
            local_x, local_y, local_z = x % 64, y % 64, z % 64
            return chunk.is_voxel_at((local_x, local_y, local_z))
        return False

    def setup_instance_data(self):
        self.instance_data = np.array([], dtype=np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.instance_vbo)
        glBufferData(GL_ARRAY_BUFFER, self.instance_data.nbytes, self.instance_data, GL_DYNAMIC_DRAW)

    def get_or_create_chunk(self, chunk_position):
        if chunk_position not in self.chunks:
            self.chunks[chunk_position] = Chunk(chunk_position, self)  # Pass self as the world reference
        return self.chunks[chunk_position]

    def set_voxel(self, position, color):
        chunk_position = (position[0] // 64, position[1] // 64, position[2] // 64)
        local_position = (position[0] % 64, position[1] % 64, position[2] % 64)
        chunk = self.get_or_create_chunk(chunk_position)
        chunk.set_voxel(local_position, color)

    def process_chunk_queue(self):
        if self.chunk_queue:
            chunk_pos = self.chunk_queue.pop()
            if chunk_pos not in self.loaded_chunks:
                chunk = self.get_or_create_chunk(chunk_pos)
                self.thread_pool.submit(generate_chunk_terrain, chunk)
                self.loaded_chunks.add(chunk_pos)

    def update_chunks(self, camera_position):
        camera_chunk = (int(camera_position.x) // 64, 0, int(camera_position.z) // 64)

        # Calculate the number of chunks in each direction based on the render radius
        chunk_radius = math.ceil(self.render_radius / 64)

        for dx in range(-chunk_radius, chunk_radius + 1):
            for dz in range(-chunk_radius, chunk_radius + 1):
                chunk_pos = (camera_chunk[0] + dx, 0, camera_chunk[2] + dz)
                distance = math.sqrt(dx ** 2 + dz ** 2) * 64

                if distance <= self.render_radius:
                    if chunk_pos not in self.loaded_chunks and chunk_pos not in self.chunk_queue:
                        self.chunk_queue.add(chunk_pos)

        # Remove chunks that are too far away
        chunks_to_remove = [chunk_pos for chunk_pos in self.loaded_chunks
                            if math.sqrt((chunk_pos[0] - camera_chunk[0]) ** 2 +
                                         (chunk_pos[2] - camera_chunk[2]) ** 2) * 64 > self.render_radius]

        for chunk_pos in chunks_to_remove:
            self.loaded_chunks.remove(chunk_pos)
            if chunk_pos in self.chunks:
                del self.chunks[chunk_pos]
            if chunk_pos in self.mesh_vbos:
                glDeleteBuffers(1, [self.mesh_vbos[chunk_pos]])
                del self.mesh_vbos[chunk_pos]

    def render(self, camera_position, frustum):
        start_time = time.time()
        glUseProgram(self.shader)

        view_matrix = glGetFloatv(GL_MODELVIEW_MATRIX)
        proj_matrix = glGetFloatv(GL_PROJECTION_MATRIX)

        glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, np.identity(4))
        glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, view_matrix)
        glUniformMatrix4fv(self.proj_loc, 1, GL_FALSE, proj_matrix)
        
        # Calculate normal matrix (transpose of the inverse of the upper-left 3x3 part of the model-view matrix)
        normal_matrix = np.linalg.inv(view_matrix[:3, :3]).T
        glUniformMatrix3fv(self.normal_matrix_loc, 1, GL_FALSE, normal_matrix)

        glUniform3f(self.light_pos_loc, camera_position.x, camera_position.y + 10, camera_position.z)
        glUniform3f(self.view_pos_loc, camera_position.x, camera_position.y, camera_position.z)

    # Rest of the rendering code...
    # (Keep the existing rendering logic here)

        visible_chunks = []
        for chunk_pos, chunk in self.chunks.items():
            chunk_center = Vector3(chunk_pos[0] * 64 + 32, chunk_pos[1] * 64 + 32, chunk_pos[2] * 64 + 32)
            if is_chunk_visible(frustum, chunk_center, 55.4):  # 55.4 is the radius of a chunk
                visible_chunks.append((chunk_pos, chunk))

        visible_chunks = self.occlusion_cull(visible_chunks, camera_position)

        for chunk_pos, chunk in visible_chunks:
            distance = np.linalg.norm(
                np.array(chunk_pos) * 64 - np.array([camera_position.x, camera_position.y, camera_position.z]))

            lod = self.get_lod_for_distance(distance)

            if chunk.lod_needs_remesh[lod]:
                chunk.generate_mesh(lod)
                if chunk_pos in self.mesh_vbos:
                    glDeleteBuffers(1, [self.mesh_vbos[chunk_pos]])
                vbo = glGenBuffers(1)
                glBindBuffer(GL_ARRAY_BUFFER, vbo)
                glBufferData(GL_ARRAY_BUFFER, chunk.lod_meshes[lod].nbytes, chunk.lod_meshes[lod], GL_STATIC_DRAW)
                self.mesh_vbos[chunk_pos] = vbo

            if chunk_pos in self.mesh_vbos:
                glBindVertexArray(chunk.vao)

                # Update instance data
                instance_data = np.array([chunk_pos[0] * 64, chunk_pos[1] * 64, chunk_pos[2] * 64], dtype=np.float32)
                glBindBuffer(GL_ARRAY_BUFFER, self.instance_vbo)
                glBufferData(GL_ARRAY_BUFFER, instance_data.nbytes, instance_data, GL_DYNAMIC_DRAW)

                # Set up instanced attribute
                glEnableVertexAttribArray(3)
                glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
                glVertexAttribDivisor(3, 1)

                glDrawArraysInstanced(GL_QUADS, 0, len(chunk.lod_meshes[lod]) // 10, 1)

                glBindVertexArray(0)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glUseProgram(0)

    def occlusion_cull(self, visible_chunks, camera_position):
        culled_chunks = []
        depth_buffer = np.full((int(self.render_radius / 32) * 2 + 1, int(self.render_radius / 32) * 2 + 1), np.inf)
        camera_chunk = (int(camera_position.x) // 64, int(camera_position.y) // 64, int(camera_position.z) // 64)

        # Sort chunks by distance from camera
        visible_chunks.sort(key=lambda x: np.linalg.norm(
            np.array(x[0]) * 64 - np.array([camera_position.x, camera_position.y, camera_position.z])))

        center = int(self.render_radius / 32)
        for chunk_pos, chunk in visible_chunks:
            x, y, z = chunk_pos
            dx, dz = x - camera_chunk[0], z - camera_chunk[2]

            chunk_depth = np.linalg.norm(np.array([dx, dz]))
            buffer_x, buffer_z = dx + center, dz + center

            if 0 <= buffer_x < depth_buffer.shape[0] and 0 <= buffer_z < depth_buffer.shape[1]:
                if chunk_depth < depth_buffer[buffer_x, buffer_z]:
                    depth_buffer[buffer_x, buffer_z] = chunk_depth
                    culled_chunks.append((chunk_pos, chunk))

        return culled_chunks


def process_chunk_queue(self):
    while self.chunk_queue:
        chunk_pos = self.chunk_queue.pop()
        if chunk_pos not in self.loaded_chunks:
            self.thread_pool.submit(self.generate_and_mesh_chunk, chunk_pos)
            self.loaded_chunks.add(chunk_pos)


def generate_and_mesh_chunk(self, chunk_pos):
    chunk = self.get_or_create_chunk(chunk_pos)
    generate_chunk_terrain(chunk)
    for lod in [1, 2, 4]:
        chunk.generate_mesh(lod)


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
    chunk.needs_remesh = True
    for lod in chunk.lod_needs_remesh:
        chunk.lod_needs_remesh[lod] = True


def create_frustum(self, camera):
    frustum = []
    m = glGetFloatv(GL_MODELVIEW_MATRIX).transpose()
    p = glGetFloatv(GL_PROJECTION_MATRIX).transpose()
    clip = np.dot(p, m)

    def normalize_plane(plane):
        mag = np.linalg.norm(plane[:3])
        return plane / mag

    # Right, Left, Bottom, Top, Far, Near
    frustum.append(normalize_plane(clip[3] - clip[0]))
    frustum.append(normalize_plane(clip[3] + clip[0]))
    frustum.append(normalize_plane(clip[3] - clip[1]))
    frustum.append(normalize_plane(clip[3] + clip[1]))
    frustum.append(normalize_plane(clip[3] - clip[2]))
    frustum.append(normalize_plane(clip[3] + clip[2]))

    return frustum


def is_chunk_visible(frustum, chunk_center, chunk_radius):
    for plane in frustum:
        if np.dot(plane[:3], chunk_center) + plane[3] <= -chunk_radius:
            return False
    return True


def main():
    pygame.init()
    display = (800, 640)
    pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    glViewport(0, 0, display[0], display[1])
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (display[0] / display[1]), 0.1, 1000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

    world = VoxelWorld()
    camera = Camera()
    camera.position = Vector3(64, 40, 64)

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

        keys = pygame.key.get_pressed()
        mouse_dx, mouse_dy = pygame.mouse.get_rel()

        camera.rotate(-mouse_dx * 0.1, -mouse_dy * 0.1)

        movement_speed = 0.5
        forward = (keys[pygame.K_w] - keys[pygame.K_s]) * movement_speed
        right = (keys[pygame.K_d] - keys[pygame.K_a]) * movement_speed
        up = (keys[pygame.K_SPACE] - keys[pygame.K_LSHIFT]) * movement_speed

        camera.move(right, up, forward)

        world.update_chunks(camera.position)
        world.process_chunk_queue()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        camera.apply()
        frustum = create_frustum(world, camera)
        world.render(camera.position, frustum)

        pygame.display.flip()
        clock.tick(60)

def main():
    pygame.init()
    display = (800, 640)
    pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    glViewport(0, 0, display[0], display[1])
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (display[0] / display[1]), 0.1, 1000.0)
    glMatrixMode(GL_MODELVIEW)

    camera = Camera()
    world = VoxelWorld()

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
        if keys[pygame.K_w]:
            camera.move(0, 0, 0.1)
        if keys[pygame.K_s]:
            camera.move(0, 0, -0.1)
        if keys[pygame.K_a]:
            camera.move(0.1, 0, 0)
        if keys[pygame.K_d]:
            camera.move(-0.1, 0, 0)
        if keys[pygame.K_SPACE]:
            camera.move(0, 0.1, 0)
        if keys[pygame.K_LSHIFT]:
            camera.move(0, -0.1, 0)

        mouse_rel = pygame.mouse.get_rel()
        camera.rotate(mouse_rel[0] * 0.1, -mouse_rel[1] * 0.1)

        glLoadIdentity()
        camera.apply()

        frustum = create_frustum(world, camera)
        world.update_chunks(camera.position)
        world.process_chunk_queue()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        world.render(camera.position, frustum)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()



from OpenGL.GL import *
from OpenGL.GLUT import *
from PIL import Image
import os


class Road:
    def __init__(self):
        self.road_texture = self.load_texture("./assets/road_texture.png")

    def load_texture(self, file):
        """ Load a texture from a file. """
        if not os.path.exists(file):
            raise FileNotFoundError(f"Texture file not found: {file}")

        img = Image.open(file)
        img_data = img.tobytes("raw", "RGBX", 0, -1)

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                     img.size[0], img.size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

        return texture

    def draw_road(self):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.road_texture)
        glColor3f(1, 1, 1)  # Reset color to white for texture rendering
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3f(-10, -10, 0)
        glTexCoord2f(1, 0)
        glVertex3f(10, -10, 0)
        glTexCoord2f(1, 1)
        glVertex3f(10, 10, 0)
        glTexCoord2f(0, 1)
        glVertex3f(-10, 10, 0)
        glEnd()
        glDisable(GL_TEXTURE_2D)

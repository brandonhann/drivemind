from OpenGL.GL import *
import math
import os
from PIL import Image
from car_config import car_configurations


class Car:
    def __init__(self, lane, direction, linear_speed=0.06):
        self.lane = lane
        self.direction = direction
        self.linear_speed = linear_speed
        self.config = car_configurations[(lane, direction)]
        self.x = self.config["x"]
        self.y = self.config["y"]
        self.angle = self.config["angle"]
        self.radius = self.config["radius"]
        self.car_texture = self.load_texture("./assets/car.png")
        # Default to False if not specified
        self.flip_texture = self.config.get("flip_texture", False)
        self.visible = True

    def load_texture(self, file):
        """ Load a texture from a file. """
        if not os.path.exists(file):
            raise FileNotFoundError(f"Texture file not found: {file}")

        img = Image.open(file)
        # Ensuring the image is in RGBA format
        img = img.convert("RGBA")
        img_data = img.tobytes("raw", "RGBA", 0, -1)

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                     img.size[0], img.size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

        return texture

    def update_position(self):
        if self.lane == "straight":
            if "left" in self.direction or "right" in self.direction:
                self.x += -self.linear_speed if self.direction == "left" else self.linear_speed
                # Check if the car is out of bounds for left/right movement
                if self.x < -10 or self.x > 10:
                    self.visible = False  # Make the car invisible instead of resetting
            elif "front" in self.direction or "down" in self.direction:
                self.y += self.linear_speed if self.direction == "front" else -self.linear_speed
                # Check if the car is out of bounds for front/down movement
                if self.y < -10 or self.y > 10:
                    self.visible = False  # Make the car invisible instead of resetting
        else:  # For curved paths (lane is either "left" or "right")
            angle_speed = (self.linear_speed /
                           (2 * math.pi * self.radius)) * 360
            if self.lane == "left":
                self.angle += angle_speed
                self.angle %= 360  # Normalize the angle for left turns
            else:  # self.lane == "right"
                self.angle -= angle_speed
                while self.angle < 0:
                    self.angle += 360  # Ensure angle stays positive

            # Update position based on the new angle
            self.x = self.config["x"] + self.radius * \
                math.cos(math.radians(self.angle))
            self.y = self.config["y"] + self.radius * \
                math.sin(math.radians(self.angle))

            # Check if the turn is complete for curved paths
            if self.is_turn_complete():
                self.visible = False  # Make the car invisible once the turn is complete

    def is_turn_complete(self):
        # Calculate the angle difference from the start angle
        angle_diff = (self.angle - self.config["angle"]) % 360
        # Check for completion of turn for both left and right turns
        return angle_diff >= 90 and angle_diff < 270

    def set_initial_position(self):
        self.x = self.config["x"]
        self.y = self.config["y"]
        self.angle = self.config["angle"]

    def calculate_progress(self):
        progress = 0
        if self.lane == "straight":
            if "left" in self.direction or "right" in self.direction:
                start_pos = self.config["x"]
                end_pos = -start_pos
                total_distance = abs(end_pos - start_pos)
                current_distance = abs(self.x - start_pos)
                progress = (current_distance / total_distance) * 100
            elif "front" in self.direction or "down" in self.direction:
                start_pos = self.config["y"]
                end_pos = -start_pos
                total_distance = abs(end_pos - start_pos)
                current_distance = abs(self.y - start_pos)
                progress = (current_distance / total_distance) * 100

        else:  # Curved paths
            start_angle = self.config["angle"]
            current_angle = self.angle
            angle_diff = 0

            if self.lane == "left":
                angle_diff = (current_angle - start_angle + 360) % 360
            elif self.lane == "right":
                # Correctly handling right turn angle difference
                if current_angle <= start_angle:
                    angle_diff = start_angle - current_angle
                else:
                    angle_diff = start_angle + (360 - current_angle)

            progress = (angle_diff / 90) * 100
            # Ensure progress does not exceed 100%
            progress = min(progress, 100)

        return progress

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.angle - 90, 0, 0, 1)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.car_texture)
        glColor3f(1, 1, 1)

        glBegin(GL_QUADS)
        # Apply texture coordinates based on flip_texture
        if self.flip_texture:
            glTexCoord2f(1, 0)
            glVertex3f(-1, -0.5, 0.02)
            glTexCoord2f(0, 0)
            glVertex3f(1, -0.5, 0.02)
            glTexCoord2f(0, 1)
            glVertex3f(1, 0.5, 0.02)
            glTexCoord2f(1, 1)
            glVertex3f(-1, 0.5, 0.02)
        else:
            glTexCoord2f(0, 0)
            glVertex3f(-1, -0.5, 0.02)
            glTexCoord2f(1, 0)
            glVertex3f(1, -0.5, 0.02)
            glTexCoord2f(1, 1)
            glVertex3f(1, 0.5, 0.02)
            glTexCoord2f(0, 1)
            glVertex3f(-1, 0.5, 0.02)
        glEnd()

        glDisable(GL_TEXTURE_2D)
        glPopMatrix()

import pygame
from OpenGL.GL import *
from OpenGL.GLUT import *
import sys
import math


class UserInterface:
    def __init__(self, initial_window_size=(896, 504)):
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 14)
        glutInit(sys.argv)
        self.initial_window_size = initial_window_size
        self.scale_factor = (1, 1)
        self.car_count_positions = {
            "straight_left": (670, 290),    # Near x: 10, y: 4
            "straight_right": (135, 205),   # Near x: -10, y: -4
            "straight_front": (605, 65),    # Near x: 4, y: -10
            "straight_down": (375, 350),    # Near x: -4, y: 10
            "right_down": (335, 350),       # Near x: -10, y: 10
            "right_left": (660, 310),       # Near x: 10, y: 10
            "right_front": (690, 65),      # Near x: 10, y: -10 CHANGE THIS
            "right_right": (105, 175),      # Near x: -10, y: -10
            "left_left": (690, 275),        # Near x: 10, y: 10 CHANGE THIS
            "left_right": (150, 230),       # Near x: -10, y: 10
            "left_front": (525, 65),       # Near x: -10, y: -10
            "left_down": (410, 350),        # Near x: 10, y: -10
        }
        self.previous_car_counts = {}  # Add this line to store previous car counts

    def set_initial_window_size(self, size):
        self.initial_window_size = size

    def update_scale_factor(self, current_window_size):
        self.scale_factor = (current_window_size[0] / self.initial_window_size[0],
                             current_window_size[1] / self.initial_window_size[1])

    def draw_circle(self, x, y, radius, color):
        segments = 32  # Number of segments to approximate the circle
        glColor3fv(color)  # Set the color of the circle
        glBegin(GL_TRIANGLE_FAN)
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            glVertex2f(x + math.cos(angle) * radius,
                       y + math.sin(angle) * radius)
        glEnd()

    def render_text(self, text, x, y, color=(255, 255, 255)):
        scaled_x = x * self.scale_factor[0]
        scaled_y = y * self.scale_factor[1]
        glColor3f(*color)
        glWindowPos2f(scaled_x, scaled_y)
        for character in text:
            glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(character))

    def draw_traffic_lights(self, traffic_lights):
        # Determine colors based on traffic light state
        front_back_color = self.get_color_from_state(
            traffic_lights["front_back"].get_visual_state())
        left_right_color = self.get_color_from_state(
            traffic_lights["left_right"].get_visual_state())

        # Draw the traffic lights with appropriate colors
        self.draw_circle(-12, 0, 1, left_right_color)  # Left
        self.draw_circle(12, 0, 1, left_right_color)   # Right
        self.draw_circle(0, -12, 1, front_back_color)  # Bottom
        self.draw_circle(0, 12, 1, front_back_color)   # Top

    def get_color_from_state(self, state):
        if state == "green":
            return (0, 1, 0)
        elif state == "yellow":
            return (1, 1, 0)
        else:  # red or any other state
            return (1, 0, 0)

    def draw_car_counts(self, car_counts):
        for key, (x, y) in self.car_count_positions.items():
            count = car_counts.get(key, 0)  # Get the count for each position
            # Check if the count has changed since the last draw
            if self.previous_car_counts.get(key, -1) != count:
                # Debugging print only if count has changed
                print(f"Drawing {key} with count: {count}")
            self.previous_car_counts[key] = count  # Update the previous counts
            self.render_text(str(count), x, y)

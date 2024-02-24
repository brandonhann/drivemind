from OpenGL.GL import *
import math


class Path:
    def __init__(self):
        pass

    def draw_path(self, start_x, start_y, end_x=None, end_y=None, radius=None, start_angle=None, end_angle=None, direction='front'):
        colors = {'front': (1, 0, 0), 'down': (0, 0, 1),
                  'left': (0, 1, 0), 'right': (1, 1, 0)}
        glColor3f(*colors[direction])
        glLineWidth(2)

        if end_x is not None and end_y is not None:
            glBegin(GL_LINES)
            glVertex3f(start_x, start_y, 0.01)
            glVertex3f(end_x, end_y, 0.01)
            glEnd()
        else:
            glBegin(GL_LINE_STRIP)
            angle_step = 1
            for angle in range(start_angle, end_angle + angle_step, angle_step):
                rad = math.radians(angle)
                x = start_x + (radius * math.cos(rad))
                y = start_y + (radius * math.sin(rad))
                glVertex3f(x, y, 0.01)
            glEnd()

    def draw_paths(self):
        # Draw straight paths (straight)
        self.draw_path(-10, 4, 10, 4, direction='left')
        self.draw_path(-10, -4, 10, -4, direction='right')
        self.draw_path(4, -10, 4, 10, direction='front')
        self.draw_path(-4, -10, -4, 10, direction='down')

        # Draw turning paths (right)
        self.draw_path(-10, -10, radius=4, start_angle=0,
                       end_angle=90, direction='right')
        self.draw_path(10, -10, radius=4, start_angle=90,
                       end_angle=180, direction='front')
        self.draw_path(10, 10, radius=4, start_angle=180,
                       end_angle=270, direction='left')
        self.draw_path(-10, 10, radius=4, start_angle=270,
                       end_angle=360, direction='down')

        # Draw wider turning paths (left)
        self.draw_path(-10, -10, radius=12, start_angle=0,
                       end_angle=90, direction='front')
        self.draw_path(10, -10, radius=12, start_angle=90,
                       end_angle=180, direction='left')
        self.draw_path(10, 10, radius=12, start_angle=180,
                       end_angle=270, direction='down')
        self.draw_path(-10, 10, radius=12, start_angle=270,
                       end_angle=360, direction='right')

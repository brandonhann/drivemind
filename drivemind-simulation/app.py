import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
import subprocess
import sys
import os
import threading
import cProfile
import pstats
import signal
from PIL import Image
from path import Path
from road import Road
from car import Car
from ui import UserInterface
from traffic_light import TrafficLight

output_dir = "output"
frames_dir = "frames"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
frames_output_dir = os.path.join(output_dir, frames_dir)
if not os.path.exists(frames_output_dir):
    os.makedirs(frames_output_dir)


def frames_to_video(input_path="output/frames", output_path="output", fps=30):
    input_path_formatted = input_path.replace("\\", "/")
    output_path_formatted = output_path.replace("\\", "/")
    command = (
        f"ffmpeg -framerate {fps} -i {input_path_formatted}/frame_%05d.png "
        f"-c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p "
        f"{input_path_formatted}/simulation_video.mp4"
    )
    subprocess.run(command, shell=True, check=True)


def main():
    pygame.init()
    pygame.display.set_caption('drivemind-simulation')
    display = (896, 504)
    show_debug = True
    screen = pygame.display.set_mode(
        display, DOUBLEBUF | OPENGL | pygame.RESIZABLE)
    init_opengl(display)

    clock = pygame.time.Clock()
    target_fps = 60
    # Interval in seconds for frame capture
    frame_capture_interval = 1.0 / target_fps
    last_frame_capture_time = 0

    capture_interval = 5

    path = Path()
    road = Road()
    ui = UserInterface()

    ffmpeg_cmd = [
        'ffmpeg',
        '-y',  # Overwrite output file if it exists
        '-f', 'rawvideo',  # Input format
        '-vcodec', 'rawvideo',
        '-s', '896x504',  # Size of one frame
        '-pix_fmt', 'rgba',  # Format
        '-r', str(target_fps),  # Ensure this matches target_fps
        '-i', '-',  # The input comes from a pipe
        '-vf', 'vflip',  # Flip the video
        '-an',  # No audio
        '-vcodec', 'mpeg4',
        '-b:v', '5000k',  # Bitrate
        f'{output_dir}/simulation.mp4'
    ]
    ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    frame_number = 0
    frame_path = os.path.join(
        frames_output_dir, f"frame_{frame_number:05d}.png")
    threads = []

    # Random intensity between 1 and 5 for initial setup
    intensity_range = random.randint(1, 5)
    car_counts = generate_car_counts(
        intensity_range)  # Initialize car counts here
    active_lights = "left_right"
    traffic_light_interval = 5  # Duration for green light
    yellow_light_duration = 3    # Duration for yellow light
    red_light_delay = 3          # Delay after red light
    prev_front_back_state = None
    prev_left_right_state = None
    traffic_lights = {
        "front_back": TrafficLight(traffic_light_interval, yellow_light_duration, red_light_delay),
        "left_right": TrafficLight(traffic_light_interval, yellow_light_duration, red_light_delay)
    }
    cars = []

    traffic_lights["left_right"].state = "green"
    traffic_lights["left_right"].visual_state = "green"

    last_frame_time = time.time()
    frame_times = []

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt
            current_time = time.time()
            frame_number += 1
            if (current_time - last_frame_capture_time) >= frame_capture_interval:
                width, height = pygame.display.get_surface().get_size()
                image_data = glReadPixels(
                    0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)

                # Define frame_path here, where it's used
                frame_path = os.path.join(
                    frames_output_dir, f"frame_{frame_number:05d}.png")

                try:
                    ffmpeg_process.stdin.write(image_data)
                    last_frame_capture_time = current_time
                except BrokenPipeError:
                    print("Error: FFMPEG process was closed.", file=sys.stderr)
                    break

                # Use threading to save the frame asynchronously
                thread = threading.Thread(
                    target=save_frame_async, args=(image_data, frame_path, width, height))
                thread.start()
                threads.append(thread)

            # Update the state of traffic lights
            traffic_lights["front_back"].update()
            traffic_lights["left_right"].update()

            # Check the current state of the traffic lights
            front_back_state = traffic_lights["front_back"].state
            left_right_state = traffic_lights["left_right"].state

            # If the traffic light state changes to red, generate new car counts
            if (active_lights == "left_right" and left_right_state == "red" and prev_left_right_state != "red") or \
                    (active_lights == "front_back" and front_back_state == "red" and prev_front_back_state != "red"):
                # Determine new intensity for car generation
                intensity = random.randint(1, 5)
                # Generate new car counts based on intensity
                car_counts = generate_car_counts(intensity)

            # Update the previous state variables for the next iteration
            prev_front_back_state = front_back_state
            prev_left_right_state = left_right_state

            # Logic to switch the active lights from left_right to front_back or vice versa
            if active_lights == "left_right" and traffic_lights["left_right"].is_red_delayed():
                traffic_lights["front_back"].state = "green"
                traffic_lights["front_back"].visual_state = "green"
                traffic_lights["front_back"].last_change_time = time.time()
                active_lights = "front_back"
            elif active_lights == "front_back" and traffic_lights["front_back"].is_red_delayed():
                traffic_lights["left_right"].state = "green"
                traffic_lights["left_right"].visual_state = "green"
                traffic_lights["left_right"].last_change_time = time.time()
                active_lights = "left_right"

            # Decrement car counts for the active green light side every second
            current_time = time.time()
            if "last_countdown_update" not in locals() or current_time - last_countdown_update >= 1:
                if active_lights == "left_right" and left_right_state == "green":
                    decrement_car_counts(car_counts, "left_right", cars)
                elif active_lights == "front_back" and front_back_state == "green":
                    decrement_car_counts(car_counts, "front_back", cars)
                last_countdown_update = current_time

            cars = [car for car in cars if car.visible]
            render_scene(road, path, ui, cars, traffic_lights,
                         car_counts, show_debug)
            # Capture frame
            if frame_number % 5 == 0:  # Adjust capture interval as needed
                width, height = pygame.display.get_surface().get_size()
                image_data = glReadPixels(
                    0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
                try:
                    ffmpeg_process.stdin.write(image_data)
                except BrokenPipeError:
                    print("Error: FFMPEG process was closed.", file=sys.stderr)
                    break

            frame_number += 1
            if frame_number % capture_interval == 0:
                thread = threading.Thread(
                    target=save_frame_async, args=(image_data, frame_path, width, height))
                thread.start()
                threads.append(thread)
            pygame.display.flip()
            clock.tick(target_fps)
            pygame.time.wait(10)

    except KeyboardInterrupt:
        print("Shutting down...")

    finally:
        # Properly terminate the ffmpeg process
        ffmpeg_process.stdin.close()
        ffmpeg_process.wait()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Release any other resources, if necessary
        pygame.quit()


def init_opengl(display):
    """ Initialize OpenGL context """
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Set clear color
    glEnable(GL_DEPTH_TEST)  # Enable depth testing
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glClearDepth(1.0)  # Set depth clear value
    resize_opengl(display)  # Set initial viewport and projection


def resize_opengl(size):
    """ Handle window resizing """
    glViewport(0, 0, size[0], size[1])  # Set viewport to cover new window size
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (size[0] / size[1]), 1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, -22, 10, 0, 0, 0, 0, 1, 0)


def render_scene(road, path, ui, cars, traffic_lights, car_counts, show_debug):
    """ Render the scene each frame """
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear buffers

    road.draw_road()
    path.draw_paths()
    if show_debug:
        ui.draw_traffic_lights(traffic_lights)
        ui.draw_car_counts(car_counts)

    for car in cars:
        if car.visible:
            car.update_position()
            car.draw()


def decrement_car_counts(car_counts, active_side, cars):
    lane_mapping = {
        "left_left": ("left", "left"),
        "straight_left": ("straight", "left"),
        "right_left": ("right", "left"),
        "left_right": ("left", "right"),
        "straight_right": ("straight", "right"),
        "right_right": ("right", "right"),
        "left_front": ("left", "front"),
        "straight_front": ("straight", "front"),
        "right_front": ("right", "front"),
        "left_down": ("left", "down"),
        "straight_down": ("straight", "down"),
        "right_down": ("right", "down"),
    }

    if active_side == "left_right":
        keys_to_decrement = ["left_left", "straight_left",
                             "right_left", "left_right", "straight_right", "right_right"]
    else:  # active_side == "front_back"
        keys_to_decrement = ["left_front", "straight_front",
                             "right_front", "left_down", "straight_down", "right_down"]

    for key in keys_to_decrement:
        if car_counts[key] > 0:
            car_counts[key] -= 1
            # Determine the lane and direction for the new car
            lane, direction = lane_mapping[key]
            # Add a new car to the track for each count decremented
            cars.append(Car(lane, direction))


def generate_car_counts(intensity):
    car_counts = {
        "straight_left": random.randint(0, intensity),
        "straight_right": random.randint(0, intensity),
        "straight_front": random.randint(0, intensity),
        "straight_down": random.randint(0, intensity),
        "right_down": random.randint(0, intensity),
        "right_left": random.randint(0, intensity),
        "right_front": random.randint(0, intensity),
        "right_right": random.randint(0, intensity),
        "left_left": random.randint(0, intensity),
        "left_right": random.randint(0, intensity),
        "left_front": random.randint(0, intensity),
        "left_down": random.randint(0, intensity)
    }
    return car_counts


def save_frame_async(image_data, frame_path, width, height):
    image = Image.frombytes("RGBA", (width, height), image_data)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image.save(frame_path)


if __name__ == "__main__":
    profiler = cProfile.Profile()
    try:
        profiler.enable()
        main()
    finally:
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumtime')
        stats.print_stats()
        frames_to_video("./output/frames", "./output", fps=30)
        print("Video saved to ./output/simulation.mp4")

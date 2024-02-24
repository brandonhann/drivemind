import glob
import os

output_dir = "output/frames"


def delete_files(dir):
    frame_files = glob.glob(os.path.join(dir, 'frame_*.png'))
    for file in frame_files:
        os.remove(file)

    video_file = os.path.join(dir, 'simulation_video.mp4')
    if os.path.exists(video_file):
        os.remove(video_file)


delete_files(output_dir)

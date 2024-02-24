car_configurations = {
    # Straight paths
    # Car moving left on top horizontal path
    ("straight", "left"): {"x": 10, "y": 4, "angle": 90, "radius": None, "flip_texture": False},
    # Car moving right on bottom horizontal path
    ("straight", "right"): {"x": -10, "y": -4, "angle": 90, "radius": None, "flip_texture": True},
    # Car moving up on right vertical path
    ("straight", "front"): {"x": 4, "y": -10, "angle": 0, "radius": None, "flip_texture": False},
    # Car moving down on left vertical path
    ("straight", "down"): {"x": -4, "y": 10, "angle": 0, "radius": None, "flip_texture": True},

    # Right turning paths (smaller radius)
    # Car turning right from bottom to left
    ("right", "down"): {"x": -10, "y": 10, "angle": 0, "radius": 4, "flip_texture": True},
    # Car turning right from left to top
    ("right", "left"): {"x": 10, "y": 10, "angle": 270, "radius": 4, "flip_texture": True},
    # Car turning right from top to right
    ("right", "front"): {"x": 10, "y": -10, "angle": 180, "radius": 4, "flip_texture": True},
    # Car turning right from right to bottom
    ("right", "right"): {"x": -10, "y": -10, "angle": 90, "radius": 4, "flip_texture": True},

    # Left turning paths (larger radius)
    # Car turning left from bottom to left
    ("left", "left"): {"x": 10, "y": -10, "angle": 90, "radius": 12, "flip_texture": False},
    # Car turning left from top to right
    ("left", "right"): {"x": -10, "y": 10, "angle": 270, "radius": 12, "flip_texture": False},
    # Car turning left from left to bottom
    ("left", "front"): {"x": -10, "y": -10, "angle": 0, "radius": 12, "flip_texture": False},
    # Car turning left from right to top
    ("left", "down"): {"x": 10, "y": 10, "angle": 180, "radius": 12, "flip_texture": False},
}

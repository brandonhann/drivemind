import cv2
import numpy as np
import os

# Initialize global variables
drawing = False  # true if mouse is pressed
ix, iy = -1, -1
collision_boxes = {}
display_size = (896, 504)

# Path to the background image
bg_image_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "bg.png")

# Load the background image
bg_img = cv2.imread(bg_image_path)

# Check if the image loaded successfully
if bg_img is None:
    print("Error: Could not load background image.")
    exit()

# Resize the background image to match the display size
bg_img = cv2.resize(bg_img, display_size)

# Create a window and bind the function to window
cv2.namedWindow('image')


def draw_rectangle_with_drag(event, x, y, flags, param):
    global ix, iy, drawing, bg_img

    # Create a copy of the original image to draw the preview rectangle
    temp_img = bg_img.copy()

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            # Draw the rectangle on the temporary image for preview
            cv2.rectangle(temp_img, (ix, iy), (x, y), (0, 255, 0), 2)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        # Finalize the drawing on the original image
        cv2.rectangle(bg_img, (ix, iy), (x, y), (0, 255, 0), 2)

        # Display the final image before pausing for input
        cv2.imshow('image', bg_img)
        cv2.waitKey(1)  # Refresh the display

        # Now, prompt for the box name
        box_name = input("Enter the name for this box: ")

        # Calculate and store the box details
        width = abs(x - ix)
        height = abs(y - iy)
        collision_boxes[box_name] = (min(ix, x), min(iy, y), width, height)

        print(
            f"Box '{box_name}' drawn: Top-left ({min(ix, x)}, {min(iy, y)}) Width {width}, Height {height}")

    # Display the temporary image if drawing
    if drawing:
        cv2.imshow('image', temp_img)
    else:
        cv2.imshow('image', bg_img)


cv2.setMouseCallback('image', draw_rectangle_with_drag)

while (1):
    cv2.imshow('image', bg_img)
    if cv2.waitKey(20) & 0xFF == 27:  # Break if ESC is pressed
        break

cv2.destroyAllWindows()

# Print all boxes
print("\ncollision_boxes = {")
for box_name, details in collision_boxes.items():
    print(f"    \"{box_name}\": {details},")
print("}")

import cv2
import os
import numpy as np
import csv
from scipy.spatial import distance as dist

current_dir = os.path.dirname(os.path.abspath(__file__))
video_path = os.path.join(current_dir, 'input', 'simulation.mp4')

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)

fgbg = cv2.createBackgroundSubtractorMOG2()

cars_detected = {}
nextCarID = 0
max_frames_to_consider_lost = 15
max_frames_stationary = 30
grace_period = 5
all_detections_log = {}
collision_boxes = {
    # Updated with width and height for the box
    "straight_left": (302, 202, 20, 20),
    "straight_right": (615, 290, 35, 24),
    "straight_front": (567, 334, 41, 41),
    "straight_down": (271, 381, 40, 44),
    "right_down": (235, 185, 22, 18),
    "right_left": (551, 164, 30, 37),
    "right_front": (668, 342, 48, 37),
    "right_right": (188, 391, 34, 42),
    "left_left": (356, 390, 30, 35),
    "left_right": (473, 164, 22, 25),
    "left_front": (496, 375, 47, 56),
    "left_down": (692, 256, 38, 25),
}


def check_collision(car_bbox, collision_box):
    # Unpack the bounding box and collision box coordinates
    (x, y, w, h) = car_bbox
    (cx, cy, cw, ch) = collision_box

    # Check for overlap between the two boxes
    return not (x + w < cx or x > cx + cw or y + h < cy or y > cy + ch)


while True:
    ret, frame = cap.read()
    if not ret:
        break

    fgmask = fgbg.apply(frame)
    kernel = np.ones((5, 5), np.uint8)
    fgmask = cv2.dilate(fgmask, kernel, iterations=1)
    contours, _ = cv2.findContours(
        fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    current_centroids = []

    for contour in contours:
        if cv2.contourArea(contour) < 500:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        centroid = (int(x + w/2), int(y + h/2))
        current_centroids.append((centroid, (x, y, w, h)))

        for box_name, box in collision_boxes.items():
            cv2.rectangle(frame, box[:2], (box[0] +
                          box[2], box[1] + box[3]), (0, 0, 255), 2)

    if len(cars_detected) == 0 and current_centroids:
        for centroid, bbox in current_centroids:
            cars_detected[nextCarID] = {
                'centroid': centroid, 'frames_detected': 1, 'bbox': bbox, 'last_centroid': centroid, 'last_seen_frame': 0, 'stationary_frames': 0,
                'collision_statuses': {box_name: False for box_name in collision_boxes}
            }
            nextCarID += 1

    else:
        objectIDs = list(cars_detected.keys())
        previous_centroids = [cars_detected[objectID]
                              ['centroid'] for objectID in objectIDs]

        if previous_centroids and current_centroids:
            prev_centroids_array = np.array(previous_centroids).reshape(-1, 2)
            curr_centroids_array = np.array(
                [c[0] for c in current_centroids]).reshape(-1, 2)

            D = dist.cdist(prev_centroids_array, curr_centroids_array)

            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            usedRows = set()
            usedCols = set()

            for (row, col) in zip(rows, cols):
                if row in usedRows or col in usedCols:
                    continue

                objectID = objectIDs[row]
                new_centroid = current_centroids[col][0]
                distance_moved = dist.euclidean(
                    new_centroid, cars_detected[objectID]['last_centroid'])

                if distance_moved == 0:
                    cars_detected[objectID]['stationary_frames'] += 1
                else:
                    cars_detected[objectID]['centroid'] = new_centroid
                    cars_detected[objectID]['frames_detected'] += 1
                    cars_detected[objectID]['bbox'] = current_centroids[col][1]
                    cars_detected[objectID]['last_centroid'] = new_centroid
                    # Reset stationary frame count
                    cars_detected[objectID]['stationary_frames'] = 0

                # Reset last seen frame
                cars_detected[objectID]['last_seen_frame'] = 0

                usedRows.add(row)
                usedCols.add(col)

            unusedCols = set(range(0, D.shape[1])).difference(usedCols)
            for col in unusedCols:
                cars_detected[nextCarID] = {
                    'centroid': current_centroids[col][0],
                    'frames_detected': 1,
                    'bbox': current_centroids[col][1],
                    'last_centroid': current_centroids[col][0],
                    'last_seen_frame': 0,
                    'stationary_frames': 0
                }
                nextCarID += 1

            # Increase the last_seen_frame count for any undetected cars
            for objectID in objectIDs:
                if objectID not in usedRows:
                    cars_detected[objectID]['last_seen_frame'] += 1

    # Remove cars that have not been seen for a long time or have been stationary too long
    cars_to_remove = [objectID for objectID, car in cars_detected.items(
    ) if car['last_seen_frame'] > max_frames_to_consider_lost or car['stationary_frames'] > max_frames_stationary]

    # Update all_detections_log with the final detection statuses before removing the cars
    for objectID in cars_to_remove:
        car_info = cars_detected[objectID]
        all_detections_log[objectID] = {
            'frames_detected': car_info['frames_detected'],
            'collision_statuses': car_info['collision_statuses']
        }
        # Now remove the car from the active tracking dictionary
        del cars_detected[objectID]

    for objectID, car in cars_detected.items():
        car_bbox = car['bbox']
        # Ensure 'collision_statuses' is initialized
        if 'collision_statuses' not in car:
            car['collision_statuses'] = {
                box_name: False for box_name in collision_boxes}
        for box_name, collision_box in collision_boxes.items():
            if check_collision(car_bbox, collision_box):
                # Update collision status
                car['collision_statuses'][box_name] = True

        # Drawing and logging
        x, y, w, h = car_bbox
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = f"ID {objectID}"
        cv2.putText(frame, text, (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Optional: Immediate logging of collision status for debugging
        collision_statuses_str = ", ".join(
            [f"{box_name}={status}" for box_name, status in car['collision_statuses'].items()])
        print(
            f"Car {objectID}: bbox={car_bbox}, Collisions=({collision_statuses_str})")

    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

with open(os.path.join(current_dir, 'car_detections.csv'), mode='w', newline='') as file:
    writer = csv.writer(file)
    # Include headers for each collision box
    headers = [
        'CarID', 'Time Detected (seconds)'] + list(collision_boxes.keys())
    writer.writerow(headers)
    for carID, data in all_detections_log.items():
        time_detected_seconds = data['frames_detected'] / fps
        # Prepare a row with collision status for each box
        collision_status_values = [
            data['collision_statuses'][box_name] for box_name in collision_boxes.keys()]
        row = [carID, round(time_detected_seconds, 2)] + \
            collision_status_values
        writer.writerow(row)

import cv2
import time
from object_tracker import ObjectTracker
import os
from dotenv import load_dotenv

load_dotenv() 

START_POINT_X_LINE_1 = int(os.getenv('START_POINT_X_LINE_1'))
START_POINT_Y_LINE_1 = int(os.getenv('START_POINT_Y_LINE_1'))
START_POINT_X_LINE_2 = int(os.getenv('START_POINT_X_LINE_2'))
START_POINT_Y_LINE_2 = int(os.getenv('START_POINT_Y_LINE_2'))
Y_LINE_1 = int(os.getenv('Y_LINE_1'))
Y_LINE_2 = int(os.getenv('Y_LINE_2'))
OFFSET = int(os.getenv('OFFSET'))

VIDEO_PATH = os.getenv('VIDEO_PATH')
MODEL_PATH = os.getenv('MODEL_PATH')
CLASS_LIST_PATH = os.getenv('CLASS_LIST_PATH')
CLASS_TO_DETECT = os.getenv('CLASS_TO_DETECT') # e.g. "person" or "car"
DETECTED_OBJ_IMAGES_FOLDER = os.getenv('DETECTED_OBJ_IMAGES_FOLDER') # path to save detected object images

def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:  
        colorsBGR = [x, y]
        print(colorsBGR)

cv2.namedWindow('RGB')
cv2.setMouseCallback('RGB', RGB)

if not os.path.exists(DETECTED_OBJ_IMAGES_FOLDER):
    os.makedirs(DETECTED_OBJ_IMAGES_FOLDER)

def main():
    tracker = ObjectTracker(MODEL_PATH, CLASS_LIST_PATH, CLASS_TO_DETECT)

    objects_going_down = {}
    counter_down = []
    objects_going_up = {}
    counter_up = []

    cap = cv2.VideoCapture(VIDEO_PATH)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        tracked_objects = tracker.detect_and_track_objects(frame)

        for bbox in tracked_objects:
            x1, y1, w, h, obj_id = bbox
            x2, y2 = x1 + w, y1 + h
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
            cv2.putText(frame, str(obj_id), (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)

            # object going down, first goes beyond line 1 then line 2
            if Y_LINE_1 < (cy + OFFSET) and Y_LINE_1 > (cy - OFFSET):
                objects_going_down[obj_id] = time.time()
            if obj_id in objects_going_down and Y_LINE_2 < (cy + OFFSET) and Y_LINE_2 > (cy - OFFSET):
                if obj_id not in counter_down:
                    counter_down.append(obj_id)
                    # save the detected object image
                    object_img = frame[y1:y2, x1:x2]
                    timestamp = time.strftime('%Y%m%d-%H%M%S')
                    cv2.imwrite(f'detected_objects/object_{obj_id}_down_{timestamp}.jpg', object_img)

            # object going up, first goes beyond line 2 then line 1
            if Y_LINE_2 < (cy + OFFSET) and Y_LINE_2 > (cy - OFFSET):
                objects_going_up[obj_id] = time.time()
            if obj_id in objects_going_up and Y_LINE_1 < (cy + OFFSET) and Y_LINE_1 > (cy - OFFSET):
                if obj_id not in counter_up:
                    counter_up.append(obj_id)
                    # save the detected object image
                    object_img = frame[y1:y2, x1:x2]
                    timestamp = time.strftime('%Y%m%d-%H%M%S')
                    cv2.imwrite(f'detected_objects/object_{obj_id}_up_{timestamp}.jpg', object_img)

        cv2.line(frame, (START_POINT_X_LINE_1, Y_LINE_1), (START_POINT_Y_LINE_1, Y_LINE_1), (255, 255, 255), 1)
        cv2.putText(frame, 'L1', (START_POINT_X_LINE_1, Y_LINE_1-10), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
        cv2.line(frame, (START_POINT_X_LINE_2, Y_LINE_2), (START_POINT_Y_LINE_2, Y_LINE_2), (255, 255, 255), 1)
        cv2.putText(frame, 'L2', (START_POINT_X_LINE_2, Y_LINE_2-10), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

        count_down = len(counter_down)
        count_up = len(counter_up)
        cv2.putText(frame, f'going down: {count_down}', (60, 90), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(frame, f'going up: {count_up}', (60, 130), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

        cv2.imshow("RGB", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

import math
from collections import defaultdict
from ultralytics import YOLO
import pandas as pd

class ObjectTracker:
    def __init__(self, model_path, class_list_path, class_to_detect):
        self.model = YOLO(model_path)
        self.class_to_detect = class_to_detect
        self.center_points = {}
        self.id_count = 0
        with open(class_list_path, "r") as file: # read classes list from coco.txt
            self.class_list = file.read().split("\n")

    def detect_and_track_objects(self, frame):
        results = self.model.predict(frame)
        detections = results[0].boxes.data.cpu().numpy()
        px = pd.DataFrame(detections).astype("float")

        list_bbox = []
        for index, row in px.iterrows():
            x1, y1, x2, y2 = map(int, row[:4])
            class_id = int(row[5])
            class_name = self.class_list[class_id]
            if self.class_to_detect in class_name:
                list_bbox.append([x1, y1, x2 - x1, y2 - y1])  # convertion to width and height format (x, y, w, h)
        
        return self.update(list_bbox)

    def update(self, objects_rect):
        objects_bbs_ids = []

        # get center point of each detected object
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2

            # check whether that object was detected already
            same_object_detected = False
            for id, pt in self.center_points.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])

                if dist < 35:
                    self.center_points[id] = (cx, cy)
                    objects_bbs_ids.append([x, y, w, h, id])
                    same_object_detected = True
                    break

            # new object is detected, assign the ID to that object
            if not same_object_detected:
                self.center_points[self.id_count] = (cx, cy)
                objects_bbs_ids.append([x, y, w, h, self.id_count])
                self.id_count += 1

        # clean center points dictionary by removing IDS that are not used anymore
        new_center_points = {}
        for obj_bb_id in objects_bbs_ids:
            _, _, _, _, object_id = obj_bb_id
            center = self.center_points[object_id]
            new_center_points[object_id] = center

        # update dictionary without unused IDs
        self.center_points = new_center_points.copy()
        return objects_bbs_ids
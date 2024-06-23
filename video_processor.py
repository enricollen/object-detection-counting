import cv2

class VideoProcessor:
    def __init__(self, video_path, frame_width=540, frame_height=1150, skip_frames=2):
        self.cap = cv2.VideoCapture(video_path)
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.skip_frames = skip_frames
        self.frame_count = 0

    def read_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        self.frame_count += 1
        if self.frame_count % self.skip_frames != 0:
            return None
        frame = cv2.resize(frame, (self.frame_width, self.frame_height))
        return frame

    def release(self):
        self.cap.release()

    @staticmethod
    def show_frame(window_name, frame):
        cv2.imshow(window_name, frame)
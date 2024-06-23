import cv2

class VideoProcessor:
    def __init__(self, video_path, skip_frames=2):
        self.cap = cv2.VideoCapture(video_path)
        self.skip_frames = skip_frames
        self.frame_count = 0
        # Automatically determine video width and height
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def read_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        """
        # uncomment only to skip frames (reduce overhead)
        self.frame_count += 1
        if self.frame_count % self.skip_frames != 0:
            return None
        frame = cv2.resize(frame, (self.frame_width, self.frame_height))
        """

        return frame

    def release(self):
        self.cap.release()

    @staticmethod
    def show_frame(window_name, frame):
        cv2.imshow(window_name, frame)
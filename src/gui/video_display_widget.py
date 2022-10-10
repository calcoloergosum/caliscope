# At this point I can't even recall where I copied this code from, but it is what
# actually works and drives home to me that I need to develop a better understanding
# of threads, signals, slots, events, all that as it relates to GUI development

# Moving on to pythonguis.com tutorials for just that. But this code works...

import sys
from pathlib import Path
import time

import cv2

from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QPushButton,
                            QToolBar, QLabel, QLineEdit, QCheckBox, QScrollArea,
                            QVBoxLayout, QHBoxLayout, QGridLayout)

from PyQt6.QtMultimedia import QMediaPlayer, QMediaCaptureSession, QVideoFrame
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QImage, QPixmap


# Append main repo to top of path to allow import of backend
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.cameras.video_capture_widget import CameraCaptureWidget
from src.cameras.camera import Camera

class VideoDisplayWidget(QWidget):
    def __init__(self, camcap):
        super(VideoDisplayWidget, self).__init__()

        self.VBL = QVBoxLayout()
        self.HBL = QHBoxLayout()

        # FeedLabel 
        self.VideoScreen = QLabel()
        self.VBL.addWidget(self.VideoScreen)

        self.MediapipeToggle = QCheckBox("Show Mediapipe Overlay")
        self.MediapipeToggle.setCheckState(Qt.CheckState.Checked)
        self.MediapipeToggle.stateChanged.connect(self.toggle_mediapipe)
        self.HBL.addWidget(self.MediapipeToggle)

        self.rotate_ccw_btn = QPushButton("Rotate CCW")
        self.rotate_ccw_btn.clicked.connect(self.rotate_ccw)
        self.HBL.addWidget(self.rotate_ccw_btn)
    
        self.rotate_cw_btn = QPushButton("Rotate CW")
        self.rotate_cw_btn.clicked.connect(self.rotate_cw)
        self.HBL.addWidget(self.rotate_cw_btn)
        # self.VBL.addWidget(self.mediapipeLabel)

        self.setLayout(self.VBL)
        self.VBL.addLayout(self.HBL)

        self.vid_display = FrameEmitter(camcap)
        self.vid_display.start()
        self.vid_display.ImageUpdate.connect(self.ImageUpdateSlot)
        
    def rotate_ccw(self):
        # Clockwise rotation called because the display image is flipped
        self.vid_display.camcap.rotate_CW()

    def rotate_cw(self):
        # Counter Clockwise rotation called because the display image is flipped
        self.vid_display.camcap.rotate_CCW()
            
    def ImageUpdateSlot(self, Image):
        self.VideoScreen.setPixmap(QPixmap.fromImage(Image))
        # self.FeedLabel.setPixmap(Image)

    def CancelFeed(self):
        self.vid_display.stop()
        self.vid_cap_widget.capture.release()

    def toggle_mediapipe(self, s):
        print("Toggle Mediapipe")
        self.vid_display.camcap.toggle_mediapipe()


class FrameEmitter(QThread):
    """

    """
    ImageUpdate = pyqtSignal(QImage)

   
    def __init__(self, camcap):
        super(FrameEmitter,self).__init__()
        self.peak_fps_display = 10
        self.camcap = camcap

    def run(self):
        # self.camcap = CameraCaptureWidget(self.camcap) #, self.width ,self.height)
        self.ThreadActive = True
        self.height = self.camcap.cam.resolution[0]
        self.width = self.camcap.cam.resolution[1]

        while self.ThreadActive:
            try:    # takes a moment for capture widget to spin up...don't error out

                # Grab a frame from the capture widget and adjust it to 
                frame = self.camcap.frame
                fps = self.camcap.FPS_actual
                self.fps_text =  str(int(round(fps, 0))) 
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                FlippedImage = cv2.flip(Image, 1)

                # overlay frame rate
                cv2.putText(FlippedImage, "FPS:" + self.fps_text, (10, 70),cv2.FONT_HERSHEY_TRIPLEX, 2,(0,165,255), 2)

                qt_frame = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format.Format_RGB888)
                Pic = qt_frame.scaled(self.width, self.height, Qt.AspectRatioMode.KeepAspectRatio)
                self.ImageUpdate.emit(Pic)
                time.sleep(1/fps)
                # time.sleep(1/self.peak_fps_display)

            except AttributeError:
                pass
    def stop(self):
        self.ThreadActive = False
        self.quit()

if __name__ == "__main__":
    # create a camera widget to pull in a thread of frames
    # these are currently processed by mediapipe but don't have to be
    # capture_widget = VideoCaptureWidget(0,1080,640)

    cam = Camera(1)
    camcap = CameraCaptureWidget(cam)
    App = QApplication(sys.argv)
    display = VideoDisplayWidget(camcap)

    display.show()
    sys.exit(App.exec())
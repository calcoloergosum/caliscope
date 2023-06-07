import pyxy3d.logger

logger = pyxy3d.logger.get(__name__)
from time import sleep

import sys
from PyQt6.QtWidgets import QApplication
from pyxy3d.configurator import Configurator
from pathlib import Path
from pyxy3d import __root__
from pyxy3d.cameras.camera_array import CameraArray
from pyxy3d.recording.recorded_stream import RecordedStreamPool
from pyxy3d.cameras.synchronizer import Synchronizer
from pyxy3d.triangulate.sync_packet_triangulator import SyncPacketTriangulator
from pyxy3d.session.session import Session
from pyxy3d.gui.vizualize.playback_triangulation_widget import (
    PlaybackTriangulationWidget,
)
from pyxy3d.trackers.tracker_enum import TrackerEnum

# session_path = Path(__root__, "dev", "sample_sessions", "293")
# recording_path = Path(session_path, "recording_1")

# session_path = Path(__root__, "dev", "sample_sessions", "293")
session_path = Path(
    __root__,
    "dev",
    "sessions_copy_delete",
    "rain_day_test",
)


config = Configurator(session_path)
camera_array: CameraArray = config.get_camera_array()

tracker = TrackerEnum.HOLISTIC.value()


logger.info(f"Loading session {session_path}")
session = Session(config)

app = QApplication(sys.argv)
recording_path = Path(session_path, "recording_1")

xyz_history_path = Path(recording_path, tracker.name, f"xyz_{tracker.name}.csv")
vizr_dialog = PlaybackTriangulationWidget(camera_array, xyz_history_path)
vizr_dialog.show()

sys.exit(app.exec())
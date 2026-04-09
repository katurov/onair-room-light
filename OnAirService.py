# /// script
# dependencies = [
#   "requests",
#   "pyobjc-framework-AVFoundation",
#   "pyobjc-framework-CoreAudio",
#   "pyobjc-framework-CoreMediaIO",
#   "pyobjc-framework-Cocoa",
# ]
# ///

import AVFoundation
import CoreAudio
import CoreMediaIO
import struct
import json
import signal
import sys
import objc
import requests
import os
import logging
from Foundation import NSTimer, NSObject
from PyObjCTools import AppHelper

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("OnAirService")

INDICATOR_IP = "192.168.42.247"
INTERVAL = 8.0
PID_FILE = "/tmp/OnAirService.pid"

def check_pid():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            os.kill(pid, 0)
            logger.warning(f"Service is already running (PID: {pid}). Exiting.")
            sys.exit(1)
        except (ValueError, OSError, ProcessLookupError):
            try:
                os.remove(PID_FILE)
            except OSError:
                pass

    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

def cleanup():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

class OnAirMonitor(NSObject):
    def init(self):
        self = objc.super(OnAirMonitor, self).init()
        if self is None: return None
        
        self.audio_status = {}
        self.video_status = {}
        self.last_state = "Unknown"
        self.timer = None
        return self

    def start(self):
        logger.info(f"Starting OnAir Service (Interval: {INTERVAL}s)")
        self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            INTERVAL, self, "tick:", None, True
        )
        self.tick_(None)

    def tick_(self, timer):
        self.check_audio()
        self.check_video()
        status = self.get_current_status()
        
        # Логируем только изменение состояния
        if status != self.last_state:
            logger.info(f"Status changed: {self.last_state} -> {status if status else 'None'}")
            self.last_state = status
            
        self.send_indicator_signal(status)
        self.print_summary(status)

    def check_audio(self):
        try:
            session = AVFoundation.AVCaptureDeviceDiscoverySession.discoverySessionWithDeviceTypes_mediaType_position_(
                [AVFoundation.AVCaptureDeviceTypeBuiltInMicrophone, AVFoundation.AVCaptureDeviceTypeExternalUnknown],
                AVFoundation.AVMediaTypeAudio,
                AVFoundation.AVCaptureDevicePositionUnspecified
            )
            devices = session.devices()
        except Exception as e:
            logger.error(f"Failed to discovery audio devices: {e}")
            devices = []

        current_status = {}
        for mic in devices:
            d_id = mic.connectionID()
            is_active = False
            try:
                aopa = CoreAudio.AudioObjectPropertyAddress(
                    CoreAudio.kAudioDevicePropertyDeviceIsRunningSomewhere,
                    CoreAudio.kAudioObjectPropertyScopeGlobal,
                    CoreAudio.kAudioObjectPropertyElementMaster
                )
                response = CoreAudio.AudioObjectGetPropertyData(d_id, aopa, 0, [], 4, None)
                is_active = bool(struct.unpack('I', response[2])[0])
            except Exception:
                pass
            current_status[d_id] = {"Mic": mic.localizedName(), "Active": is_active}
        self.audio_status = current_status

    def check_video(self):
        device_types = [
            AVFoundation.AVCaptureDeviceTypeBuiltInWideAngleCamera,
            AVFoundation.AVCaptureDeviceTypeExternalUnknown
        ]
        try:
            device_types.append(AVFoundation.AVCaptureDeviceTypeContinuityCamera)
        except AttributeError:
            device_types.append("AVCaptureDeviceTypeContinuityCamera")

        try:
            session = AVFoundation.AVCaptureDeviceDiscoverySession.discoverySessionWithDeviceTypes_mediaType_position_(
                device_types,
                AVFoundation.AVMediaTypeVideo,
                AVFoundation.AVCaptureDevicePositionUnspecified
            )
            devices = session.devices()
        except Exception as e:
            logger.error(f"Failed to discovery video devices: {e}")
            devices = []

        current_status = {}
        for vid in devices:
            d_id = vid.connectionID()
            is_active = False
            try:
                vopa = CoreMediaIO.CMIOObjectPropertyAddress(
                    CoreMediaIO.kCMIODevicePropertyDeviceIsRunningSomewhere,
                    CoreMediaIO.kCMIOObjectPropertyScopeGlobal,
                    CoreMediaIO.kCMIOObjectPropertyElementMaster
                )
                response = CoreMediaIO.CMIOObjectGetPropertyData(d_id, vopa, 0, None, 4, None, None)
                is_active = bool(struct.unpack('I', response[3])[0])
            except Exception:
                pass
            current_status[d_id] = {"Cam": vid.localizedName(), "Active": is_active}
        self.video_status = current_status

    def get_current_status(self):
        if any(b['Active'] for b in self.video_status.values()):
            return "Green"
        if any(b['Active'] for b in self.audio_status.values()):
            return "Yellow"
        return None

    def send_indicator_signal(self, status):
        if status is None:
            return

        endpoint = "video" if status == "Green" else "air"
        url = f"http://{INDICATOR_IP}/{endpoint}"
        
        try:
            requests.get(url, timeout=4)
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not reach indicator at {url}: {e}")

    def print_summary(self, status):
        # Оставляем визуальный индикатор в одной строке для консоли
        sys.stdout.write(f"\rCurrent: {status if status else 'None'}    ")
        sys.stdout.flush()

def signal_handler(sig, frame):
    logger.info("Stopping OnAir service (Signal received)")
    cleanup()
    sys.exit(0)

if __name__ == "__main__":
    check_pid()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        monitor = OnAirMonitor.alloc().init()
        if monitor:
            monitor.start()
            AppHelper.runConsoleEventLoop()
        else:
            logger.error("Failed to initialize monitor object")
            cleanup()
    except Exception as e:
        logger.error(f"Fatal service error: {e}", exc_info=True)
        cleanup()

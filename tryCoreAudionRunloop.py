import AVFoundation
import CoreAudio
import CoreMediaIO
import struct
import json
import signal
import sys
import objc
from Foundation import NSTimer, NSObject
from PyObjCTools import AppHelper

class MicCamMonitor(NSObject):
    # Исправление 1: Правильная инициализация через objc.super
    def init(self):
        self = objc.super(MicCamMonitor, self).init()
        if self is None: return None
        
        self.audio_status = {}
        self.video_status = {}
        self.timer = None
        return self

    def start(self):
        print("Starting Service (Polling mode)...")
        # Исправление 2: Таймер запускается с интервалом 1.0 сек
        self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            8.0, self, "tick:", None, True
        )

    # Важно: сигнатура метода для таймера должна принимать один аргумент (timer)
    def tick_(self, timer):
        self.check_audio()
        self.check_video()
        self.print_summary()

    def check_audio(self):
        # Используем современный способ поиска устройств
        try:
            session = AVFoundation.AVCaptureDeviceDiscoverySession.discoverySessionWithDeviceTypes_mediaType_position_(
                [AVFoundation.AVCaptureDeviceTypeBuiltInMicrophone, AVFoundation.AVCaptureDeviceTypeExternalUnknown],
                AVFoundation.AVMediaTypeAudio,
                AVFoundation.AVCaptureDevicePositionUnspecified
            )
            devices = session.devices()
        except Exception:
            devices = []

        current_status = {}
        for mic in devices:
            d_id = mic.connectionID()
            is_active = False
            try:
                # Проверяем статус через CoreAudio
                aopa = CoreAudio.AudioObjectPropertyAddress(
                    CoreAudio.kAudioDevicePropertyDeviceIsRunningSomewhere,
                    CoreAudio.kAudioObjectPropertyScopeGlobal,
                    CoreAudio.kAudioObjectPropertyElementMaster
                )
                response = CoreAudio.AudioObjectGetPropertyData(d_id, aopa, 0, [], 4, None)
                is_active = bool(struct.unpack('I', response[2])[0])
            except Exception:
                pass
            
            # Сохраняем имя и статус
            current_status[d_id] = {"Mic": mic.localizedName(), "Active": is_active}
        
        self.audio_status = current_status

    def check_video(self):
        # Формируем список типов камер
        device_types = [
            AVFoundation.AVCaptureDeviceTypeBuiltInWideAngleCamera,
            AVFoundation.AVCaptureDeviceTypeExternalUnknown
        ]
        
        # Безопасное добавление ContinuityCamera (для iPhone)
        try:
            # Пытаемся взять константу, если она есть в версии PyObjC
            device_types.append(AVFoundation.AVCaptureDeviceTypeContinuityCamera)
        except AttributeError:
            # Если нет (старая версия), добавляем строку вручную
            device_types.append("AVCaptureDeviceTypeContinuityCamera")

        try:
            session = AVFoundation.AVCaptureDeviceDiscoverySession.discoverySessionWithDeviceTypes_mediaType_position_(
                device_types,
                AVFoundation.AVMediaTypeVideo,
                AVFoundation.AVCaptureDevicePositionUnspecified
            )
            devices = session.devices()
        except Exception:
            devices = []

        current_status = {}
        for vid in devices:
            d_id = vid.connectionID()
            is_active = False
            try:
                # Проверяем статус через CoreMediaIO
                vopa = CoreMediaIO.CMIOObjectPropertyAddress(
                    CoreMediaIO.kCMIODevicePropertyDeviceIsRunningSomewhere,
                    CoreMediaIO.kCMIOObjectPropertyScopeGlobal,
                    CoreMediaIO.kCMIOObjectPropertyElementMaster
                )
                # Читаем 4 байта (UInt32)
                response = CoreMediaIO.CMIOObjectGetPropertyData(d_id, vopa, 0, None, 4, None, None)
                is_active = bool(struct.unpack('I', response[3])[0])
            except Exception:
                pass

            current_status[d_id] = {"Cam": vid.localizedName(), "Active": is_active}
        
        self.video_status = current_status

    def print_summary(self):
        output = {
            "Audio": list(self.audio_status.values()),
            "Video": list(self.video_status.values())
        }
        # Вывод JSON в одну строку, чтобы не засорять консоль (опционально)
        print(json.dumps(output))
        
        if True in [b['Active'] for b in list(self.video_status.values())] :
            print("Green")
        elif True in [b['Active'] for b in list(self.audio_status.values())]:
            print("Yellow")
        else:
            print("None")


def signal_handler(sig, frame):
    print("\nStopping service...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    # Создаем и инициализируем монитор
    monitor = MicCamMonitor.alloc().init()
    if monitor:
        monitor.start()
        # Запускаем цикл событий
        AppHelper.runConsoleEventLoop()
    else:
        print("Failed to initialize monitor")
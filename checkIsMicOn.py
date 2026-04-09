#!/opt/homebrew/bin/python3.10
#
# Special thanks to guys in this post:
# 	https://stackoverflow.com/questions/39574616/how-to-detect-microphone-usage-on-os-x
#
# Also thanks to the documentaion:
# 	* This property shows that camera is in use: 
# 		https://developer.apple.com/documentation/coremediaio/kcmiodevicepropertydeviceisrunningsomewhere
#		it is much better than https://stackoverflow.com/questions/41512552/avcapturedevice-isinusebyanotherapplication-always-returns-false 
#		which always return "False" -- "I'm free to use" for camera
#	* Also this thread helps me to understand how cameras works on M1:
#		https://github.com/wouterdebie/onair/issues/3
#	* As soon as Camera in DAL device here is _models.py for it:
#		https://github.com/ronaldoussoren/pyobjc/blob/02ef37072ab0799e48f8d2dd7af5babe79614abf/pyobjc-framework-CoreMediaIO/Lib/CoreMediaIO/_metadata.py#L124
#		and this can help to understand how does it works. Look at this thread:
#		https://stackoverflow.com/questions/42681127/coremediaio-incorrectly-updated-properties-kcmiodevicepropertydeviceisrunningso?noredirect=1&lq=1
#		it can help to learn how to go to root loop (I didn't made yet)
#	* Sometimes the camera is used exclusively and only at this case this property is up:
#		https://developer.apple.com/documentation/avfoundation/avcapturedevice/1389512-isinusebyanotherapplication
#	* The description of AVCaptureDevice in OSX:
#		https://developer.apple.com/documentation/avfoundation/avcapturedevice
#
#
# NB: Here IS the problem that using this code in a loop will cause Exception or return
#	the same values disregard of the reality.
#	My using of this code is pretty simple: run it anytime I need (or use in a loop
#	inside my script using subprocessing - this is why I return JSON)
#
# Depends on: pip3.10 install pyobjc
#
# Here is a WARNING: AVCaptureDeviceTypeExternal is deprecated for Continuity Cameras.
#	Will work later to deal with it or never: https://forum.opencv.org/t/warning-deprecated-method-on-mac-os/16504/2
#

import AVFoundation
import CoreAudio
import CoreMediaIO
import struct
import json

mic_ids = {
	mic.connectionID(): mic
	for mic in AVFoundation.AVCaptureDevice.devicesWithMediaType_(
		AVFoundation.AVMediaTypeAudio
	)
}

vid_ids = {
	vid.connectionID(): vid
	for vid in AVFoundation.AVCaptureDevice.devicesWithMediaType_(
		AVFoundation.AVMediaTypeVideo
	)
}

vopa = CoreMediaIO.CMIOObjectPropertyAddress( 
	CoreMediaIO.kCMIODevicePropertyDeviceIsRunningSomewhere 
)

aopa = CoreAudio.AudioObjectPropertyAddress(
	CoreAudio.kAudioDevicePropertyDeviceIsRunningSomewhere,
	CoreAudio.kAudioObjectPropertyScopeGlobal,
	CoreAudio.kAudioObjectPropertyElementMaster
)

aresponse = []
vresponse = []
for mic_id in mic_ids:
	response = CoreAudio.AudioObjectGetPropertyData(mic_id, aopa, 0, [], 4, None)
	try :
		aresponse.append(
			{
				"Mic" : str(mic_ids[mic_id].localizedName()),
				"Active" : bool(struct.unpack('I', response[2])[0])
			}
		)
	except Exception as Err :
		aresponse.append(
			{
				"Mic" : str(mic_ids[mic_id].localizedName()),
				"Active" : None
			}
		)

for (did, cam) in vid_ids.items() :
	response = CoreMediaIO.CMIOObjectGetPropertyData( did, vopa, 0, None, 4, None, None )
	try :
		vresponse.append(
			{
				"Cam" : str(cam.localizedName()),
				"Active" : bool(struct.unpack('I', response[3])[0])
			}
		) 
	except Exception as Err :
		vresponse.append(
			{
				"Cam" : str(cam.localizedName()),
				"Active" : None
			}
		) 

print( json.dumps({ "Audio" : aresponse, "Video" : vresponse}, indent=4))
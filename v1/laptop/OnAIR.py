'''
This program designed as daemon for OSX (tested with macOS Catalina 10.15.6) works on: 
	- MacBook Air 13 mid 13

The main Idea is:
	IF camera OR microphone IS active THEN we have to turn led light "On AIR" ON
	ELSE turn led light "On AIR" OFF

This daemon paired with special ESP in this way:
	- microcontroller starts
	- mini-web-server started on microcontroller
	- THIS daemon sends on or off depends on state of mic and cam

PLEASE USE YOUR IP-ADDRESS in code instead of 192.168.0.42 or ESP module (or use "airscreen.local" instead)


This daemon paired with SLACK account, you should get own key for application, using
	this instruction: 	
		How to is here : https://github.com/witnessmenow/arduino-slack-api
		Codes are here : https://www.webfx.com/tools/emoji-cheat-sheet/
	Also you should put this key to: export SLKKEY="xoxp-............" and put it into ~/.bash_profile 

PLEASE USE YOUR gags in updateSlackStatus call, mine are funny for me personally (and are in Russian)

The Architecture is easy: daemon uses IOREG keys to find states of devices like cam and mics
'''
import 	subprocess
import 	threading
import 	requests
import 	os
from 	time 		import sleep, strftime

def getMicState():
	ioreg = subprocess.check_output( ['ioreg -r -w0 -c AppleHDAEngineInput'], stderr=subprocess.STDOUT, shell=True )
	lines = ioreg.decode().split("\n")
	for line in lines:
		if "IOAudioEngineState" in line :
			try :
				i = int(line[-1:])
				if i < 1 :
					return False
				else :
					return True
			except ValueError :
				return True
			except :
				return True

def getCamState():
	ioreg = subprocess.check_output( ['ioreg -r -w0 -c AppleCamIn'], stderr=subprocess.STDOUT, shell=True )
	lines = ioreg.decode().split("\n")
	for line in lines:
		if "CameraActive" in line :
			try :
				i = line.index("= ")
				i = i + 2

				YesOrNo = line[i:]

				if YesOrNo.startswith("Yes") :
					return True
				else :
					return False

			except ValueError:
				return True
			except :
				return True

def updateSlackStatus ( status_text, status_emoji ):
	API_URL = "https://slack.com/api/users.profile.set"
	HEADERS = {
		"Content-type" : "application/json; charset=utf-8",
		"Authorization": "Bearer {}".format(os.environ['SLKKEY'])
		}
	NWSTTSM = {
		"profile": {
			"status_text"	: status_text,
			"status_emoji"	: status_emoji
			}
		}

	try :
		rq = requests.post(API_URL, json=NWSTTSM, headers=HEADERS, timeout=3)
	except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as err:
		print( strftime('%Y-%m-%d %H:%M:%S'), "Got an SLACK error", err )
		pass

def updateLocalStatusBis ( busy = False, reason = "air") :
	try :
		if busy:
			resp = requests.get("http://192.168.0.42/{}".format(reason), timeout=2)
		else :
			resp = requests.get("http://192.168.0.42/vacant", timeout=2)
	except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as err:
		print( strftime('%Y-%m-%d %H:%M:%S'), "Got an error on connection", err )
		pass


if __name__ == '__main__':

	print("Daemon started")
	prev_state = [False, False]

	while True :
		micbusy = getMicState()
		cambusy = getCamState()

		if True in [micbusy, cambusy] :
			if micbusy and cambusy :
				b_thread = threading.Thread( target=updateLocalStatusBis, args=(True, "air") )
				s_thread = threading.Thread( target=updateSlackStatus, args=("Говорит и показывает в Москву", ":phone:") )
			elif cambusy :
				b_thread = threading.Thread( target=updateLocalStatusBis, args=(True, "video") )
				s_thread = threading.Thread( target=updateSlackStatus, args=("Камера, мотор!", ":phone:") )
			elif micbusy :
				b_thread = threading.Thread( target=updateLocalStatusBis, args=(True, "voice") )
				s_thread = threading.Thread( target=updateSlackStatus, args=("Говорит ротом", ":phone:") )
		else :
			b_thread = threading.Thread( target=updateLocalStatusBis, args=(False, None) )
			s_thread = threading.Thread( target=updateSlackStatus, args=("", "") )

		if prev_state != [micbusy, cambusy] :
			prev_state = [micbusy, cambusy]
			b_thread.start()
			s_thread.start()
		elif True in [micbusy, cambusy]:
			b_thread.start()


		sleep(7)

#
#
# WHAT by katurov@gmail.com for katurov@gmail.com

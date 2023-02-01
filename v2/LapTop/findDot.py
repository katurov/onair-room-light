from PIL 							import Image
from python_imagesearch.imagesearch import imagesearcharea
from time 							import sleep

import 	subprocess
import 	threading
import  sys

import 	pyscreenshot 				as ImageGrab
import 	requests


print("\"On Air\" version for Monterey M1 trying to start!\n\n")


def checkMicState () :
	points = [
		"a.png",
		"b.png",
		"c.png",
		"d.png"
	]

	im = ImageGrab.grab(bbox=(2700, 0, 2880, 50))
	for point in points :
		pos = imagesearcharea("reference/{}".format(point), 2700, 0, 2880, 50, im=im)
		if (pos[0] >= 0) :
			#print("Found, pattern '{}'".format(point))
			return True

	return False


def checkCamState():
	ioreg = subprocess.check_output( ['ioreg -r -w0 -c AppleH13CamIn'], stderr=subprocess.STDOUT, shell=True )
	lines = ioreg.decode().split("\n")
	for line in lines:
		if "FrontCameraActive" in line :
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


def processCheckState (  ) :
	global current_state

	while True :
		try :
			mic = checkMicState()
			cam = checkCamState()

			current_state = { "mic" : mic, "cam": cam} 
		except KeyboardInterrupt :
			break
		except Exception as e :
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print(exc_type, exc_tb.tb_lineno)

		sleep( 10 )

def processSendState (  ) :
	global current_state

	while True :
		try :
			if current_state["mic"] and current_state["cam"] :
				r = requests.get('http://airsign.local/video', timeout=4)
			elif current_state["mic"] :
				r = requests.get('http://airsign.local/air', timeout=4)
			else :
				pass
		except KeyboardInterrupt :
			break
		except Exception as e :
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print(exc_type, exc_tb.tb_lineno)

		print("\r{}                 ".format(current_state), end='')
		sleep( 7 )



current_state = { "mic" : False, "cam": False}

if __name__ == '__main__':
	try :
		c_thread = threading.Thread( target=processCheckState )
		s_thread = threading.Thread( target=processSendState )

		c_thread.start()
		sleep(0.5)
		s_thread.start()

		s_thread.join()
		c_thread.join()
	except KeyboardInterrupt :
		print("Exiting            ")
	except Exception as e :
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(exc_type, exc_tb.tb_lineno)


# WHAT
#
# by Paul A Katurov <katurov@gmail.com> for people
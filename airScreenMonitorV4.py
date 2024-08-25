from    time        import sleep
from    subprocess  import check_output
from    sys         import exc_info
from    requests    import get
from    json        import loads

def decodeResults ( jresults ) :
	vset = jresults.get('Video', [])
	if vset is not None :
		for v in vset :
			if v is not None :
				va = v.get("Active", False)
				if va :
					return "Green"

	mset = jresults.get('Audio', [])
	if mset is not None :
		for m in mset :
			if m is not None :
				ma = m.get("Active", False)
				if ma :
					return "Yellow"

	return None

if __name__ == '__main__':
	while True:
		try :
			ioreg = check_output( ['/Users/katurov/AirScreenMonV4/checkIsMicOn.py 2> /dev/null'],  shell=True )
			checkresult = ioreg.decode()
			jresult = loads( checkresult )

			color = decodeResults ( jresult )

			print( color, end="\r")

			if color is None :
				pass
			elif color == "Yellow" :
				r = get('http://192.168.0.140/air', timeout=4)
			elif color == "Green" :
				r = get('http://192.168.0.140/video', timeout=4)
			else :
				pass
			
			sleep(8)
		except Exception as e :
			exc_type, exc_obj, exc_tb = exc_info()
			print(exc_type, exc_tb.tb_lineno)
			break

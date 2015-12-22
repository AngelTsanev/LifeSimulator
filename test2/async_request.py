import urllib2
import threading


temp = 24
mutex = threading.Lock()

#class AHR(urllib2.HTTPHandler):
#	def http_response(self, reg, resp):
#	    global temp	    
#
#	    for l in resp:
#		temp = [int(s) for s in l.split() if s.isdigit()]
#	    global mutex
#
#	    mutex.acquire()
#	    temp = temp[0]
#	    mutex.release()
#
#	    return resp



#!/usr/bin/python

##
## The is a simple daemon app to
## collect temperatures from a single
## or multiple set of DS18B20 temperature
## sensors and put the value in a file 
## which will be read in by controller.py.
##
## This daemon will merge INFO/WARN messages
## into the garage_backend.log every 5 secs. 
##
##   SEE ALSO  /etc/systemd/system/garage_temp.service
##	This is the systemd config file for the service

from w1thermsensor import W1ThermSensor
import time, logging
from daemon import runner


class App():
	def __init__(self):
		self.stdin_path      = '/dev/null'
		self.stdout_path     = '/dev/null'
		self.stderr_path     = '/dev/null'
		self.pidfile_path    = '/tmp/garage_temp.pid'
		self.pidfile_timeout = 5
		
	def run(self):
	   while True:
		temps = []
		file = '/tmp/garage_temp'
		for sensor in W1ThermSensor.get_available_sensors():
			result = sensor.get_temperature(W1ThermSensor.DEGREES_C)
			temps.append(result)		

		if temps == []:
			Ctemp = 0.0
			f = open(file, 'w')
			f.write("%s\n" % (Ctemp))
			f.close()
			logger.warn("Did not report anything")
		else:
			Ctemp = float(sum(temps) / len(temps))
			f = open(file, 'w')
			f.write("%s\n" % (Ctemp))
			f.close()
			logger.info("Reported %s" % Ctemp)

		time.sleep(5)
		## TEMPLATE LOGGER MESSAGES
		##
		#logger.debug("Debug Message")
		#logger.info("Info Message")
		#logger.warn("Warning Message")
		#logger.error("Error Message")

app = App()
logger = logging.getLogger("Garage Temperature Log")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("/home/pi/garage_pi/instance/garage_backend.log")
#handler = logging.FileHandler("/home/pi/garage_pi/instance/garage_temp.log")
handler.setFormatter(formatter)
logger.addHandler(handler)

daemon_runner = runner.DaemonRunner(app)
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()

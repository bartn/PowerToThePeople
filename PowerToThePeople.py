#!/usr/bin/env python

from requests import get
from requests.exceptions import Timeout, ConnectionError
from time import time, strftime, asctime, sleep
from sys import stdout
from exceptions import KeyboardInterrupt
from subprocess import check_output

import RPi.GPIO as GPIO		#Raspberry Pi
import MySQLdb 				#Mysql connector

db = MySQLdb.connect(host="localhost", user="root", passwd="eindhoven", db="energylogging")

cursor = db.cursor()

try:
	from config import *
except ImportError:
	from defaults import *
	print 'Warning! copy defaults.py to config.py and edit that file!'


def _waitForLedFlash():
	while GPIO.input(ldr_gpio_pin) == GPIO.HIGH:	#Wait for a pin rising
		sleep(0.01) #minimal sleep
	sleep(0.25)	#debounce sleep
	while GPIO.input(ldr_gpio_pin) == GPIO.LOW:	#Make really really sure we get a LOW here
		sleep(0.01) #minimal sleep

def	main():

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(ldr_gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	_waitForLedFlash()	#Skip first led flash to get a proper duration for the first one we'll use

	lastPvOutputTime = lastLedFlashTime = time()	#first impression duration will be inaccurate
	energy = 0
	nLedFlashes = 0
	watt_data = []

	while True:
		_waitForLedFlash()

		now   = time()
		watt  = int(3600 / (now - lastLedFlashTime))
		current_usage = '%s : %4d Watt' % (asctime(), watt)
		lastLedFlashTime = now
		nLedFlashes += 1

		print current_usage 	#check if double prints

		if pvoutput_interval and now >= lastPvOutputTime + pvoutput_interval:
			interval     = now - lastPvOutputTime
			watt_average = nLedFlashes * 3600 / interval #different meter
		 	energy 		= nLedFlashes

		 	print 'Flashed %d' % nLedFlashes
			print 'interval %d' % interval
		 	print 'Watt Average %d' % watt_average
		 	print 'Energy used %d' % energy

		 	sql = "INSERT INTO logdata(wattaverage, energy) \
		 	       VALUES ('%s', '%s')" % \
		 	       (watt_average, energy)
		 	try:
		 	   # Execute the SQL command
		 	   cursor.execute(sql)
		 	   # Commit your changes in the database
		 	   db.commit()
		 	   
		 	except:
		 	   # Rollback in case there is any error
		 	   db.rollback()
		 	
			payload = {
				'key' : pvoutput_key,
				'sid' : pvoutput_sid,
				'd'   : strftime('%Y%m%d'),
				't'   : strftime('%H:%M'),
				'v3'  : energy,
				'v4'  : watt_average
				}
			try:
				get('http://pvoutput.org/service/r2/addstatus.jsp', params=payload, timeout=5.0)
			except ConnectionError:
				print 'Warning: pvoutput update failed'
			except Timeout:
				print 'Warning: pvoutput timed out'
			lastPvOutputTime = now
			nLedFlashes = 0

		stdout.flush()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print 'Interrupted by user'
	GPIO.cleanup()
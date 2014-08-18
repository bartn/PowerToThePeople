#!/usr/bin/env python

from requests import get
from requests.exceptions import Timeout, ConnectionError
from time import time, strftime, asctime, sleep
from sys import stdout
from exceptions import KeyboardInterrupt
from subprocess import check_output

import RPi.GPIO as GPIO		#Raspberry Pi

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
	sleep(0.25) #debounce sleep
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
		nu = strftime('%Y%m%d %H:%M')
		print 'flashed at %s' % nu

		stdout.flush()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print 'Interrupted by user'
	GPIO.cleanup()
#!/usr/bin/env python

from requests import get
from requests.exceptions import Timeout, ConnectionError
from time import time, strftime, asctime, sleep
from sys import stdout
from exceptions import KeyboardInterrupt
from subprocess import check_output
import spidev
import os
import RPi.GPIO as GPIO		#Raspberry Pi

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)

# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data

# Function to convert data to voltage level,
# rounded to specified number of decimal places. 
def ConvertVolts(data,places):
  volts = (data * 3.3) / float(1023)
  volts = round(volts,places)  
  return volts
  
# Function to calculate temperature from
# TMP36 data, rounded to specified
# number of decimal places.
def ConvertTemp(data,places):
  temp = ((data * 330)/float(1023))-50
  temp = round(temp,places)
  return temp

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
		watt  = int((3600 / (now - lastLedFlashTime)))
		lastLedFlashTime = now
		nLedFlashes += 1

		


		if pvoutput_interval and now >= lastPvOutputTime + pvoutput_interval:
			interval     = now - lastPvOutputTime
			watt_average = nLedFlashes * 3600 / interval #different meter
		 	energy 		= nLedFlashes 
			temp_level = ReadChannel(temp_channel)
	  		temp       = ConvertTemp(temp_level,1)
		 	print 'Flashed: %d' % nLedFlashes
			print 'Interval: %d' % interval
		 	print 'Watt Average: %d' % watt_average
		 	print 'Current temperature %d' % temp
		 	
			payload = {
				'key' : pvoutput_key,
				'sid' : pvoutput_sid,
				'd'   : strftime('%Y%m%d'),
				't'   : strftime('%H:%M'),
				#'v3'  : energy,
				'v4'  : watt_average, 
				'v5'  : temp
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
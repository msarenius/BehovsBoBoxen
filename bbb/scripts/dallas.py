#!/usr/bin/python
#2016-02-07:17.33
import datetime
import time
import sqlite3

import subprocess
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(11,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(15,GPIO.OUT)
GPIO.setup(29,GPIO.OUT)
GPIO.setup(31,GPIO.OUT)
GPIO.setup(33,GPIO.OUT)
GPIO.setup(35,GPIO.OUT)
GPIO.setup(37,GPIO.OUT)
GPIO.setup(12,GPIO.OUT)
GPIO.setup(16,GPIO.OUT)
GPIO.setup(18,GPIO.OUT)
GPIO.setup(22,GPIO.OUT)
GPIO.setup(32,GPIO.OUT)
GPIO.setup(36,GPIO.OUT)
GPIO.setup(38,GPIO.OUT)
GPIO.setup(40,GPIO.OUT)
#GPIO general purpose input output

sensors = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
#master in raspberrypi ask these sensors (slaves)
setpoints = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
#nr of rooms holding the setpoint values we want
actualTemp = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
#the value we have
pins = [11,13,15,29,31,33,35,37,12,16,18,22,32,36,38,40]
#may be programmed for input or output

#read dallasgivare
path1="/sys/bus/w1/devices/w1_bus_master1/w1_master_slaves"
i=0
tfile=open (path1,'r')

for line in tfile:
  dallas=line[0:15]
  sensors[i] = dallas
  #print sensors[i] 
  i=i+1
tfile.close()

def initiate(setpoints, actualTemp, sensors):
	setpoints = setPoints(setpoints) 
	# we fill the array (rooms) with actual setpointvalues for each room in the function setPoints
	actualTemp = actualTemps(actualTemp, sensors)
	updateTempFile(actualTemp)
	#print "setpoints:", setpoints, "/actuals:", actualTemp

def setPoints(setpoints):
	setpoint=0

	# Creates or opens a file called mydb with a SQLite3 DB
	db = sqlite3.connect('/var/www/html/application/data/.ht.sqlite3')
	cursor = db.cursor()
	cursor.execute("SELECT * FROM roomsettings")
	all_rows = cursor.fetchall()
	i=0

	for row in all_rows:
		#row[0] returns the first column in the query (rowid), row[2] returns setvalue.
		setpoints[i] = row[2]
		i = i +1
	db.close()
	return setpoints

def actualTemps(actualTemp, sensors):
	basePath="/sys/bus/w1/devices/"
	tailPath="/w1_slave"
	
	i = 0
	while i < 8:
		string = str(sensors[i])
		searchPath = basePath + string + tailPath
		tfile = open(searchPath)
		text = tfile.read()
		tfile.close()
		secondline = text.split("\n")[1]
		temperaturedata = secondline.split(" ")[9]
		temperature = float(temperaturedata[2:])
		temperature = temperature / 1000
		actualTemp[i] = (round(temperature,1))		
		#print actualTemp[i]
		i = i + 1
	return actualTemp


#read actual time and date, removes microseconds
def getdate():
    date = datetime.datetime.now()
    return(unicode(date.replace(microsecond=0)))
	
def updateTempFile(actualTemp):
	file = open("/var/www/html/application/textfile/temperature.txt", "w") 
	file.write(getdate()) 
	file.write("; ") 
	file.write('; '.join(map(str, actualTemp)))	
	file.close

def main():

    while 1 > 0:            
	initiate(setpoints, actualTemp, sensors)
	actualtime=datetime.datetime.now()#get time
	actualhour=actualtime.hour#get hour


	#get setpoints
	x = 0
	while x < 8:
		room = "room" + str(x)
		string = "/var/www/html/application/textfile/" + room + ".txt"
		room = open(string, "r")
		setpoints[x]=float(room.read().split(',')[actualhour])
		room.close()
		#end get setpoint 
	    	if actualTemp[x] > setpoints[x]: GPIO.output(pins[x],True)
	    	if actualTemp[x] < setpoints[x]: GPIO.output(pins[x],False)
		x = x + 1
		
    #print getdate(), 'Actual temp=',temp1, 'Setpoint=' ,setpoints[1] #temp2,temp3,temp4,temp5,temp6,temp7,temp8
	time.sleep(10) #vanta i 297s(ca 5min)
main();

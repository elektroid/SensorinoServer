import sys
from serial import Serial




linuxPossibleSerialPorts=['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2',
			'/dev/ttyUSB0','/dev/ttyUSB1','/dev/ttyUSB2','/dev/ttyUSB3',
			'/dev/ttyS0','/dev/ttyS1',
			'/dev/ttyS2','/dev/ttyS3'] # TODO : complete list

windowsPossibleSerialPorts=['COM1', 'COM2', 'COM3', 'COM4'] # TODO : complete list

arduino=None

for device in linuxPossibleSerialPorts:

	try:
		arduino = Serial(device, 9600) 
	except:
		print("arduino not on "+device);
	if (arduino!=None):
		print ("found arduino on "+device)
		break

if (arduino==None):
	print("Unable to find arduino\n")
	toto=1
	

while True:
	print(arduino.readline())


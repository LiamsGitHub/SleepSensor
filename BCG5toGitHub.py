# BCG version 5
# Reads Murata SCA10H data through UART port, splits parameters and saves
# Liam Goudge. 24th Mar 2018
# Raspberry PI version. Output saved to DropBox. Time and Date related filename

import serial
import datetime
import time
import dropbox
import re
import numpy as np # required for SD calc
import sys

duration = 3600 * 7 # set for number of seconds to scan (7 hours here)
dbtoken = 'you need a DropBox Developer account and key for this';

fnamebase = '/home/pi/python/'

# Generate a data filename based on the time and date
t = datetime.datetime.now()

year = str(t.year)
month = str(t.month)
day = str(t.day)
hour = str(t.hour)
min = str(t.minute)

filename1 = fnamebase + 'sleepdat' + year + month.zfill(2) + day.zfill(2) + "start" + hour.zfill(2) + 'h' + min.zfill(2) + '.txt'
filename2 = fnamebase + 'log' + year + month.zfill(2) + day.zfill(2) + "start" + hour.zfill(2) + 'h' + min.zfill(2) + '.txt'

fhandle = open (filename1,'w')
flog = open (filename2,'w')

flog.write(filename1 + '\n')
flog.write('Current time: ' + str(t) + '\n')
print ('Starting time: ' + str(t) + '\n')

fhandle.write(str(t) + '\n' )
fhandle.write('count, heart rate, hrv, resp rate, signal, status \n')

# Set up the UART serial port to talk to the Murata BCG

ser = serial.Serial(
    port='/dev/ttyUSB0',\
    baudrate=230400,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)

ser.flushInput()
ser.flushOutput()

flog.write("connected to: " + ser.portstr + '\n')

# Now start data collection

frame = list()
count=0


while (count<duration):
    for line in ser.read(1):
    	hexval = line.encode('hex')
    	
    	if hexval == 'fe':
		# 0xFE is the header for a new data frame
    		#print "----------- Start frame -------------"
    		# this all works on the prior frame that will be deleted after printing
    		
    		# Process heart rate field
    	
    		heartrate = frame[9:13]
    		heartrate.reverse()
    		heart = ''.join(heartrate)
    		
    		if (heart == '00000000') or (heart == ''):
    			heartint=int(0)
    			
    		else:
    			heartint=int(heart,16)
    			
    		
    		# Process respiration rate field
    		
    		resprate = frame[13:17]
    		resprate.reverse()
    		resp = ''.join(resprate)
    		
    		if (resp == '00000000') or (resp == ''):
    			respint=int(0)
    			
    		else:
    			respint=int(resp,16)
	
    		
    		# Process other fields
    		
    		sv = frame[17:21]
    		hrv = frame[21:25]
    		hrv.reverse()
		hrvval=''.join(hrv)
		if (hrvval=='00000000') or (hrvval==''):
			hrvint=int(0)
		else:
			hrvint=int(hrvval,16)
		    		
    		
    		# Process signal strength
    		
    		sigstr = frame [25:29]
    		sigstr.reverse()
    		sig = ''.join(sigstr)
    		
    		if (sig == '00000000') or (sig == ''):
    			sigint=int(0)
    			
    		else:
    			sigint=int(sig,16)
    		
    		
    		# Process other fields
    		
    		status = frame [29:33]
    		status.reverse()
		statval = ''.join(status)
		if (statval=='00000000') or (statval == ''):
			statint=int(0)
		else:
			statint=int(statval,16)

    		
    		b2b = frame [33:37]
    		b2b1 = frame [37:41]
    		b2b2 = frame [ 41:45]
    		
    		
    		del frame[:]
    		count = count +1
    		flog.write('Count: ' + str(count) + '\n')
    		
    		fhandle.write(str(count) + ',' + str(heartint) + ',' + str(hrvint) + ',' + str(respint) + ',' +  str(statint) + ',' + str(sigint) + '\n')
    		
    	frame.append(hexval)

ser.close()
fhandle.close()

# Now post-process the data
# Parses sleep data from SCA10H
# Looks for outliers on heart rate and sleep activity.


# Finally upload the results to DropBox
#client = dropbox.client.DropboxClient(dbtoken);
client = dropbox.Dropbox(dbtoken)

f = open(filename1, 'rb');
data = f.read()
#response = client.put_files(filename1, f);
response = client.files_upload(data,filename1)
f.close()

f = open(filename2, 'rb');
data = f.read()
#response = client.put_file(filename2, f);
response = client.files_upload(data,filename2)
f.close()

exit()






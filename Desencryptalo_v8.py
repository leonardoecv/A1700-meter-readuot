#! python
# Script to implement readout of measurements data from ABB ELSTER A1700 power meter
# for comunication with meter I'm using and USB Serial optical probe: 
# http://www.ebay.co.uk/itm/Optical-Probe-IEC1107-IEC61107-62056-21-with-USB-cable-Windows-10-version-/202031866928?
# the decryptA1700 function is based on the work done by the cool people from Gurux Community
# check it out at: http://www.gurux.fi/comment/9495

import serial
import time
import binascii
import datetime


s = None
# Uncomment password to use in decryptA1700 function:
# password = bytearray(b'\x2d\x2d\x2d\x2d\x2d\x2d\x2d\x2d')          #default password: --------
password = bytearray(b'\x30\x30\x30\x30\x30\x30\x30\x30')         #default password:  00000000
# password = bytearray(b'\x30\x30\x30\x31\x61\x62\x63\x64')         #default password level 1 0001ABDC
# password = bytearray(b'\x61\x62\x63\x64\x30\x30\x30\x32')         #default password level 2 ABCD0002
# password = bytearray(b'\x66\x65\x64\x63\x30\x30\x30\x33')         #default password level 3 FEDC0003

def open():
    global s
    
    #to_do: auto detect so and port configuration 
    
    s = serial.Serial()
    # s.port = "/dev/ttyS3"
    s.port = "COM4"
    s.baudrate = 300
    s.bytesize = serial.SEVENBITS           #number of bits per bytes
    s.parity = serial.PARITY_EVEN           #set parity check: EVEN
    s.stopbits = serial.STOPBITS_ONE        #number of stop bits
    s.timeout = 1.5                         #non-block read
    s.xonxoff = False                       #disable software flow control
    s.rtscts = False                        #disable hardware (RTS/CTS) 
    try: 
        s.open()
        print ('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + '   ###   :' + 'Begining communication')
    except Exception as e:
        print ("Error atemping to open serial port: " + str(e))
        exit()    
        
def getLine():          #Gets serial data from port and return it as a single line
    res = []
    while True:
        c = s.read()
        if not c: break
        res.append(c)
    res = b''.join(res)
    print('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + '   <<<   : ' + res.decode('utf-8'))
    return res
 
def getId():
    mensaje = bytearray(b'\x2F\x3F\x21\x0D\x0A')    #Sends command: /?!<CR><LF> to begin communication
    s.write(mensaje)                                #expets ID message from metter  
    print('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + '   >>>   : ' + mensaje.decode('utf-8'))
    return getLine()                                #and returns it

def modeSwitchRequest():
    mensaje = bytearray(b'\x06\x30\x35\x31\x0D')    #Sends command:
    s.write(mensaje)
    s.write(b'\x0A')
    time.sleep(0.2)     #Waits to send the whole message before changing port setup.
    s.baudrate = 9600
    return getLine()


def decryptA1700(seed, password):
    crypted = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')
    byte_mask = int('11111111', 2)
    for i in range (0, 8):
        crypted[i]= password[i] ^ seed[i]
    last = crypted[7]
    for i in range (0, 8):
        crypted[i] = (crypted[i] + last) & byte_mask  
        last = crypted[i]
    crypted = binascii.hexlify(crypted)
    return crypted

open()
identidad = getId()
if identidad:
    semilla = modeSwitchRequest()
    seed=bytearray()
    for i in range (0, 5):
        if semilla[i] == b'\x28': break
    for count in range (1,17):
        seed.append(semilla[i+count]) 
    seed = binascii.unhexlify(seed)
    mensaje = bytearray(b'\x01\x50\x32\x02\x28')
    mensaje.extend(decryptA1700(semilla, password))
    mensaje.extend(b'\x29\x03\x60\x0D\x0A')
    print('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + '   >>>   : ' + mensaje.decode('utf-8'))
    s.write(mensaje)
    response = getLine()
    for i in range (0, len(response)):
        if response[i] == b'\x06': 
            print("Yes!! it Acknowledged it baby, now it should be a piece of cake")
            break
            
    s.write(b'\x01\x42\x30\x03\x71')            #Ends communication with meter

s.close()


 

 

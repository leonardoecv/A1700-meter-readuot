#! python3
# A1700.

import serial
import time
import binascii

s = None

def open():
    global s
    s = serial.Serial()
    # s.port = "/dev/ttyS3"
    s.port = "COM4"
    s.baudrate = 300
    s.bytesize = serial.SEVENBITS #number of bits per bytes
    s.parity = serial.PARITY_EVEN #set parity check: EVEN
    s.stopbits = serial.STOPBITS_ONE #number of stop bits
    s.timeout = 1.5            #non-block read
    s.xonxoff = False     #disable software flow control
    s.rtscts = False     #disable hardware (RTS/CTS) 
    try: 
        s.open()
    except Exception as e:
        print ("Error atemping to open serial port: " + str(e))
        exit()    
        
def getLine():
    res = []
    while True:
        c = s.read()
        if not c: break
        res.append(c)
    return b''.join(res)
 
def getId():
    mensaje = bytearray(b'\x2F\x3F\x21\x0D\x0A')
    s.write(mensaje) 
    return getLine()
    
def modeSwitchRequest():
    mensaje = bytearray(b'\x06\x30\x35\x31\x0D')
    s.write(mensaje)
    s.write(b'\x0A')
    time.sleep(0.2)     #Espera para enviar el mensaje completo antes de cambiar configuracion del puerto
    s.baudrate = 9600
    return getLine()


def handShake(seed):
    password = bytearray(b'\x2d\x2d\x2d\x2d\x2d\x2d\x2d\x2d')         #contraseña --------
    # password = bytearray(b'\x30\x30\x30\x30\x30\x30\x30\x30')         #contraseña 00000000
    # password = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')         #contraseña 00000000
    # password = bytearray(b'\x30\x30\x30\x31\x61\x62\x63\x64')         #contraseña nivel 1 0001abcd
    # password = bytearray(b'\x61\x62\x63\x64\x30\x30\x30\x32')         #contraseña nivel 2 ABCD0002
    # password = bytearray(b'\x66\x65\x64\x63\x30\x30\x30\x33')         #contraseña nivel 3 FEDC0003
    password = bytearray(b'\x30\x31\x32\x31\x31\x37\x39\x33')
    crypted = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')
    # seed = b'\xFD\x2B\xA0\xE2\x97\x31\xD2\x30'
    print(seed)
    byte_mask = int('11111111', 2)
    for i in range (0, 8):
        crypted[i]= password[i] ^ seed[i]
    last = crypted[7]
    for i in range (0, 8):
        crypted[i] = (crypted[i] + last) & byte_mask  
        last = crypted[i]
    print(crypted)
    crypted = binascii.hexlify(crypted)
    return crypted

def invierte_byte(origen, destino = bytearray()):
    for  i in range (7, -1, -1): destino.append(origen[i])
    return destino
  
    
open()
identidad = getId()
if identidad:
    print(identidad)
    semilla = modeSwitchRequest()
    seed=bytearray()
    for i in range (0, 5):
        if semilla[i] == b'\x28': break
    for count in range (1,17):
        seed.append(semilla[i+count])
    # print(seed)    
    seed = binascii.unhexlify(seed)
    # print(seed)
    mensaje = bytearray(b'\x01\x50\x32\x02\x28')
    mensaje.extend(handShake(semilla))
    mensaje.extend(b'\x29\x03\x60\x0D\x0A')
    print(b'>>>' + mensaje)
    s.write(mensaje)
    print(getLine())
    s.write(b'\x01\x42\x30\x03\x71')            #Ends communication with meter

s.close()


 

 

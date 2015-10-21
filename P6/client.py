#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys

if len(sys.argv) != 3:
    sys.exit('Usage: python client.py method receiver@IP:SIPport')

METHOD = sys.argv[1]
DOMINIO = sys.argv[2].split('@')[0]
SERVER = sys.argv[2].split('@')[1].split(':')[0]
PORT = int(sys.argv[2].split('@')[1].split(':')[1])

my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((SERVER, PORT))

if METHOD == 'INVITE':
    line = 'INVITE sip:' + sys.argv[2].split(':')[0] + ' ' + 'SIP/2.0\r\n\r\n'
    print "Enviando: " + line
    my_socket.send(line)
    try:
        data = my_socket.recv(1024)
    except socket.error:
        sys.exit('Error: No server listening at ' + SERVER + 'port' + PORT)
    print 'Recibido -- ', data
    d_list = data.split()
    if d_list[2] == 'Trying' and d_list[5] == 'Ringing' and d_list[8] == 'OK':
        line = 'ACK sip:' + sys.argv[2].split(':')[0] + ' ' + 'SIP/2.0\r\n\r\n'
        print "Enviando: " + line
        my_socket.send(line)
        print "Terminando socket..."
        my_socket.close()
        print "Fin."
elif METHOD == 'BYE':
    line = 'BYE sip:' + sys.argv[2].split(':')[0] + ' ' + 'SIP/2.0\r\n\r\n'
    print "Enviando: " + line
    my_socket.send(line)
    data = my_socket.recv(1024)
    print 'Recibido -- ', data
    if data == 'SIP/2.0 200 OK\r\n\r\n':
        print "Terminando socket..."
        my_socket.close()
        print "Fin."
else:
    exit('EL MÉTODO ES INCORRECTO. INVITE O BYE')

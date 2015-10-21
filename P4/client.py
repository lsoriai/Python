#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys

# Cliente UDP simple.

# Dirección IP del servidor.
if len(sys.argv) != 6:
    sys.exit("Usage: client.py ip puerto register sip_address expires_value")

SERVER = sys.argv[1]
PORT = int(sys.argv[2])
REGISTER = sys.argv[4]
EXPIRES = sys.argv[5]


# Contenido que vamos a enviar
#LINE = ' '.join(sys.argv[3:])

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((SERVER, PORT))

#print "Enviando: " + LINE
#my_socket.send(LINE + '\r\n')

my_socket.send("REGISTER " + "sip:" + REGISTER + " SIP/2.0\r\n" + "Expires: " +
               EXPIRES + "\r\n\r\n")

data = my_socket.recv(1024)

print 'Recibido -- ', data
print "Terminando socket..."

# Cerramos todo
my_socket.close()
print "Fin."

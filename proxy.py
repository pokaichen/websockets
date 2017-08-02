# This script converts between websockets and udp.
# This is so the websockets JS monitor can talk with the UDP stat monitor.

# ws
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer
import SocketServer

# udp
import socket
import sys
from threading import Thread
import time

STAT_MON_PORT = 6000
PORT_RX = 6004
PORT_WS = 443
sys_ip = '127.0.0.1'

DEVEL_MODE=False
try:
  import subprocess32
except:
  DEVEL_MODE = True
  sys_ip = '172.17.10.120'
print "Devel mode: ", DEVEL_MODE, " Connecting to sys: ", sys_ip, PORT_RX, " ws port: ", PORT_WS

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (sys_ip, STAT_MON_PORT) # send UDP
sock.bind(('', PORT_RX)) # receive UDP

clients = []
UDP_MAX = 65535

def threaded_function():
  while True:
    time.sleep(.001)
    data, address = sock.recvfrom(UDP_MAX) # receive UDP
#    print "receive from udp ", len(data), len(clients), address, "send to: ", clients[0].address
    for i in xrange(len(clients)):
      clients[i].sendMessage(data)

thread = Thread(target = threaded_function, args = ())
thread.daemon = True
thread.start()

class SimpleEcho(WebSocket):

    def handleMessage(self):
        print "receive from ws:", len(self.data)
        # echo message back to client
        #self.sendMessage(self.data)
        sock.sendto(self.data, server_address) # send UDP

    def handleConnected(self):
        print self.address, 'connected'
        clients.append(self)

    def handleClose(self):
        if len(clients):
          clients.pop(0)
        print self.address, 'closed'

server = SimpleWebSocketServer('', PORT_WS, SimpleEcho, 0.001)

def action(a):
  print a

SocketServer.TCPServer.allow_reuse_address = True # avoids '[Errno 98] Address already in use'
try:
  server.serveforever(lambda(a) : action(a))
except KeyboardInterrupt:
  print '^C received, shutting down the WS server'
  server.close()
  sys.exit(0)

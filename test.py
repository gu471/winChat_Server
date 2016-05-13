import socket
import sys
from thread import start_new_thread
from chatClasses import tcpHandler
import time

import curses

screen = curses.initscr()
screen.immedok(True)
curses.noecho()
curses.curs_set(0)
curses.cbreak()
screen.keypad(1)

listenerPort = 5006
promoterPort = 5005
server_address = "127.0.0.1"

log2Write = []
Xmessages = []

debug = 80

tosend = ""

closing = False
sending = False

listenerConnection = None
promoterConnection = None

uuid = ""

def handleData(data):
	log(data, 20)

	return

def log(logMsg, verbosity = 0):
	global log2Write
	
	if (verbosity < debug):
		log2Write.append("[" + str(verbosity) + "]: " + logMsg)
	#sys.stdout.flush()

def connectSocket(_type, server_address, port):
	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
	# Connect to server
	try:
		sock.connect((server_address, port))
		log("starting up on %s port %s _ " % sock.getsockname() + _type)
	except socket.error, msg:
		log(_type + " : Connect Failed. Error Code: {} Error: {}".format(str(msg[0]), msg[1]))
		sys.exit()

	return sock

def startListener(address, port):
	log("startung listener", 50)
	connection = connectSocket("listener", address, port)
	tcp = tcpHandler(connection)
	
	global listenerConnection
	global uuid
	listenerConnection = connection
	
	data = str(uuid)
	tcp.write(data)

	while True:
		try:
			data, length = tcp.listen()
			
			log(address + ": '%s'" % data, 10)
			if data:
				handleData(data)
			else:
				log(address + ": connection closed _ listener", 5)
				break
		except socket.error, msg:
			log(address + ": '%s'" % msg + " _ listener", 4)
			break


def startPromoter(address, port):
	global sending
	global tosend
	global uuid
	
	connection = connectSocket("promoter", address, port)
	tcp = tcpHandler(connection)
	
	global promoterConnection
	promoterConnection = connection
	
	uuid, length = tcp.listen()
	log(str(uuid) + " | " + str(length))

	while True:
		if sending:
			log("want to send: " + tosend)
			log(tcp.write(tosend), 60)
			
			tosend = ""
			sending = False

def printScreen():
	global tosend
	global screen
	global log2Write
	
	empty = ""
	for i in range(1,79):
		empty += " "	
	
	lastLength = 0
	lastToSendLength = 0
	
	screen.clear()
	box1 = curses.newwin(22, 80, 0, 0)
	box1.box()    
	box1.refresh()
		
	box2 = curses.newwin(3, 80, 23, 0)
	box2.box()    
	box2.refresh()	
				
	while True:
		logLength = len(log2Write)
		tempWrite = log2Write
		
		if logLength > lastLength:
			#print >>sys.stderr, log2Write.pop(0)
			#screen.erase()
			
			if logLength < 20:
				maxim = logLength
			else:
				maxim = 20
						
			i = 0
			while i < maxim:
				box1.addstr(i+1, 1, empty)	
				box1.addstr(i+1, 1, tempWrite[logLength - i - 1])
				i += 1
			
			lastLength = logLength
			
			box1.refresh()
			#screen.refresh()
		
		lengthToSend = len(tosend)
		if lengthToSend <> lastToSendLength:
			lastToSendLength = lengthToSend
			
			screen.addstr(24, 1, empty)			
			screen.addstr(24, 1, tosend)
			box2.refresh()
		
		#screen.refresh()

def checkKeyboard():
	global tosend
	global closing
	global sending
	global screen
	
	key = ''
	while not closing:
		key = screen.getch()
		if key == curses.KEY_END:
			closing = True
		elif key == ord('\n'):
			sending = True
		elif key == curses.KEY_BACKSPACE:
			tosend = tosend[:-1]		
		elif key <= 256:
			tosend += chr(key)

def Main():
	global closing
	global tosend
	global uuid
	
	start_new_thread(printScreen, ())
	start_new_thread(checkKeyboard, ())
	
	start_new_thread(startPromoter, (server_address, promoterPort,))
	
	while uuid == "":
		pass

	log(str(uuid), 50)
	log("prepare listener start", 50)
	start_new_thread(startListener, (server_address, listenerPort,))
	#time.sleep(1)
	
	
	while not closing:
		pass
	
	time.sleep(1)
	listenerConnection.close()
	promoterConnection.close()
	curses.endwin()
	print tosend
	#listeningConnection.close()
	#promotingConnection.close()


Main()

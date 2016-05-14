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

chat2Write = []
log2Write = []
Xmessages = []

debug = 80

tosend = ""

closing = False
sending = False
disconnecting = False

listenerConnection = None
promoterConnection = None

uuid = ""

def handleData(data):
	log(data, 0)

	return

def log(logMsg, verbosity = 0):
	global log2Write
	
	if (verbosity < debug):
		log2Write.append("[" + str(verbosity) + "]: " + logMsg)
	if (verbosity <= 5):
		chat2Write.append(logMsg)

def connectSocket(_type, server_address, port):
	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
	# Connect to server
	try:
		sock.connect((server_address, port))
		log("starting up on %s port %s _ " % sock.getsockname() + _type, 2)
	except socket.error, msg:
		log(_type + " : Connect Failed. Error Code: {} Error: {}".format(str(msg[0]), msg[1]), 2)
		sys.exit()

	return sock

def startListener(address, port):
	global disconnecting

	log("startung listener", 120)
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
			log(address + ": '%s'" % data, 20)
			if data:
				handleData(data)
			else:
				log(address + ": connection closed _ listener", 2)
				break
		except socket.error, msg:
			if '[Errno 32] Broken pipe' in str(msg):
				log(address + ": connection closed _ listener", 2)
			else:
				log(address + ": '%s'" % msg + " _ listener", 2)
			break
	
	uuid = ""
	disconnecting = True

def startPromoter(address, port):
	global disconnecting
	global sending
	global tosend
	global uuid
	
	connection = connectSocket("promoter", address, port)
	tcp = tcpHandler(connection)
	
	global promoterConnection
	promoterConnection = connection
	
	uuid, length = tcp.listen()
	log(str(uuid) + " | " + str(length), 40)

	while not disconnecting:
		if sending:
			if tosend != "":
				log("want to send: " + tosend, 120)
				log(tcp.write(tosend), 120)
				
				tosend = ""
			sending = False
	
	uuid = ""
	connection.close()
	log(address + ": connection closed _ promoter", 2)

def write2Box(box, messageList, lastLength, maxLines):
	empty = ""
	for i in range(1,99):
		empty += " "	
		
	logLength = len(messageList)
	tempWrite = messageList
	
	if logLength > lastLength:		
		if logLength < maxLines:
			maxim = logLength
		else:
			maxim = maxLines
					
		i = 0
		while i < maxim:
			box.addstr(i+1, 1, empty)	
			box.addstr(i+1, 1, tempWrite[logLength - i - 1])
			i += 1
		
		return logLength, box
		
		box.refresh()
	else:
		return lastLength, box

def printScreen():
	global tosend
	global screen
	global log2Write

	empty = ""
	for i in range(1,99):
		empty += " "	
	
	logLength = 0
	chatLength = 0
	lastToSendLength = 0
	
	screen.clear()
	chatbox = curses.newwin(22, 120, 0, 0)
	chatbox.box()    
	chatbox.refresh()
		
	sendbox = curses.newwin(3, 120, 23, 0)
	sendbox.box()    
	sendbox.refresh()
	
	logbox = curses.newwin(35, 120, 27, 0)
	logbox.box()    
	logbox.refresh()
	
	screen.addstr(63, 1, "F5 - (re)connect")
	screen.addstr(" | END - close")
	screen.addstr(64, 1, "F6 - disconnect")
				
	while True:
		logLength, box = write2Box(logbox, log2Write, logLength, 35)
		box.refresh()
		
		chatLength, box = write2Box(chatbox, chat2Write, chatLength, 20)
		box.refresh()
		
		lengthToSend = len(tosend)
		
		if lengthToSend <> lastToSendLength:
			lastToSendLength = lengthToSend
			
			sendbox.addstr(1, 1, empty)			
			sendbox.addstr(1, 1, tosend)
			sendbox.refresh()
		
		screen.refresh()
			
def checkKeyboard():
	global tosend
	global closing
	global sending
	global screen
	global disconnecting
	global listenerConnection
	
	key = ''
	while not closing:
		key = screen.getch()
		if key == curses.KEY_END:
			closing = True
		elif key == ord('\n'):
			sending = True
		elif key == curses.KEY_BACKSPACE:
			tosend = tosend[:-1]
		elif key == curses.KEY_F5:
			connect()
		elif key == curses.KEY_F6:
			disconnecting = True
			log("connection closed _ listener", 2)
		elif key <= 256:
			tosend += chr(key)

def connect():
	global server_address
	global promoterPort
	global listenerPort
	global uuid
	global disconnecting
	
	disconnecting = False
	start_new_thread(startPromoter, (server_address, promoterPort,))
	
	while uuid == "":
		time.sleep(1)

	log("connect with uuid: " + str(uuid), 20)
	log("prepare listener start", 120)
	start_new_thread(startListener, (server_address, listenerPort,))

def Main():
	global closing
	global tosend
	global uuid
	
	global listenerConnection
	global promoterConnection
	
	start_new_thread(printScreen, ())
	start_new_thread(checkKeyboard, ())

	connect()

	while not closing:
		pass
	
	time.sleep(1)
	listenerConnection.close()
	promoterConnection.close()
	curses.endwin()

Main()

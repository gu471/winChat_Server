#!/usr/bin/env python3

#code|[,data]
	#HELO
	#msgC|TS|from|to|TSpurge|_data
	#restart (10Min)

	#EHLO|sam
	#msgS|to|_data
	#register|sam|forename|surename|holdtime
	#change|sam|holdtime
	#delete|sam

import socket
import sys
from thread import start_new_thread
from chatClasses import uuidSAM, uuidMessage, tcpHandler
import time

listenerPort = 5005
promoterPort = 5006

log2Write = []
#connectionsPromoter = []

messages = []
userIDs = []

debug = 80

#TBD
def handleData(data):
	global userIDs
	
	for userID in userIDs:
		message = uuidMessage(userID, "TBD", data)
		log(str(userID) + " <+ " + data, 20)
		messages.append(message)

	return

def log(logMsg, verbosity = 0):
	if (verbosity < debug):
		log2Write.append("[" + str(verbosity) + "]: " + logMsg)
	sys.stdout.flush()

def client_thread(user, connection, address):
	global userIDs

	userIDs.append(user.uuid)
		
	tcp = tcpHandler(connection)
	
	data = str(user.uuid)
	log("sending uuid: " + str(user.uuid), 50)
	
	log(tcp.write(data), 50)
	log("uuid sent " + str(user.uuid), 50)
	time.sleep(2)

	while True:
		try:		
			data, length = tcp.listen()
			log(address + ": " + data + " | " + str(length), 60)
			if data:
				handleData(data)
			else:
				log(address + ": connection closed _ listener", 5)
				userIDs.pop(userIDs.index(user.uuid))
				break
		except socket.error, msg:
			log(address + ": '%s'" % msg + " _ listener", 4)
			userIDs.pop(userIDs.index(user.uuid))
			break

def client_thread_promote(user, connection, address):
	global userIDs
	
	tcp = tcpHandler(connection)
	#users.append(user)
	log("user <+ " + str(user.uuid) + user.user, 30)

	while (user.uuid in userIDs):
		while (len(messages) > 0):
			log("messages: " + str(len(messages)), 60)
			for message in messages:
				if True or message.uuid == user.uuid:
					msg = messages.pop(messages.index(message))
					data = msg.header + msg.message

					log(address + " <<< " + msg.header, 25);

					tcp.write(data)
		time.sleep(2)
	log(address + ": connection closed _ promoter", 5)

def startSocket(_type, port):
	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
	# Bind the socket to the address given on the command line
	server_address = ('', port)    
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	# bind socket
	try:
		sock.bind(server_address)
		log("starting up on %s port %s _ " % sock.getsockname() + _type)
	except socket.error, msg:
		log(_type + " : Bind Failed. Error Code: {} Error: {}".format(str(msg[0]), msg[1]))
		sys.exit()

	sock.listen(1)
	log("waiting for a connection _ " + _type)

	return sock

def startListener(port):
	sock = startSocket("listener", port)

	while True:
		connection, client_address = sock.accept()
		user = uuidSAM("TBD")
		try:
			log(client_address[0] + " connected on :" + str(client_address[1]) + " _ listener")
			start_new_thread(client_thread, (user, connection,client_address[0],))
		except:
			log("Thread couldn't be startet for " + client_address[0] + " _ listener")

def startPromoter(port):
	sock = startSocket("promoter", port)
	
	while True:
		log("wait for conn", 50)
		connection, client_address = sock.accept()
		tcp = tcpHandler(connection)
		
		log("wait for uuid", 50)
		
		uuid, length = tcp.listen()
		
		log("got uuid: " + uuid, 50)
		user = uuidSAM("TBD", uuid)
		
		try:
			log(client_address[0] + " connected on :" + str(client_address[1]) + " _ promoter")
			start_new_thread(client_thread_promote, (user,connection,client_address[0],))
		except:
			log("Thread couldn't be startet for " + client_address[0] + " _ promoter")

def cleanupPromotionList():
	return

def cleanupChecker():
	return

def Main():
	start_new_thread(startListener, (listenerPort,))
	start_new_thread(startPromoter, (promoterPort,))

	while True:
		while len(log2Write) > 0:
			print >>sys.stderr, log2Write.pop(0)

		cleanupChecker()

def null():
	return
Main()

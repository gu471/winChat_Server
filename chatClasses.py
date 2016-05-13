import uuid

class uuidSAM:
	"""description of class"""
	
	def __init__(self, user, uid = None):
		self.user = user
		if uid == None:
			self.uuid = uuid.uuid4()
		else:
			self.uuid = uuid.UUID(uid)

class uuidMessage:
	"""description of class"""
	
	def __init__(self, uuid, header, message):
		self.header = header
		self.message = message
		self.uuid = uuid

class tcpHandler:
	
	def __init__(self, connection):
		self.connection = connection
	
	def listen(self):
		connection = self.connection
		#2 if not init EOT else SYN
		if not connection.recv(1) == 'I':
			connection.send('E')
		connection.send('S')
		#if not L return "" else recv Length
		while not connection.recv(1) == 'L':
			return 0, 0
		
		length = int(connection.recv(1024))
		connection.send('A')
		
		#if not (isinstance( length, int )): length = 1024*1024
		
		data = connection.recv(length)
		connection.send('A')
		
		return data, length

	def write(self, data):
		connection = self.connection
		#1 send init
		connection.send('I')
		#3 if not SYN exit else ACK
		val = connection.recv(1)
		if not val == 'S':
			return "SYN expected, got " + val
		connection.send('L')
		
		connection.send(str(len(data)))
		connection.recv(1)
		connection.send(data)
		connection.recv(1)
		return "ok"

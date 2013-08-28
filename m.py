import socket, base64, ssl, gtk, pygtk, os, time, mimetypes
pygtk.require('2.0')

class NetworkControl:
	def connectTo(self, host, port, SSL):
		self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		if SSL == True:
			self.object = ssl.wrap_socket(self.sock)
		else:
			self.object = self.sock
		print(self.object.connect((host, port)))
		return True
	def SSL(self):
		if self.sock:
			self.object = ssl.wrap_socket(self.sock)
			return True
		else:
			return False
	def write(self, text):
		print("> " + text + "\n")
		self.object.send(text + "\r\n")
		return True
	def read(self):
		return self.object.recv(4096)
	def close(self):
		self.sock.close()

class MailProtocol:
	def __init__(self):
		self.attachedfiles = []
		return
	def authenticate(self, username, password):
		pass
	def send(self, mailFrom, mailTo, subject, content):
		pass
	def attach(self, fileName):
		self.attachedfiles.append(fileName)
		return
		
class MailSMTP(MailProtocol):
	def __init__(self, host, port):
		self.attachedfiles = []
		self.auth = False
		self.conn = NetworkControl()
		self.conn.connectTo(host, port, False)
		self.parse(self.conn.read())
		return
	def parse(self, message):
		print(message)
		return message[:3]
	def authenticate(self, username, password):
		self.status = ""
		self.conn.write("HELO 127.0.0.1")
		self.status = self.parse(self.conn.read())
		if self.status == "250":
			self.conn.write("AUTH LOGIN")
			self.status = self.parse(self.conn.read())
			self.conn.write(base64.standard_b64encode(username))
			self.status = self.parse(self.conn.read())
			self.conn.write(base64.standard_b64encode(password))
			self.status = self.parse(self.conn.read())
			if self.status == "535":
				return False
			self.auth = True
			return True
		return
	def send(self, mailFrom, mailTo, subject, content):
		print("Sending...")
		if self.auth == False:
			return False
		md5part = base64.standard_b64encode(str(time.time()))
		self.conn.write("MAIL FROM: <" + mailFrom + ">")
		self.status = self.parse(self.conn.read())
		self.conn.write("RCPT TO: <" + mailTo + ">")
		self.status = self.parse(self.conn.read())
		self.conn.write("DATA")
		self.status = self.parse(self.conn.read())
		
		# Prepare headers for a full mime-compliant email
		self_headers = []
		self_headers.append("From: "+mailFrom)
		self_headers.append("To: "+mailTo)
		self_headers.append("Subject: "+subject)
		self_headers.append("Content-Type: multipart/alternative; boundary=\""+md5part+"\"")
		self_headers.append("MIME-Version: 1.0")
		
		# Prepare the body/bodies
		self_body = []
		# Plaintext first
		self_body.append("Content-Type: text/plain; charset=\"iso-8859-1\"\r\nContent-Transfer-Encoding: 7bit\r\n\r\n"+content+"\r\n")
		# Attachments
		try:
			self.attachedfiles
		except NameError:
			self.attachedfiles = None
		if self.attachedfiles is None:
			self.attachedfiles = []
		for file in self.attachedfiles:
			fileData = open(file, "rb")
			d = fileData.read()
			fileFormat = mimetypes.guess_type(file)
			self_body.append("Content-Type: "+fileFormat[0]+"; name=\""+os.path.basename(file)+"\"\r\nContent-Transfer-Encoding: base64\r\nContent-Disposition: attachment; file=\""+os.path.basename(file)+"\"\r\n\r\n"+d.encode("base64"))
		
		for b in self_headers:
			self.conn.write(b)
		self.conn.write("")
		self.conn.write("This is a multi-part message in MIME format.\r\n\r\n")
		for b in self_body:
			self.conn.write("--"+md5part+"")
			self.conn.write(b)
		self.conn.write("--"+md5part+"--")
		self.conn.write("")
		self.conn.write(".")
		self.status = self.parse(self.conn.read())
		return
		
class MailSMTPSSL(MailSMTP, MailProtocol):
	def __init__(self, host, port):
		self.attachedfiles = []
		self.auth = False
		self.conn = NetworkControl()
		self.conn.connectTo(host, port, True)
		self.parse(self.conn.read())
		return	
		
class MailSMTPTLS(MailSMTP, MailProtocol):
	def __init__(self, host, port):
		self.attachedfiles = []
		self.auth = False
		self.conn = NetworkControl()
		self.conn.connectTo(host, port, False)
		self.parse(self.conn.read())
		return
	def authenticate(self, username, password):
		self.status = ""
		self.conn.write("HELO 127.0.0.1")
		self.status = self.parse(self.conn.read())
		if self.status == "250":
			self.conn.write("STARTTLS")
			self.status = self.parse(self.conn.read())
			if self.status == "220":
				self.conn.SSL()
				self.status = ""
				self.conn.write("HELO 127.0.0.1")
				self.status = self.parse(self.conn.read())
				if self.status == "250":
					self.conn.write("AUTH LOGIN")
					self.status = self.parse(self.conn.read())
					self.conn.write(base64.standard_b64encode(username))
					self.status = self.parse(self.conn.read())
					self.conn.write(base64.standard_b64encode(password))
					self.status = self.parse(self.conn.read())
					if self.status == "535":
						return False
					else:
						self.auth = True
						return True
		return
mimetypes.init()


import socket, base64, ssl, gtk, pygtk, os
from Tkinter import Tk
from tkFileDialog import askopenfilename
pygtk.require('2.0')
import m
class Entry:
	def __init__(self,width):
		self.component = gtk.Entry(width)
		return

class TextView:
	def __init__(self, title):
		self.component = gtk.TextView(title)
		return

class Label:
	def __init__(self, title):
		self.component = gtk.Label(title)
		return

class Window:
	def __init__(self, title, x, y, border_x):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_title(title)
		self.window.set_size_request(x,y)
		self.window.set_border_width(border_x)
		self.window.connect("delete-event", lambda a,b: gtk.main_quit())
		self.window.show()

		return

	def addFrame(self, frame):
		self.window.add(frame.frame)
		
		return

class Button:
	def __init__(self, text):
		self.component = gtk.Button(text)
		self.component.show()
		return

class Table:
	def __init__(self, rows, cols, border_x):
		self.component = gtk.Table(rows, cols, True)
		self.component.set_border_width(border_x)
		self.component.show()

		return

	def attach(self, element, topleft, topright, bottomleft, bottomright):
		self.component.attach(element.component, topleft, topright, bottomleft, bottomright)
		
		return
class FileUpload:
	def __init__(self):
		self.fileCheck = Label('No file selected')
		self.btn = Button('Attach File')
		self.btn.component.connect('clicked', self.openFileBrowser)
		self.tbl = Table(1,4,0)
		self.tbl.attach(self.fileCheck, 0, 3, 0, 1)
		self.tbl.attach(self.btn, 3, 4, 0, 1)
		self.fileCheck.component.show()
		self.component = self.tbl.component
		self.pathValue = None
		return
	def openFileBrowser(self,v):
		Tk().withdraw()
		filePath = askopenfilename()
		if filePath == None:
			self.pathValue = None
			self.fileCheck.component.set_label("No file selected")
		else:
			self.pathValue = filePath
			self.fileCheck.component.set_label(filePath)
		return
	def get_text(self):
		return self.pathValue
class Frame:
	def __init__(self):
		self.frame = gtk.Frame()
		self.frame.show()
		return

	def add(self, element):
		self.frame.add(element.component)
		return

class ComboBox:
	def __init__(self):
		self.component = gtk.combo_box_new_text()
		self.component.show()
		return
class GUI:
	def __init__(self):
		self.fields = {}
		self.labels = {}
		self.iters = {}
		self.oldentries = []
		self.window = None
		self.frame = None
		self.msg = None

		return
class Mailer:
	def __init__(self):
		self.ui = GUI()
		self.protocol = "None"
		return
	def createWindow(self):
		window = Window("MiniMailer 2.0", 315, 500, 2)
		frametest = Frame()
		window.addFrame(frametest)
		return frametest
	def bindUI(self, frm):
		self.ui.frame = frm
		self.ui.table = Table(16, 3, 20)
		self.ui.frame.add(self.ui.table)

		self.ui.labels["to"] = Label("Recipient's Email: ")
		self.ui.table.attach(self.ui.labels["to"], 0, 1, 1, 2)

		self.ui.fields["to"] = Entry(100)
		self.ui.table.attach(self.ui.fields["to"], 0, 3, 2, 3)

		self.ui.labels["from"] = Label("Sender's Email: ")
		self.ui.table.attach(self.ui.labels["from"], 0, 1, 3, 4)

		self.ui.fields["from"] = Entry(100)
		self.ui.table.attach(self.ui.fields["from"], 0, 3, 4, 5)

		self.ui.labels["password"] = Label("Password: ")
		self.ui.table.attach(self.ui.labels["password"], 0, 1, 5, 6)

		self.ui.fields["password"] = Entry(100)
		self.ui.fields["password"].component.set_visibility(False)
		self.ui.table.attach(self.ui.fields["password"], 0, 3, 6, 7)

		# Subject field label
		self.ui.labels["subject"] = Label("Subject: ")
		self.ui.table.attach(self.ui.labels["subject"], 0, 1, 7, 8)

		# Subject field
		self.ui.fields["subject"] = Entry(120)
		self.ui.table.attach(self.ui.fields["subject"], 0, 3, 8, 9)

		# Combo box label
		self.ui.labels["protocol"] = Label("Protocol to use: ")
		self.ui.table.attach(self.ui.labels["protocol"], 0, 1, 9, 10)

		# Combo box to select protocol type
		protocols = ["SSL", "TLS", "None"]
		self.ui.protocolSelect = ComboBox()
		#self.ui.protocolSelect.component.set_entry_text_column(0)
		self.ui.protocolSelect.component.connect("changed", self.setProtocolFromUI)
		for p in protocols:
			self.ui.protocolSelect.component.append_text(p)
		self.ui.table.attach(self.ui.protocolSelect, 0, 3, 10, 11)

		# Message body label
		self.ui.labels["message"] = Label("Message: ")
		self.ui.table.attach(self.ui.labels["message"], 0, 1, 11, 12)
		
		# Message body text field
		self.ui.fields["message"] = TextView(None)
		self.ui.msg = self.ui.fields["message"].component.get_buffer()
		self.ui.table.attach(self.ui.fields["message"], 0, 3, 12, 16)

		# Attach a file path
		self.ui.fileattach = FileUpload()
		self.ui.table.attach(self.ui.fileattach, 0, 3, 17, 18)
		
		# Attach a file button

		# Send button
		self.ui.send = Button("Send")
		self.ui.send.component.connect("clicked", self.do_send)
		self.ui.table.attach(self.ui.send, 1, 2, 19, 20)
	
		# Detect if this is the first use
		self.detectIfFirstUse()

		for num in self.ui.fields:
			self.ui.fields[num].component.set_editable(True)
			self.ui.fields[num].component.show()

		for num in self.ui.labels:
			self.ui.labels[num].component.set_justify(gtk.JUSTIFY_LEFT)
			self.ui.labels[num].component.show()
		return
	def setProtocolFromUI(self, v):
		self.protocol = v.get_active_text()
		return
	def do_send(self, blah):
		self.sendObject = False
		if (self.protocol == "TLS"):
			self.sendObject = m.MailSMTPTLS("smtp.gmail.com",587)
		elif (self.protocol == "SSL"):
			self.sendObject = m.MailSMTPSSL("smtp.gmail.com",465)
		else:
			self.sendObject = m.MailSMTP("smtp.gmail.com",25)
		if (self.ui.fileattach.get_text() != None):
			self.sendObject.attach(self.ui.fileattach.get_text())
		it1, it2 = self.ui.msg.get_bounds()
		self.sendObject.authenticate(self.ui.fields["from"].component.get_text(), self.ui.fields["password"].component.get_text())
		self.sendObject.send(self.ui.fields["from"].component.get_text(), self.ui.fields["to"].component.get_text(), self.ui.fields["subject"].component.get_text(), self.ui.msg.get_text(it1,it2))
		return
	def detectIfFirstUse(self):
		try:
			self.fp = open(os.path.expanduser("~/minimailer/config.txt"),"r")
			self.ui.fields["to"].component.set_text(self.fp.readline().strip('\n'))
			self.ui.fields["from"].component.set_text(self.fp.readline().strip('\n'))
			self.fp.close()
		except IOError:
			if not os.path.isdir(os.path.expanduser("~/minimailer/")):
				os.mkdir(os.path.expanduser("~/minimailer/"))
			self.fp = open(os.path.expanduser("~/minimailer/config.txt"),"w")
			self.fp.close()
		return

mail = Mailer()
frm = mail.createWindow()
mail.bindUI(frm)
gtk.main()

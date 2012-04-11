from HTMLParser import HTMLParser
import urllib
import smtplib
import base64
from time import time
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import os


class ParseSDUTChallenge(HTMLParser):
	challengeValue = ""
	nextIsValueOfChallgenge = 0
	def handle_starttag(self, tag, attrs):
		if tag == "input":
			for attr in attrs:
				for vals in attr:
					if self.nextIsValueOfChallgenge:
						if vals != "value":
							self.challengeValue = vals
							self.nextIsValueOfChallgenge = 0
					if vals == "challenge":
						self.nextIsValueOfChallgenge = 1

class ParseSDUTLinks(HTMLParser):
    rss_data_name = ""
    rss_data_link = ""
    rss_data_v = dict()
    rss_data = []
    def handle_starttag(self, tag, attrs):
        if tag == "p":
        	self.rss_data_v = dict()
        	self.rss_data_name = ""
        	self.rss_data_link = ""
        if tag == "a":
        	for attr in attrs:
	    	    for vals in attr:
	    	    	if vals != "href":
		    	    	self.rss_data_link = vals
    def handle_endtag(self, tag):
        if tag == "p":
        	if self.rss_data_name != "Back":
	        	self.rss_data_v['name'] = self.rss_data_name
	        	self.rss_data_v['link'] = self.rss_data_link
	        	self.rss_data.append(self.rss_data_v)
	        
    def handle_data(self, data):
        self.rss_data_name = data

class SendSDUTNewspaper():
	SdutUsername = "xxx@xxx"
	SdutPassword = "xxxxx"
	senderEmailAddress = "xxx@xxx.com"
	recipientMailAddress = "xxx@free.kindle.com"
	device = "kindle"
	deviceExtension = ".mobi"
	gmailUserName = "xxxx"
	gmailUserPassword = "xxxx"
	url = "http://sandiegouniontribune.ca.newsmemory.com/ebook.php?page=downloadEbooks&device="+device
	
	parser = ParseSDUTLinks()
	challengeParser = ParseSDUTChallenge()
	
	def init(self):
		t= int(time())
		challengefile = urllib.urlopen(self.url)
		self.challengeParser.feed(challengefile.read())
		params = urllib.urlencode({'username':self.SdutUsername,'password':self.SdutPassword,'submit':'Log in','pSetup':'sandiegouniontribune','time':t,'token':'','challenge':self.challengeParser.challengeValue,'protError':'4','device':'kindle'})
		self.file = urllib.urlopen(self.url,params)
		
	
	def parseFileName(self):
		date_temp = self.newspaper_title.split(',')
		date = date_temp[1].strip().split(" ")
		self.local_filename = "_".join(date)+self.deviceExtension
	
	def parseData(self):
		self.parser.feed(self.file.read())
		if len(self.parser.rss_data) > 0:
			self.newspaper_file = self.parser.rss_data[0]['link']
			self.newspaper_title = self.parser.rss_data[0]['name']
			self.parseFileName()
			if not os.path.exists(self.local_filename):
				self.removeOldFile()
				self.sendMail()
			
	def removeOldFile(self):
		for file in os.listdir(os.getcwd()):
			if file.endswith('.mobi'):
				os.remove(file)
				
	def readNewsPaperFile(self):
		try:
			newspaper_localfile_tmp = urllib.urlretrieve(self.newspaper_file,self.local_filename)
			return newspaper_localfile_tmp[0]
		except Exception:
			print "Error: unable to read the Newspaper File"
	
	def sendMail(self):
		file = self.readNewsPaperFile()
		msg = MIMEMultipart()
		msg['Subject'] = self.newspaper_title		
		fp = open(file, 'rb')
		mimefile = MIMEApplication(fp.read(),self.local_filename)
		mimefile.add_header('Content-Disposition', 'attachment', filename = self.local_filename)
		fp.close()
		msg.attach(mimefile)
		try:
			server = smtplib.SMTP()
			server.connect('smtp.gmail.com',587)
			server.ehlo()
			server.starttls()
			server.login(self.gmailUserName,self.gmailUserPassword)
			server.sendmail(self.senderEmailAddress, self.recipientMailAddress, msg.as_string())
			server.quit()
		except Exception:
		   print "Error: unable to send email: %s",Exception
		   


sendSDUT = SendSDUTNewspaper()
sendSDUT.init()
sendSDUT.parseData()
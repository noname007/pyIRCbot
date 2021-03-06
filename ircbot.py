#-*- encoding: utf-8 -*-

import sys
reload(sys).setdefaultencoding("utf8")

import socket
import time
import re
import function
from function.webapi.ip import reIPv4
from function.webapi.ip import reIPv6
from function.webapi.ip import reURL


class ircBot:

	def __init__(self, host, port, nick, password, channel):
		self.Host = host
		self.Port = port
		self.Nick = nick
		self.Password = password
		self.Chan = channel
		self.Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def createConnection(self):
		self.Sock.connect((self.Host, self.Port))
		self.Sock.send("NICK " + self.Nick + "\r\n")
		self.Sock.send("PASS " + self.Nick + ":" + self.Password + "\r\n")
		self.Sock.send("USER " + self.Nick + " " + self.Nick + " " + self.Nick + " :" + self.Nick + "\r\n")
 		self.Sock.send("JOIN " + self.Chan + "\r\n")

	def receiveData(self):
		return self.Sock.makefile()

	def responsePingfromServer(self, message):
		if message.startswith("PING"):
			self.Sock.send(message.replace("PING", "PONG"))

	def replyMessage(self, replies, nickname, limit):
		if len(replies) > limit:
			head = 0;
			tail = limit;
			while tail < len(replies):
				while ord(replies[tail]) & 0xc0 != 0x80:
					if tail + 1 < len(replies):
						tail = tail + 1
					else:
						break
				self.Sock.send("PRIVMSG " + self.Chan + " :"  + "%s: %s\r\n" % (nickname, replies[head:tail].replace("\n", "")))
				print ">>> " + replies[head:tail]
				time.sleep(1)
				head = tail
				tail = tail + limit
				if tail > len(replies):
					self.Sock.send("PRIVMSG " + self.Chan + " :"  + "%s: %s\r\n" % (nickname, replies[head:len(replies)].replace("\n", "")))
					print ">>> " + replies[head:len(replies)]
		else:
			for reply in replies.strip().split("\n"):
				self.Sock.send("PRIVMSG " + self.Chan + " :"  + "%s: %s\r\n" % (nickname, reply))
				print ">>> " + reply

	def speakInChannel(self, message):
		self.Sock.send("PRIVMSG " + self.Chan + " :" + message + "\r\n")
		print ">>> " + message

	def searchUserLocation(self, message, ipURL, check_the_water_meter = ""):
		if re.search(R"JOIN", message.strip()):
			if re.search(R"PRIVMSG", message.strip()):
				pass
			elif re.match(r"^:([^!]+)", message).group(1) == self.Nick:
				pass
			else:
				nickname = re.match(r"^:([^!]+)", message).group(1)
				origin_ip = re.search(R"^:([^ ]+)", message).group(1).split('@')[1]
				if re.search(reIPv4, origin_ip):
					print "<<< " + nickname
					ip = re.search(reIPv4, origin_ip).group(0)
					if check_the_water_meter:
						check_the_water_meter(lambda nick, ip: self.speakInChannel(nickname + " " + ip + " " + function.webapi.ip.reply(ipURL, ip)), nickname, ip)
					else:
						self.speakInChannel(nickname + " " + ip + " " + function.webapi.ip.reply(ipURL, ip))
				elif re.search(reIPv6, origin_ip):
					print "<<< " + nickname
					ip = re.search(reIPv6, origin_ip).group(0)
					if check_the_water_meter:
						check_the_water_meter(lambda nick, ip: self.speakInChannel(nickname + " " + ip + " " + function.webapi.ip.reply(ipURL, ip)), nickname, ip)
					else:
						self.speakInChannel(nickname + " " + ip + " " + function.webapi.ip.reply(ipURL, ip))
				elif re.search(reURL, origin_ip):
					print "<<< " + nickname
					ip = re.search(reURL, origin_ip).group(0)
					if check_the_water_meter:
						check_the_water_meter(lambda nick, ip: self.speakInChannel(nickname + " " + ip + " " + function.webapi.ip.reply(ipURL, ip)), nickname, ip)
					else:
						self.speakInChannel(nickname + " " + ip + " " + function.webapi.ip.reply(ipURL, ip))


class ip_once(object):

	class helper(object):
		def __init__(self):
			self.prev_mday = time.localtime().tm_mday
			self.ip_info_set = set()

		def __call__(self, cur_mday, fn, pr):
			if self.prev_mday != cur_mday:
				self.ip_info_set.clear()
				self.prev_mday = cur_mday

			if pr not in self.ip_info_set:
				fn(*pr)
				self.ip_info_set.add(pr)

	def __init__(self):
		self.aux = self.helper()

	def __call__(self, fn, nick, ip):
		self.aux(time.localtime().tm_mday, fn, (nick, ip))

# -*- coding: utf-8 -*-
import socket
import time


class NetworkSocket(object):
	def __init__(self, host='localhost', port=50000):
		self.host = host
		self.port = port
		self.data_size = 1024
		self.input_buffer = ""
		self.socket = None
		self.socket_ready = False
		self.heartbeat = 0
		self.setup_time = 0

	def destroy(self):
		self.close_socket()

	def tick(self, delta_seconds):
		received_data = self.read_socket()

		# Send heart beat string to server
		self.send_heartbeat()

		if received_data:
			# Do something with the received data,
			# print it in the log for now
			print(received_data)

	def setup_socket(self):
		new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		new_socket.connect((self.host, self.port))
		new_socket.setblocking(False)
		self.socket = new_socket
		self.socket_ready = True
		self.heartbeat = 0
		self.setup_time = time.time()

	def write_socket(self, data):
		if not self.socket_ready:
			return

		self.socket.send(data)

	def read_socket(self):
		if not self.socket_ready:
			return ""

		data = ""
		try:
			data = self.socket.recv(self.data_size).rstrip('\r\n')
		except socket.error as e:
			err = e.args[0]
			if err == 10035:  # errno.EWOULDBLOCK at POSIX
				pass
			else:
				raise

		return data

	def close_socket(self):
		if not self.socket_ready:
			return

		self.socket.close()
		self.socket_ready = False

	def send_heartbeat(self):
		cur_time = time.time()
		if cur_time - self.setup_time - self.heartbeat > 1:
			self.heartbeat = int(cur_time - self.setup_time)
			self.write_socket("socket [host: {}, port: {}] has setup {} seconds.".format(
				self.host, self.port, self.heartbeat))

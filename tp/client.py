from host import Host
from integer_set import IntegerSet
from connection import Connection
import random
import math
import utils

class Client(Host):
	def __init__(self, sim, down_mbps, up_mbps, wait_time):
		super().__init__(sim, down_mbps, up_mbps)
		self._wait_time = wait_time
		self._joined_time = sim.env.now
		self._finished = False

	def begin(self):
		"""
		Client start point.  Initially, it requests all pieces from the HTTP
		server.
		"""
		self._pending = IntegerSet(range(self.sim.piece_count))
		self._target_chunk_size = math.ceil(self.sim.piece_count / self.sim.pieces_split_size)
		self._request_pieces()

	def get_random_chunk(self):
		split_n = math.floor(len(self._pending) / self._target_chunk_size)
		if split_n == 0:
			return self._pending.copy()

		return random.choice(self._pending.split(split_n))


	def _request_pieces(self):
		HTTPServer = self.sim.HTTPServer

		if not self.has_download_space():
			return

		if HTTPServer.can_use_torrent():
			for client in self.sim.clients:
				if not self.has_download_space():
					break
				if not client.has_upload_space():
					continue

				if self.connected_to(client):
					continue

				intersection = self._pending.intersect(client.pieces)
				if len(intersection):
					if len(intersection) > self._target_chunk_size:
						intersection = intersection.take(self._target_chunk_size)

					c = client.upload_to(self, self.avail_download_space(), intersection)
					self.downloads.append(c)
					c.begin()

					self._pending.remove_set(intersection)

		if not len(self._pending) or \
			not self.has_download_space() or \
			not HTTPServer.can_use_http() or \
			self.connected_to(HTTPServer):
			return

		next_chunk = self.get_random_chunk()
		c = HTTPServer.upload_to(self, self.avail_download_space(), next_chunk)
		try:
			self._pending.remove_set(next_chunk)
		except:
			print(len(next_chunk))
			import code; code.interact(local=locals())
			raise

		self.downloads.append(c)
		c.begin()
		self.bandwidth_check_down()

	def connected_to(self, host):
		for c in self.downloads:
			if c.origin == host:
				return True

		return False

	def upload_to(self, other, other_mbps, indices):
		if not self.avail_upload_space():
			raise Exception("no upload space remaining")
		speed = min(self.avail_upload_space(), other_mbps)
		c = Connection(self.sim, self, other, speed, indices)
		self.uploads.append(c)
		return c

	def external_transfer_finished(self, c):
		if len(self._pending) and not self._finished:
			self._request_pieces()

	def upload_finished(self, c):
		self.uploads.remove(c)

	def download_finished(self, c, completed, transfered):
		"""
		Download finished callback.  Decide what to download next here.
		"""
		self.downloads.remove(c)
		if self._finished:
			return

		if completed or transfered == len(c.requested):
			self.pieces.add_set(c.requested)
		else:
			transfered_pieces = c.requested.take(transfered)
			self.pieces.add_set(transfered_pieces)
			c.requested.remove_set(transfered_pieces)
			self._pending.add_set(c.requested)

		if len(self.pieces) >= self.sim.piece_count:
			self._finished = True
			for download in self.downloads:
				download.interrupt((Connection.CLOSED,)) # single-element tuple
			self._completed_time = (self.sim.env.now - self._joined_time) / 60
			self.sim.client_completed(self)
			self.sim.env.process(self.disconnect())
		else:
			self._request_pieces()

	def disconnect(self):
		yield self.sim.env.timeout(self._wait_time)
		self.sim.client_disconnected(self)
		for upload in self.uploads:
			upload.interrupt((Connection.CLOSED,)) # single-element tuple
		# print("client disconnected")

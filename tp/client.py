from host import Host
from integer_set import IntegerSet
from connection import Connection
import random
import utils

class Client(Host):
	def __init__(self, sim, down_mbps, up_mbps, wait_time):
		super().__init__(sim, down_mbps, up_mbps)
		self._wait_time = wait_time

	def begin(self):
		"""
		Client start point.  Initially, it requests all pieces from the HTTP 
		server.
		"""

		initial_request = IntegerSet(range(self.sim.piece_count))
		self._pending = initial_request.split(1000)
		random.shuffle(self._pending)
		self._request_pieces()
		# print("should use torrent: ", self.sim.HTTPServer.should_use_torrent())


	def _request_pieces(self):
		to_remove = []

		if not self.has_download_space():
			return

		if self.sim.HTTPServer.should_use_torrent():
			for client in self.sim.clients:
				if not self.has_download_space():
					break
				if not client.has_upload_space():
					continue

				if self.connected_to(client):
					continue

				for i_set in self._pending:
					intersection = i_set.intersect(client.pieces)
					if len(intersection):
						#print(str(self.avail_download_space()) + "   " + str(self.id))
						c = client.upload_to(self, self.avail_download_space(), intersection)
						self.downloads.append(c)
						c.begin()

						if len(intersection) == len(i_set):
							to_remove.append(i_set)
						else:
							i_set.remove_set(intersection)

						break

				for s in to_remove:
					self._pending.remove(s)
				to_remove.clear()
		else:
			if self.connected_to(self.sim.HTTPServer):
				return

			c = self.sim.HTTPServer.upload_to(self, self.avail_download_space(), self._pending[0])
			self._pending.pop(0)
			self.downloads.append(c)
			c.begin()

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
		if self.has_download_space() and self._pending:
			self._request_pieces()

	def upload_finished(self, c):
		self.uploads.remove(c)

	def download_finished(self, c, completed, transfered):
		"""
		Download finished callback.  Decide what to download next here.
		"""
		self.downloads.remove(c)
		if completed:
			self.pieces.add_set(c.requested)
		else:
			transfered_pieces = c.request.take(transfered)
			self.pieces.add_set(transfered_pieces)
			c.requested.remove_set(transfered_pieces)
			self._pending.append(c.requested)

		if len(self.pieces) == self.sim.piece_count:
			self.sim.env.process(self.disconnect())
		else:
			self._request_pieces()

	def disconnect(self):
		yield self.sim.env.timeout(self._wait_time)
		self.sim.client_disconnected(self)
		for upload, in self.uploads:
			info = {
				"reason": Connection.InterruptReason.closed
			}
			upload.interrupt(info)
		print("client disconnected")

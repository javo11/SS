from host import Host
from integer_set import IntegerSet
import random

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
		self._pending = initial_requests.split(1000)
		random.shuffle(requests)
		if self.sim.HTTPServer.should_use_torrent():
			for client in self.sim.clients:
				if not client.has_upload_space():
					continue
				for i_set in self._pending:
					difference = client.pieces.copy().remove_set(i_set)
					if len(difference) != len(i_set):



		else:
			c = self.sim.HTTPServer.upload_to(self, self.down_mbps, self._pending[0])
			self.downloads.append(c)
			c.begin()

	def upload_to(self, other, other_mbps, indices):
		speed = min(self.up_mbps, other_mbps)
		c = Connection(self.sim, self, other, speed, indices)
		self.uploads.append(c)
		return c

	def external_transfer_finished(self, c):
		pass

	def upload_finished(self, c):
		print("client acknowledges upload finished")
		self.uploads.remove(c)

	def download_finished(self, c, completed, transfered):
		"""
		Download finished callback.  Decide what to download next here.
		"""
		print("client acknowledges download finished")
		self.downloads.remove(c)
		if completed:
			self.pieces.add_range(c.requested)
		else:
			self.pieces.add_range(c.request.take(transfered))
			raise NotImplementedError()

		if (len(self.pieces) == self.sim.piece_count):
			self.sim.env.process(self.disconnect())

	def disconnect(self):
		yield self.sim.env.timeout(self._wait_time)
		self.sim.client_disconnected()

from host import Host
from integer_set import IntegerSet

class Client(Host):
	def __init__(self, sim, down_mbps, up_mbps):
		super().__init__(sim, down_mbps, up_mbps)

	def begin(self):
		initial_request = IntegerSet(range(self.sim.piece_count)) # request all pieces
		c = self.sim.HTTPServer.upload_to(self, self.down_mbps, initial_request)
		self.downloads.append(c)
		c.begin()

	def upload_finished(self, c):
		print("client acknowledges upload finished")
		self.uploads.remove(c)

	def download_finished(self, c):
		print("client acknowledges download finished")
		self.downloads.remove(c)
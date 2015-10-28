from integer_set import IntegerSet

class Host:
	ID_COUNTER = 0

	def __init__(self, sim, down_mbps, up_mbps):
		self.sim = sim
		self.down_mbps = down_mbps
		self.up_mbps = up_mbps
		self.id = self.ID_COUNTER
		Host.ID_COUNTER += 1
		self.uploads = []
		self.downloads = []
		self.pieces = IntegerSet()

	def upload_to(self, other, other_mbps, indices):
		raise NotImplementedError()

	def upload_finished(self, c):
		raise NotImplementedError()

	def download_finished(self, c):
		raise NotImplementedError()
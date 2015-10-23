import connection

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
		self.pieces = set()

	def upload_to(self, other, indices):
		"""
		Transfer pieces from self to other
		"""
		if not self.downloads:
			speed = self.up_mbps # CHANGE
			c = connection.Connection(self.sim, self, other, speed, indices)
			self.uploads.append(c)
			return c
		else:
		 	raise Exception("not implemented")
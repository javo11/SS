import connection

class Host:
	_ID_COUNTER = 0

	def __init__(self, env, down_mbps, up_mbps):
		self.env = env
		self.down_mbps = down_mbps
		self.up_mbps = up_mbps
		self.id = self._ID_COUNTER
		self._ID_COUNTER += 1
		self.uploads = []
		self.downloads = []
		self.pieces = set()

	def request_download(self, other, indices):
		"""
		Transfer files from self to other
		"""
		if not self.downloads:
			cap = connection.capacity_for(self.up_mbps, 10, self.env.simulation.mtu)
			indices = range(self.env.simulation.piece_count)
			c = connection.Connection(self.env, self, other, cap, indices)
			self.uploads.append(c)
			return c
		else
		 	raise Exception("not implemented")
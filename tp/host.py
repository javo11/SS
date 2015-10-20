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

	def upload_to(self, other, indices):
		"""
		Transfer files from self to other
		"""
		if not self.downloads:
			latency = 10 #change
			cap = connection.capacity_for(self.up_mbps, latency, self.env.sim.mtu)
			indices = range(self.env.sim.piece_count)
			c = connection.Connection(self.env, self, other, cap, indices, latency)
			self.uploads.append(c)
			self.env.process(self.begin_upload(c))
			return c
		else:
		 	raise Exception("not implemented")

	def begin_upload(self, connection):
		raise NotImplementedError()
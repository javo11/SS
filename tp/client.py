from host import Host

class Client(Host):
	def __init__(self, sim, down_mbps, up_mbps):
		super().__init__(sim, down_mbps, up_mbps)

	def begin(self):
		initial_request = range(self.sim.piece_count) # request all pieces
		c = self.sim.HTTPServer.upload_to(self, initial_request)
		self.downloads.append(c)
		c.begin()
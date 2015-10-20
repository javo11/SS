from host import Host

class Client(Host):
	def __init__(self, env, down_mbps, up_mbps):
		super().__init__(env, down_mbps, up_mbps)
		self.action = env.process(self.run())

	def run(self):
		c = self.env.sim.HTTPServer.upload_to(self, range(self.env.sim.piece_count))
		self.downloads.append(c)

		while True:
			yield self.env.timeout(c.latency)
			piece = yield c.store.get()
			print("received piece " + str(piece) + " at " + str(self.env.now))
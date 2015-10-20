from host import Host

class Client(Host):
	def __init__(self, env, down_mbps, up_mbps):
		super().__init__(env, down_mbps, up_mbps)
		self.action = env.process(self.run())

	def run(self):
		c = self.env.simulation.HTTPServer.request_download(self)
		self.downloads.append(c)
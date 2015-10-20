from host import Host

class Server(Host):
	def __init__(self, env, down_mbps, up_mbps):
		super().__init__(env, down_mbps, up_mbps)
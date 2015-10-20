from host import Host

class Server(Host):
	def __init__(self, env, down_mbps, up_mbps):
		super().__init__(env, down_mbps, up_mbps)

	def begin_upload(self, connection):
		for i in connection.requested:
			yield connection.store.put(i)


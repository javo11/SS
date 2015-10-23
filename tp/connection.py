import simpy

class Connection:
	def __init__(self, sim, origin, destination, speed, requested):
		self.sim = sim
		self.origin = origin
		self.destination = destination
		self.speed = speed
		self.requested = requested

	def begin(self):
		self.action = self.sim.env.process(self.start_transfer())

	def start_transfer(self):
		request_size = len(self.requested) * self.sim.mtu
		time = float(request_size) / (self.speed * 1024**2)
		try:
			yield self.sim.env.timeout(time)
			print("Transfer complete from host %d to host %d at %f" % (self.origin.id, self.destination.id, self.sim.env.now))
		except simpy.Interrupt:
			
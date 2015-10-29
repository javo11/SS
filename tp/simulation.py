import math
import random
from server import Server
from client import Client

class Simulation:
	"""
	Simulation class contains all of the simulation's parameters,
	and the simpy environment.
	"""

	def __init__(self, env, settings):
		self.env = env

		self.client_up_mu = float(settings['ClientUpMu'])
		self.client_up_sigma = float(settings['ClientUpSigma'])

		self.client_down_mu = float(settings['ClientDownMu'])
		self.client_down_sigma = float(settings['ClientDownSigma'])

		self.arrival_param = float(settings['ClientsPerDay']) / (24 * 60 * 60)
		self.mtu = int(settings['MTU'])
		self.file_size = float(settings['FileSizeGB']) * (1024 ** 3)
		self.piece_count = math.ceil(self.file_size / self.mtu)
		self.HTTPServer = Server(self, 0, int(settings['HTTPUp']))
		self.run_time = int(settings['TimeLimitDays']) * 24 * 60 * 60

	def gen_client_up(self):
		return random.normalvariate(self.client_up_mu, self.client_up_sigma)

	def gen_client_down(self):
		return random.normalvariate(self.client_down_mu, self.client_down_sigma)

	def run(self):
		"""
		Spawn the client_arrival_loop process.
		"""
		self.env.process(self.client_arrival_loop())
		self.env.run(until=20000) # TESTING
		# self.env.run(until=self.run_time)

	def client_arrival_loop(self):
		"""
		Main simulation loop.  Simulation starts and ends here, after
		self.run_time seconds have elapsed.
		"""
		client_count = 0
		while True:
			t = random.expovariate(self.arrival_param)
			yield self.env.timeout(t)

			print("New client arrived at: " + str(self.env.now))
			c = Client(self, self.gen_client_down(), self.gen_client_up())
			c.begin()
			client_count += 1

	def connection_ended(self, c):
		pass
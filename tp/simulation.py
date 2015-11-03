import math
import stats
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

		self.client_wait_time_mu = float(settings['ClientWaitTimeMu']) * 60
		self.client_wait_time_sigma = float(settings['ClientWaitTimeSigma']) * 60

		self.arrival_param = float(settings['ClientsPerDay']) / (24 * 60 * 60)
		self.mtu = int(settings['MTU'])
		self.file_size = float(settings['FileSizeGB']) * (1024 ** 3)
		self.piece_count = math.ceil(self.file_size / self.mtu)
		self.HTTPServer = Server(self, 0, int(settings['HTTPUp']))
		self.run_time = float(settings['TimeLimitDays']) * 24 * 60 * 60
		self.pieces_split_size = int(settings['InitialSplitSize'])

		self.torrent_threshold = float(settings['TorrentThreshold'])
		self.stats_interval = float(settings['UpdateStatsInterval']) * 60
		self.draw_every = int(settings['DrawEvery'])

		self.clients = []

		self.update_stats_count = 0
		self.p2p_conn_count = 0
		self.http_conn_count = 0
		self.completed_clients = 0
		self.completion_time_avg = 0
		self.completion_times = []
		stats.setup_stats(self)

	def gen_client_up(self):
		return random.normalvariate(self.client_up_mu, self.client_up_sigma)

	def gen_client_down(self):
		return random.normalvariate(self.client_down_mu, self.client_down_sigma)

	def gen_client_wait_time(self):
		return random.normalvariate(self.client_wait_time_mu, self.client_wait_time_sigma)

	def run(self):
		"""
		Spawn the client_arrival_loop process.
		"""
		random.seed(1338)

		self.env.process(self.client_arrival_loop())
		self.env.process(self.stats_update_loop())
		self.env.run(until=self.run_time)

		print("SIMULATION ENDED")
		stats.stats_end(self)

	def client_arrival_loop(self):
		"""
		Main simulation loop.  Simulation starts and ends here, after
		self.run_time seconds have elapsed.
		"""
		client_count = 0
		while True:
			t = random.expovariate(self.arrival_param)
			yield self.env.timeout(t)

			# print("New client arrived at: " + str(self.env.now))
			c = Client(self, self.gen_client_down(), self.gen_client_up(), self.gen_client_wait_time())
			self.clients.append(c)
			c.begin()
			client_count += 1

	def stats_update_loop(self):
		while True:
			yield self.env.timeout(self.stats_interval)
			self.update_stats_count += 1
			draw = self.update_stats_count % self.draw_every == 0
			stats.update_stats(self, draw)

	def client_completed(self, client):
		self.completed_clients += 1
		self.completion_times.append(client._completed_time)
		self.completion_time_avg += (client._completed_time - self.completion_time_avg) / self.completed_clients

	def client_disconnected(self, client):
		self.clients.remove(client)

	def connection_started(self, c):
		if c.isp2p:
			self.p2p_conn_count += 1
		else:
			self.http_conn_count += 1

	def connection_ended(self, c):
		if c.isp2p:
			self.p2p_conn_count -= 1
		else:
			self.http_conn_count -= 1

		for client in self.clients:
			client.connection_ended(c)
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

	def __init__(self, env, settings, should_plot):
		self.env = env
		self.settings = settings
		self.should_plot = should_plot
		self.client_up_mu = float(settings['ClientUpMu'])
		self.client_up_sigma = float(settings['ClientUpSigma'])

		self.client_down_mu = float(settings['ClientDownMu'])
		self.client_down_sigma = float(settings['ClientDownSigma'])

		self.client_wait_time_mu = float(settings['ClientWaitTimeMu']) * 60
		self.client_wait_time_sigma = float(settings['ClientWaitTimeSigma']) * 60

		self.expected_clients = int(settings['ClientsPerCampaign'])
		self.mtu = int(settings['MTU'])
		self.file_size_gb = float(settings['FileSizeGB'])
		self.file_size = self.file_size_gb * (1024 ** 3)
		self.piece_count = math.ceil(self.file_size / self.mtu)
		self.http_up = int(settings['HTTPUp'])
		self.HTTPServer = Server(self, 0, self.http_up)

		self.run_time = int(settings['TimeLimitHours']) * 60 * 60
		self.interval_duration = int(settings['IntervalDurationHours']) * 60 * 60
		interval_count = self.run_time // self.interval_duration
		self.intervals = [int(p) for p in settings['IntervalPercentages'].split()]
		assert len(self.intervals) == interval_count
		assert sum(self.intervals) == 100

		self.pieces_split_size = int(settings['InitialSplitSize'])
		self.torrent_threshold = float(settings['TorrentThreshold'])
		self.http_down_threshold = float(settings['HTTPDownThreshold'])

		obj_dl_time_factor = float(settings['ObjDLTimeFactor'])
		self.obj_dl_time = self.file_size / (self.client_down_mu * (1024 ** 2))
		self.obj_dl_time *= obj_dl_time_factor

		self.clients = []
		self.active_clients_count = 0

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
		#random.seed(1338) #remove

		self.arrival_param = (self.intervals[0] / 100) * self.expected_clients
		self.arrival_param /= self.interval_duration

		self.env.process(self.client_interval_loop())
		self.env.process(self.client_arrival_loop())
		#self.env.process(self.debug_loop())
		self.env.run(until=self.run_time)

		print("SIMULATION ENDED")
		stats.plot_stats(self)
		stats.stats_end(self)

	def client_interval_loop(self):
		for i in self.intervals[1:]:
			yield self.env.timeout(self.interval_duration)
			self.arrival_param = (i / 100) * self.expected_clients
			self.arrival_param /= self.interval_duration


	def client_arrival_loop(self):
		"""
		Main simulation loop.  Simulation starts and ends here, after
		self.run_time seconds have elapsed.
		"""
		client_count = 0
		while True:
			t = random.expovariate(self.arrival_param)
			yield self.env.timeout(t)
			c = Client(self, self.gen_client_down(), self.gen_client_up(), self.gen_client_wait_time())
			self.clients.append(c)
			c.begin()
			client_count += 1
			self.clients_hist.append((self.env.now, len(self.clients)))
			self.active_clients_count += 1
			self.active_clients_hist.append((self.env.now, self.active_clients_count))
			# print("hit list: " + str(len(self.clients_hist)) + " client count: " + str(client_count))

	def debug_loop(self):
		while True:
			yield self.env.timeout(1800)
			print("clients :" + str(len(self.clients)) + " http: " + str(self.http_conn_count))


	def client_completed(self, client):
		self.completed_clients += 1
		self.completion_times.append(client._completed_time)
		self.completion_time_avg += (client._completed_time - self.completion_time_avg) / self.completed_clients
		self.completion_avg_hist.append((self.env.now, self.completion_time_avg))
		self.completion_count_hist.append((self.env.now, self.completed_clients))
		self.active_clients_count -= 1
		self.active_clients_hist.append((self.env.now, self.active_clients_count))

	def client_disconnected(self, client):
		self.clients.remove(client)
		self.clients_hist.append((self.env.now, len(self.clients)))

	def connection_started(self, c):
		if c.isp2p:
			self.p2p_conn_count += 1
			self.p2p_conn_hist.append((self.env.now, self.p2p_conn_count))
		else:
			self.http_conn_count += 1
			self.http_conn_hist.append((self.env.now, self.http_conn_count))

	def connection_ended(self, c):
		if c.isp2p:
			self.p2p_conn_count -= 1
			self.p2p_conn_hist.append((self.env.now, self.p2p_conn_count))
		else:
			self.http_conn_count -= 1
			self.http_conn_hist.append((self.env.now, self.http_conn_count))

		for client in self.clients:
			client.connection_ended(c)
import simpy
import math
import random
import configparser
from server import Server
from client import Client

class Simulation:
	pass

def setup_simulation(env):
	env.sim = Simulation()

	client_up_mu = float(env.settings['ClientUpMu'])
	client_up_sigma = float(env.settings['ClientUpSigma'])

	client_down_mu = float(env.settings['ClientDownMu'])
	client_down_sigma = float(env.settings['ClientDownSigma'])

	client_client_lat_mu = float(env.settings['ClientClientLatencyMu'])
	client_client_lat_sigma = float(env.settings['ClientClientLatencySigma'])

	client_server_lat_mu = float(env.settings['ClientServerLatencyMu'])
	client_server_lat_sigma = float(env.settings['ClientServerLatencySigma'])

	env.sim.gen_client_up = lambda: random.normalvariate(client_up_mu, client_up_sigma)
	env.sim.gen_client_down = lambda: random.normalvariate(client_down_mu, client_down_sigma)

	env.sim.gen_client_client_latency = lambda: random.normalvariate(client_client_lat_mu, client_client_lat_sigma)
	env.sim.gen_client_server_latency = lambda: random.normalvariate(client_server_lat_mu, client_server_lat_sigma)

	env.sim.arrival_param = 1.0 / float(env.settings['ArrivalLambda'])
	env.sim.mtu = int(env.settings['MTU'])
	env.sim.file_size = float(env.settings['FileSizeGB']) * (1024 ** 3)
	env.sim.piece_count = math.ceil(env.sim.file_size / env.sim.mtu)
	env.sim.HTTPServer = Server(env, 0, int(env.settings['HTTPUp']))

def start_network(env):
	# while True:
	# 	t = random.expovariate(env.sim.arrival_param)
	# 	yield env.timeout(t)
	# 	print("new client arrived at: " + str(env.now))
	client = Client(env, env.sim.gen_client_down(), env.sim.gen_client_up())

def main():
	env = simpy.Environment()
	config = configparser.ConfigParser()
	config.read("simulation.ini")
	env.settings = config['sim']
	setup_simulation(env)

	Client(env, env.sim.gen_client_down(), env.sim.gen_client_up())
	#env.process(start_network(env))
	env.run(until=1000000)

if __name__ == "__main__":
	main()
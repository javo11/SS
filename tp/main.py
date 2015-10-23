import simpy
import configparser
from simulation import Simulation

def start_network(env):
	while True:
		t = random.expovariate(env.sim.arrival_param)
		yield env.timeout(t)
		print("new client arrived at: " + str(env.now))
		c = Client(env, env.sim.gen_client_down(), env.sim.gen_client_up())
		c.begin()
		break

def main():
	env = simpy.Environment()
	config = configparser.ConfigParser()
	config.read("simulation.ini")
	settings = config['sim']
	sim = Simulation(env, settings)
	sim.run()

if __name__ == "__main__":
	main()
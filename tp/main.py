import simpy
import configparser
from simulation import Simulation

def main():
	"""
	Simulation entry point
	Read settings from simulation.ini file
	"""
	env = simpy.Environment()
	config = configparser.ConfigParser()
	config.read("simulation.ini")
	settings = config['sim']
	sim = Simulation(env, settings)
	sim.run()

if __name__ == "__main__":
	main()
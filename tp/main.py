import simpy
import configparser
import datetime
import xlsxwriter as xs
import random
from simulation import Simulation

def main():
	"""
	Simulation entry point
	Read settings from simulation.ini file
	"""
	results = []

	i = 0
	while i < 3:
		env = simpy.Environment()
		config = configparser.ConfigParser()
		config.read("simulation.ini")
		settings = config['sim']
		sim = Simulation(env, settings, i == 2)
		sim.run()
		results.append(sim.results)
		i += 1

	wb = xs.Workbook('Results_' + settings['FileSizeGB'] + '_' + settings['TorrentThreshold'] + '_' + settings['HTTPDownThreshold'] \
		+ '_' + settings['HTTPUp'] + '_'  + str(random.randint(0,10000)) + '.xlsx')
	
	ws = wb.add_worksheet()

	ws.write(0, 1, 'Exceded')
	ws.write(0, 2, 'Completed')

	i = 1
	for result in results:
		ws.write(i, 0, i)
		ws.write(i, 1, result['exceeded_proportion'])
		ws.write(i, 2, result['completed_count'])
		i += 1

	ws.write(i, 0, 'average')
	ws.write(i, 1, sum(result['exceeded_proportion'] for result in results)/len(results))
	ws.write(i, 2, sum(result['completed_count'] for result in results)/len(results))

	wb.close()

if __name__ == "__main__":
	main()
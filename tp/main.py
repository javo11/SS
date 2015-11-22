import simpy
import configparser
import datetime
import xlsxwriter as xs
import math
import random
import scipy.stats
from simulation import Simulation

def main():
	"""
	Simulation entry point
	Read settings from simulation.ini file
	"""
	results = []

	config = configparser.ConfigParser()
	config.read("simulation.ini")
	settings = config['sim']

	completed_obj_hw = int(settings["ClientsPerCampaign"]) * float(settings["CompletedPctgHW"])
	exceeded_obj_hw = float(settings["ExceededPctgHW"])
	significance_level = float(settings["SignificanceLevel"])
	z_val_two_tails = scipy.stats.norm.ppf(1 - (significance_level / 2))
	z_val_one_tail = scipy.stats.norm.ppf(1 - significance_level)

	print("Completed Target HW: " + str(completed_obj_hw))
	print("Exceeded Target HW: " + str(exceeded_obj_hw))

	completed_vals = []
	exceeded_vals = []

	i = 0
	while i < 10:
		print("RUN: " + str(i + 1))
		env = simpy.Environment()
		sim = Simulation(env, settings, i == 9)
		sim.run()
		results.append(sim.results)
		i += 1

		completed_vals.append(sim.results['completed_count'])
		exceeded_vals.append(sim.results['exceeded_proportion'])

		if i < 2:
			print("---------------")
			continue

		completed_avg = sum(completed_vals) / len(completed_vals)
		completed_S = sum([(v - completed_avg) ** 2 for v in completed_vals]) / (i - 1)
		completed_S = math.sqrt(completed_S)
		completed_hw = (z_val_two_tails * completed_S) / math.sqrt(i)
		print("runs: " + str(i) + " completed HW: " + str(completed_hw))
		print("---------------")


	wb = xs.Workbook('results/Results_' + settings['FileSizeGB'] + '_' + settings['TorrentThreshold'] + '_' + settings['HTTPDownThreshold'] \
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
import simpy
import configparser
import datetime
import xlsxwriter as xs
import math
import random
import scipy.stats
import sys
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

	print("Completed Target HW: " + str(completed_obj_hw))
	print("Exceeded Target HW: " + str(exceeded_obj_hw))

	completed_vals = []
	exceeded_vals = []
	done = False

	completed_avg = 0
	exceeded_avg = 0
	completed_hw = 0
	exceeded_hw = 0

	i = 0
	while not done:
		print("RUN: " + str(i + 1))
		env = simpy.Environment()
		sim = Simulation(env, settings, i == 0)
		sim.run()
		results.append(sim.results)
		i += 1

		if settings['RunOnce'] == 'yes':
			print("RUN ONCE")
			sys.exit()

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

		exceeded_avg = sum(exceeded_vals) / len(exceeded_vals)
		exceeded_S = math.sqrt(exceeded_avg * (1 - exceeded_avg))
		exceeded_hw = (z_val_two_tails * exceeded_S) / math.sqrt(i)
		print("runs: " + str(i) + " exceeded HW: " + str(exceeded_hw))

		print("completed_avg: " + str(completed_avg))
		print("exceeded_avg: " + str(exceeded_avg))

		if completed_hw < completed_obj_hw and exceeded_hw < exceeded_obj_hw:
			print("END ITERATIONS")
			done = True

		print("---------------")


	filename = 'results/Results_' + settings['FileSizeGB'] + '_' + settings['TorrentThreshold'] + '_' + settings['HTTPDownThreshold'] \
		+ '_' + settings['HTTPUp'] + '_'  + str(random.randint(0,10000)) + '.xlsx'

	print("Saving XLSX to: " + filename)
	wb = xs.Workbook(filename)

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
	ws.write(i, 1, exceeded_avg)
	ws.write(i, 2, completed_avg)
	i += 1
	ws.write(i, 0, 'half width')
	ws.write(i, 1, exceeded_hw)
	ws.write(i, 2, completed_hw)

	wb.close()

if __name__ == "__main__":
	main()
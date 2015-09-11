import matplotlib.pyplot as mp
import random, math, statistics

def main():
	rain_prob = 0.3
	rain_distribution = {"mu": 35, "sigma": 5}
	sunny_distribution = {"mu": 50, "sigma": 8}

	avg_earnings = []
	sigma_up = []
	sigma_down = []
	h_w = []

	r = range(20,100)
	it = 1000
	for x in r:
		earnings_arr = []
		for i in range(it):
			earnings_arr.append(canillita(rain_prob, x, rain_distribution, sunny_distribution))

		avg = sum(earnings_arr)/it
		sigma = statistics.pstdev(earnings_arr)
		h_w.append((2 * sigma)/math.sqrt(it))
		sigma_up.append(avg + h_w[-1])
		sigma_down.append(avg - h_w[-1])
		avg_earnings.append(avg)
		print(str(avg) + '\n')	

	best_avg = max(avg_earnings)
	best_index = avg_earnings.index(best_avg)
	print('Best:')
	print('Earnings: ' + str(best_avg))
	print('Qty: ' + str(best_index + min(r)))
	print('Half width: ' + str(h_w[best_index]))
	mp.plot(r, avg_earnings, r, sigma_down, r, sigma_up)
	mp.show()


def canillita(rain_prob, qty, rain_distribution, sunny_distribution):
	if random.random() < rain_prob:
		demand = random.normalvariate(rain_distribution["mu"], rain_distribution["sigma"])
	else:
		demand = random.normalvariate(sunny_distribution["mu"], sunny_distribution["sigma"])

	return earnings(round(demand, 0), qty)



def earnings(demand, qty):
	if qty < demand:
		return 0.6 * qty

	return (0.6 * demand) - (0.15 * (qty - demand))

if __name__ == '__main__':
	main()
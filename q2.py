import matplotlib.pyplot as mp
import random, math, statistics

def main():
	lambd = 0.04
	arrivals = init_arrivals(lambd)
	simulate(arrivals, 20, 4)
	
def simulate(arrivals, mu, sigma):
	events = [(arr, "arrival") for arr in arrivals]

	exits = [random.normalvariate(mu, sigma) + arrivals[0]]
	for arrival in arrivals[1:]:
		exits.append(exits[-1] + random.normalvariate(mu, sigma) + arrival)

	events.extend([(ex, "exit") for ex in exits])
	events.sort(key=lambda tup: tup[0])

	queue_count = 0

	for ev in events:
		if ev[1] == "arrival":
			queue_count += 1
			print("llego uno: " + str(queue_count) + " time: " + str(ev[0]))
		else:
			queue_count -= 1
			print("se fue uno: " + str(queue_count) + " time: " + str(ev[0]))


def init_arrivals(lambd):
	arrivals = []
	accum = 0
	while accum <= (8 * 60):
		current = random.expovariate(lambd)
		accum += current
		arrivals.append(accum)
	
	if arrivals[-1] > (8 * 60):
		arrivals.pop()

	return arrivals

if __name__ == '__main__':
	main()
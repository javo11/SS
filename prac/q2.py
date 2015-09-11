import random, math, statistics
import os, time

def main():
	lambd = 0.1
	arrivals = init_arrivals(lambd)
	simulate(arrivals, 20, 4)

def simulate(arrivals, mu, sigma):
	events = [(arr, "arrival") for arr in arrivals]

	exits = [random.normalvariate(mu, sigma) + arrivals[0]]
	for arrival in arrivals[1:]:
		exits.append(max(exits[-1], arrival) + random.normalvariate(mu, sigma))

	events.extend([(ex, "exit") for ex in exits])
	events.sort(key=lambda tup: tup[0])

	queue_count = 0
	queue_sizes = []

	for ev in events[1:]:
		os.system('clear')
		if ev[1] == "arrival":
			queue_count += 1
			print('O' * queue_count)
			time.sleep(0.5)
			#print("llego uno: " + str(queue_count) + " time: " + str(ev[0]))
		else:
			queue_count = queue_count - 1 if queue_count > 0 else 0
			print('O' * queue_count)
			time.sleep(0.5)
			#print("se fue uno: " + str(queue_count) + " time: " + str(ev[0]))

		if ev[0] < (8 * 60):
			queue_sizes.append(queue_count)

	if events[-1][0] > (8 * 60):
		print("overtime was: " + str(events[-1][0] - (8*60)))

	print("avg queue len: " + str(sum(queue_sizes) / len(queue_sizes)))


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
import matplotlib.pyplot as mp
import random, math, statistics

def main():
	lambd = 0.04
	arrivals = init_arrivals(lambd)
	simulate(arrivals, 20, 4)
	
def simulate(arrivals, mu, sigma):
	exits = []
	q_i = 0
	q_count = 0
	for j, arrival in enumerate(arrivals):
		q_count+=1
		print("Llego un gato, hay " + str(q_count) + " eperando (min "+ str(arrival) +")")
		t = arrival

		next_arrival = arrivals[j + 1]
		while q_count > 0 and (j == len(arrivals) - 1 or exits[q_i] < next_arrival):
			attention_time = random.normalvariate(mu, sigma)
			t += attention_time
			exits.append(t)
			q_count -= 1
			index += 1
			print("\tSe fue un gato, quedan " + str(q_count) + " eperando)")

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
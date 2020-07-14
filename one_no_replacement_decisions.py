from numpy.random import randint
from copy import deepcopy
import argparse

parser = argparse.ArgumentParser(description="simulate drawing rewards without replacement")
parser.add_argument('--outfile',
			help="name of file to write output to; defaults to stdio",
			default=None)
parser.add_argument('--trials', type=int,
			help="number of trials to simulate; default 10",
            default=10)

args = parser.parse_args()

starting_bag = [0]+[1]

outarray = []

for _ in range(args.trials):
	bag = deepcopy(starting_bag)
	log = []
	for _ in range(2):
		if randint(2) is 1:
			reward = randint(len(bag))
			log.append(1)
			log.append(bag.pop(reward))
		else:
			log.append(0)
			log.append(0)
	reward = sum(log[1::2])*6 - sum(log[::2])
	log.append(reward)
	if args.outfile:
		outarray.append(log)

	else:
		print(log)


import csv

with open(args.outfile, 'w') as myfile:
	wr = csv.writer(myfile,delimiter='\t')
	for log in outarray:
			wr.writerow(log)

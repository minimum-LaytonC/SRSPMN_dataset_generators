import numpy as np
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

starting_bag = 2*[0]+[1]
draws = 3
from functools import reduce
outarray = [["Idnum"]+reduce(lambda x,y: x+y, [["draw"+str(i),"result"+str(i)] for i in range(1,draws+1)])+["reward"]]


for i in range(args.trials):
	bag1 = deepcopy(starting_bag)
	bag2 = deepcopy(starting_bag)
	log = [i+1]
	for _ in range(draws):
		action = randint(3)
		if action is 1:
			marble = randint(len(bag1))
			log.append(1)
			log.append(bag1.pop(marble))
		elif action is 2:
			marble = randint(len(bag2))
			log.append(2)
			log.append(bag2.pop(marble))
		else:
			log.append(0)
			log.append(0)
	reward = sum(log[2::2])*6 - np.count_nonzero(log[1::2])
	log.append(reward)
	if args.outfile:
		outarray.append(log)
	else:
		print(log)


if args.outfile:
	import csv
	with open(args.outfile, 'w') as myfile:
		wr = csv.writer(myfile,delimiter='\t')
		for log in outarray:
				wr.writerow(log)

# optimal policy:
#	draw from one bag until you draw the target,
#	then draw from the other bag,
#	then if you've drawn both targets, don't draw.
# best case is you draw both first try, then don't draw, which gives +10 total utility.
# expected utility given optimal policy:
aa = 10 * (1/3 * 1/3)		# draw target1, draw target 2
aba = 9 * (1/3 * 2/3 * 1/2) # draw target1, miss, draw target 2
abb = 3 * (1/3 * 2/3 * 1/2) # draw target1, miss, miss
baa = 9 * (2/3 * 1/2 * 1/3) # miss, draw target1, draw target 2
bab = 3 * (2/3 * 1/2 * 2/3) # miss, draw target1, miss
bba = 3 * (2/3 * 1/2)		# miss, miss, draw target1
meu = aa+aba+abb+baa+bab+bba
# meu is 5.11111111111
total_prob = (1/3 * 1/3)+(1/3 * 2/3 * 1/2)+(1/3 * 2/3 * 1/2)+(2/3 * 1/2 * 1/3)+(2/3 * 1/2 * 2/3)+(2/3 * 1/2)
# total_prob is 1

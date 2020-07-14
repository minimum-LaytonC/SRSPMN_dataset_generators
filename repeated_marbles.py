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
parser.add_argument('--steps', type=int,
			help="number of decision steps to simulate for each trial; default 10",
            default=10)

args = parser.parse_args()

starting_bag = [0, 1]

from functools import reduce
outarray = [["Idnum"]+reduce(lambda x,y: x+y, [["draw"+str(i),"result"+str(i),"reward"+str(i)] for i in range(1,args.steps+1)])]
if args.outfile is None:
	print(outarray[0])

for i in range(1, args.trials+1):
    bag = deepcopy(starting_bag)
    log = [i]
    for _ in range(args.steps):
        if randint(2) is 1:
            got_target = bag.pop(randint(len(bag)))
            log.append(1) # did draw
            log.append(got_target) # whether we drew target
            reward = 1 if got_target else -1
            log.append(reward) # reward based on drawing target
            if len(bag) < 1:
                bag = deepcopy(starting_bag)
        else:
            log.append(0) # no draw
            log.append(0) # didn't get target
            log.append(0) # 0 reward
            bag = deepcopy(starting_bag)

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

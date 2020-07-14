import numpy as np
from numpy.random import randint
from copy import deepcopy
import argparse

parser = argparse.ArgumentParser(description="simulate the tiger problem")
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

from functools import reduce
out_array = [["Idnum"]+reduce(lambda x,y: x+y, [["action"+str(i),"observation"+str(i),"reward"+str(i)] for i in range(1,args.steps+1)])]


for i in range(1, args.trials+1):
    tiger_side = randint(1,3) # 1 is left, 2 is right.
    if args.outfile:
        log = [i]
    else:
        print("\ngame: "+str(i))
        print("[t,action,observation,utility]:")
    observation = 0
    for t in range(args.steps):
        # 0 is listen, 1 is open left, 2 is open right
        # 2/3 of the time listens, 1/3 of the time chooses random door
        action = 0 if randint(5)<4 else randint(1,3)
        utility = -1
        if action != 0:
            utility = -100 if tiger_side==action else 10
            tiger_side = randint(1,3) # on opening door, reset tiger location
        if args.outfile:
            log += [observation,action,utility]
        else:
            print([t,observation,action,utility])
        if action == 0:
            if randint(1,101) <= 85: # 85% accuracy of observation
                observation = tiger_side
            else:
                observation = 2 if tiger_side==1 else 1
        else:
            observation = 0
    if args.outfile:
        out_array.append(log)


if args.outfile:
    import csv
    with open(args.outfile, 'w') as myfile:
    	wr = csv.writer(myfile,delimiter='\t')
    	for log in out_array:
    			wr.writerow(log)

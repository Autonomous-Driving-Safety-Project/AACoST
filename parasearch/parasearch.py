from scenario import ScenarioFalsification, ScenarioTest
import numpy as np
from optimizer import Optimizer
from logger import Logger
import os
import time

DISPLAY = False
RECORD = True
OSC_NUM = 5
LEARNINGRATE = 0.5
SAMPLE_NUM = 16
MAX_EPOCH = 1000



if __name__ == '__main__':
    seeds = range(10, 51, 10)
    result = []
    # for random_seed in seeds:
    time_start = time.time()
    logger = Logger(['v', 'loss'])
    cpu_count = 1

    def fn(v):
        min_gap, r, s, b, t = scenario.run(v)
        if min_gap is not None:
            return min_gap, t
        else:
            return float('inf'), t

    for run in range(0, OSC_NUM):
        total_time = 0
        random_seed = seeds[run]
        np.random.seed(random_seed)
        retry = 100
        while retry > 0:
            retry -= 1
            n = np.random.randint(1, 1001)
            scenario = ScenarioFalsification('../output/'+ str(n) +'.xosc')
            scenario_ego = ScenarioTest('../output/'+ str(n) +'-ego.xosc')
            opt = Optimizer(fn, scenario.mins, scenario.maxs, LEARNINGRATE, SAMPLE_NUM, MAX_EPOCH, None, cpu_count)
            # Stage 1
            stg1_cnt = 10
            while stg1_cnt > 0:
                stg1_cnt -= 1
                v, opt_time = opt.run()
                total_time += opt_time
                min_gap, r, s, b, t = scenario.run(v)
                print('min_gap: {}, Rear: {}, Side: {}, Blamed: {}'.format(min_gap, r, s, b))
                # if min_gap == 0 and b:
                if min_gap == 0:
                    break
            if stg1_cnt == 0:
                break
            print(total_time)
            print('time cost: {}'.format(time.time() - time_start))
            print(v)
            # scenario.dump(v, 'result/'+ str(n) +'.xosc')
            min_gap, r, s, b, t = scenario.run(v, DISPLAY, RECORD)
            print('min_gap: {}, Rear: {}, Side: {}, Blamed: {}'.format(min_gap, r, s, b))
            # logger.dump()

            # input('Press Enter to continue...')
            if RECORD:
                os.replace('simulation.dat', 'record-falsification-{}-{}.dat'.format(n, random_seed))

            # Stage 2
            scenario_ego.set_hold_parameters(v)

            epoch = 500
            while epoch > 0:
                u = np.random.uniform(scenario_ego.mins, scenario_ego.maxs)
                min_gap = scenario_ego.run(u)
                # print('min_gap: {}'.format(min_gap))
                if min_gap is not None and min_gap > 0:
                    print(u)
                    break
                if min_gap is None:
                    break # goto Stage 1
                epoch -= 1
            if min_gap is None:
                print('Rival car collision, rewind to Stage 1.')
                continue # goto Stage 1
            elif epoch != 0:
                break
        # scenario_ego.dump(u, 'result/'+ str(n) +'-ego.xosc')
        scenario_ego.run(u, DISPLAY, RECORD)
        if RECORD and retry > 0:
            os.replace('simulation.dat', 'record-answer-{}-{}.dat'.format(n, random_seed))
        result.append((random_seed, total_time))
    #end for
    print(result)

import gym
import gym_lass
import numpy as np
import random
import os

SEED=range(10, 51, 10)
env = gym.make('HighwayFourCars-env2-v2', display=False, record=True)
for seed in SEED:
    random.seed(seed)
    np.random.seed(seed)
    env.action_space.seed(seed)
    env.observation_space.seed(seed)
    action_space = env.action_space
    high = action_space.high
    low = action_space.low

    time = 0
    for i in range(5000):
        env.reset()
        for j in range(1000):
            acc = np.random.rand(1)
            if acc < 3/11: # keep expectation of acc = 0
                ax = np.random.uniform(low=[-0.8,-0.8,-0.8], high=[0,0,0])
            else:
                ax = np.random.uniform(low=[0,0,0], high=[0.3,0.3,0.3])
            ay = np.random.uniform(low=[-1,-1,-1], high=[1,1,1])
            a = np.array([[ax[i], ay[i]] for i in range(3)]).ravel()
            s, r, d, info = env.step(a)
            if d:
                break
        # print(info['t'])
        time += info['t']
        # print(time)
        if r >= 0:
            print(seed, time)
            os.replace('simulation.dat', 'record-env2-s{}.dat'.format(seed))
            break